from langgraph.graph import StateGraph, END
from typing import TypedDict, List
from pymongo import MongoClient
from rag import RAGSystem
import google.generativeai as genai
import os
import logging
from langchain.memory import MongoDBChatMessageHistory

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY", "AIzaSyA6G0a178pQgJ_rkGxKWz-gXieGOeMNteA"))
chat_model = genai.GenerativeModel('gemini-1.5-flash')

class State(TypedDict):
    username: str
    message: str
    response: str
    user_data: dict
    laptops: List[dict]
    awaiting_laptop_selection: bool
    last_query: str
    chat_history: List[dict]

class TicketingChatbot:
    def __init__(self):
        try:
            self.client = MongoClient("localhost", 27017)
            self.db = self.client["Ticketing_Platform"]
            self.customers_collection = self.db["Customers"]
            self.tickets_collection = self.db["tickets"]
            self.rag = RAGSystem()
            self.graph = self._build_graph()
            logger.info("TicketingChatbot initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize TicketingChatbot: {e}")
            raise

    def _build_graph(self):
        workflow = StateGraph(State)
        workflow.add_node("fetch_user", self._fetch_user_data)
        workflow.add_node("process_greeting", self._process_greeting)
        workflow.add_node("process_query", self._process_query)
        workflow.add_node("handle_laptop_selection", self._handle_laptop_selection)

        workflow.set_entry_point("fetch_user")
        workflow.add_edge("fetch_user", "process_greeting")
        workflow.add_conditional_edges(
            "process_greeting",
            self._route_message,
            {
                "greeting": END,
                "query": "process_query",
                "selection": "handle_laptop_selection",
                "END": END
            }
        )
        workflow.add_edge("process_query", END)
        workflow.add_edge("handle_laptop_selection", END)
        return workflow.compile()

    def _fetch_user_data(self, state: State) -> State:
        try:
            logger.info(f"Fetching user data for {state['username']}")
            user = self.customers_collection.find_one({"username": state["username"]})
            state["user_data"] = user or {}
            state["laptops"] = user.get("laptops", []) if user else []
            state["awaiting_laptop_selection"] = state.get("awaiting_laptop_selection", False)
            state["last_query"] = state.get("last_query", "")
            # Fetch chat history
            history = MongoDBChatMessageHistory(
                connection_string="mongodb://localhost:27017",
                database_name="Ticketing_Platform",
                collection_name="chat_history",
                session_id=state["username"]
            )
            state["chat_history"] = [{"role": msg.type, "content": msg.content} for msg in history.messages[-10:]]
            logger.info(f"User data and history fetched for {state['username']}")
            return state
        except Exception as e:
            logger.error(f"Error fetching user data for {state['username']}: {e}")
            state["response"] = "Error fetching user data. Please try again."
            return state

    def _process_greeting(self, state: State) -> State:
        try:
            message = state["message"].lower().strip()
            logger.info(f"Processing greeting: {message}")
            greetings = ["hi", "hello", "good morning", "hey"]
            if any(g in message for g in greetings):
                state["response"] = "Welcome to the AI Ticketing Platform! How can I help you today?"
            elif "what can you do" in message or "features" in message:
                state["response"] = (
                    "I can assist you with:<br>"
                    "- Troubleshooting laptop issues<br>"
                    "- Retrieving information about your registered laptops<br>"
                    "- Providing solutions from our knowledge base<br>"
                    "Just tell me about your issue, e.g., 'My laptop is not working'!"
                )
            else:
                state["response"] = "I'm here to help with your laptop issues. Please describe your problem or ask about our features."
            state["awaiting_laptop_selection"] = False
            return state
        except Exception as e:
            logger.error(f"Error processing greeting: {e}")
            state["response"] = "Error processing your message. Please try again."
            return state

    def _process_query(self, state: State) -> State:
        try:
            message = state["message"].lower().strip()
            laptops = state["laptops"]
            logger.info(f"Processing query: {message}, laptops: {len(laptops)}")

            # Validate laptops
            valid_laptops = [
                laptop for laptop in laptops
                if isinstance(laptop, dict) and "name" in laptop and "model" in laptop
                and isinstance(laptop.get("name"), str) and isinstance(laptop.get("model"), str)
            ]
            laptop_names = [laptop["name"].lower() for laptop in valid_laptops]
            laptop_models = [f"{laptop['name']} {laptop['model']}".lower() for laptop in valid_laptops]

            # Available brands
            available_brands = ["Apple", "HP", "Dell", "Lenovo", "Asus", "Acer", "Microsoft", "Samsung", "MSI"]
            mentioned_brand = None
            for brand in available_brands:
                if brand.lower() in message:
                    mentioned_brand = brand.lower()
                    break

            if message.startswith("list my") and ("laptop" in message or "device" in message):
                if valid_laptops:
                    laptop_list = sorted(set(f"{laptop['name']} ({laptop['model']})" for laptop in valid_laptops))
                    state["response"] = (
                        f"Your registered laptops:<br><ul>" +
                        "".join(f"<li>{laptop}</li>" for laptop in laptop_list) +
                        "</ul>Please specify a laptop or describe an issue."
                    )
                    state["awaiting_laptop_selection"] = True
                    state["last_query"] = ""
                else:
                    state["response"] = "You don't have any laptops registered. Please provide a laptop model and issue."
            elif "list" in message and mentioned_brand:
                state["response"] = (
                    f"Available laptop brands in the market:<br><ul>" +
                    "".join(f"<li>{brand}</li>" for brand in available_brands) +
                    "</ul>Please specify a brand or describe an issue."
                )
                state["awaiting_laptop_selection"] = False
                state["last_query"] = ""
            elif mentioned_brand or any(name in message for name in laptop_names):
                # Specific query
                result = self.rag.retrieve_answers(message, state["chat_history"])
                state["response"] = result["formatted_response"]
                state["awaiting_laptop_selection"] = False
                state["last_query"] = message
            elif "laptop" in message:
                # General query
                if valid_laptops:
                    laptop_list = sorted(set(f"{laptop['name']} ({laptop['model']})" for laptop in valid_laptops))
                    state["response"] = (
                        f"Your registered laptops:<br><ul>" +
                        "".join(f"<li>{laptop}</li>" for laptop in laptop_list) +
                        "</ul>Please specify which laptop, e.g., 'HP Pavilion x360'."
                    )
                    state["awaiting_laptop_selection"] = True
                    state["last_query"] = message
                else:
                    state["response"] = "No laptops registered. Please provide a laptop model and issue."
            else:
                state["response"] = "Please clarify if you're referring to a laptop issue, or ask about our features!"
            
            logger.info(f"Query response: {state['response']}, awaiting_selection: {state['awaiting_laptop_selection']}")
            return state
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            state["response"] = "Error processing your query. Please try again."
            return state

    def _handle_laptop_selection(self, state: State) -> State:
        try:
            message = state["message"].lower().strip()
            laptops = state["laptops"]
            logger.info(f"Handling laptop selection: {message}, last_query: {state['last_query']}")

            # Validate laptops
            valid_laptops = [
                laptop for laptop in laptops
                if isinstance(laptop, dict) and "name" in laptop and "model" in laptop
                and isinstance(laptop["name"], str) and isinstance(laptop["model"], str)
            ]
            laptop_models = [ f"{laptop['name']} {laptop['model']}".lower() for laptop in valid_laptops]
            
            # Check for selection
            selected_laptop = None
            for model in laptop_models:
                if model in message or message in model or message in ["yes that", "that one", "yes"]:
                    selected_laptop = model
                    break
            
            if selected_laptop:
                query = f"{state['last_query']} {selected_laptop}" if state["last_query"] else message
                logger.info(f"Reconstructed query: {query}")
                result = self.rag.retrieve_answers(query, state["chat_history"])
                state["response"] = result["formatted_response"]
                state["awaiting_laptop_selection"] = False
                state["last_query"] = query
            else:
                laptop_list = sorted(set(f"{laptop['name']} ({laptop['model']})" for laptop in valid_laptops))
                state["response"] = (
                    f"Invalid selection. Choose from your laptops:<br><ul>" +
                    "".join(f"<li>{laptop}</li>" for laptop in laptop_list) +
                    "</ul>"
                )
                state["awaiting_laptop_selection"] = True
            
            logger.info(f"Laptop selection response: {state['response']}, awaiting_selection: {state['awaiting_laptop_selection']}")
            return state
        except Exception as e:
            logger.error(f"Error handling laptop selection: {e}")
            state["response"] = "Error processing laptop selection. Please try again."
            return state

    def _route_message(self, state: State) -> str:
        try:
            message = state["message"].lower().strip()
            logger.info(f"Routing message: {message}, awaiting_selection: {state['awaiting_laptop_selection']}")
            if state["awaiting_laptop_selection"]:
                return "selection"
            greetings = ["hi", "hello", "good morning", "hey"]
            if any(g in message for g in greetings) or "what can you do" in message or "features" in message:
                return "greeting"
            if "laptop" in message or "macbook" in message or "hp" in message or "dell" in message or state["last_query"]:
                return "query"
            return "END"
        except Exception as e:
            logger.error(f"Error routing message: {e}")
            return "END"

    def handle_message(self, username: str, message: str) -> str:
        try:
            logger.info(f"Handling message for {username}: {message}")
            state = {
                "username": username,
                "message": message,
                "response": "",
                "user_data": {},
                "laptops": [],
                "awaiting_laptop_selection": False,
                "last_query": "",
                "chat_history": []
            }
            result = self.graph.invoke(state, config={"recursion_limit": 5000})
            response = result["response"] or "No response generated. Please try again."
            
            # Save to chat history
            history = MongoDBChatMessageHistory(
                connection_string="mongodb://localhost:27017",
                database_name="Ticketing_Platform",
                collection_name="chat_history",
                session_id=username
            )
            history.add_user_message(message)
            history.add_ai_message(response)
            
            logger.info(f"Final response for {username}: {response}")
            logger.debug(f"Final state: {result}")
            return response
        except Exception as e:
            logger.error(f"Error in handle_message: {e}")
            return "An error occurred while processing your message. Please try again."