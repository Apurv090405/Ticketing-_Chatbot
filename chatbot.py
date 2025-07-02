from langgraph.graph import StateGraph, END
from typing import TypedDict, List
from pymongo import MongoClient
from rag import RAGSystem
import google.generativeai as genai
import os
import logging
from langchain_mongodb import MongoDBChatMessageHistory

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))
chat_model = genai.GenerativeModel('gemini-2.5-flash-lite-preview-06-17')

class State(TypedDict):
    username: str
    message: str
    response: str
    user_data: dict
    laptops: List[dict]
    awaiting_laptop_selection: bool
    last_query: str
    chat_history: List[dict]
    intent: str

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
        workflow.add_node("classify_intent", self._classify_intent)
        workflow.add_node("process_greeting", self._process_greeting)
        workflow.add_node("process_query", self._process_query)
        workflow.add_node("handle_laptop_selection", self._handle_laptop_selection)
        workflow.add_node("list_devices", self._list_devices)
        workflow.add_node("show_chat_history", self._show_chat_history)
        workflow.add_node("handle_identity", self._handle_identity)

        workflow.set_entry_point("fetch_user")
        workflow.add_edge("fetch_user", "classify_intent")
        workflow.add_conditional_edges(
            "classify_intent",
            lambda state: state.get("intent", "unknown"),
            {
                "greeting": "process_greeting",
                "query": "process_query",
                "list_devices": "list_devices",
                "selection": "handle_laptop_selection",
                "chat_history": "show_chat_history",
                "identity": "handle_identity",
                "unknown": "process_query"
            }
        )
        workflow.add_edge("process_greeting", END)
        workflow.add_edge("process_query", END)
        workflow.add_edge("handle_laptop_selection", END)
        workflow.add_edge("list_devices", END)
        workflow.add_edge("show_chat_history", END)
        workflow.add_edge("handle_identity", END)
        return workflow.compile()

    def _classify_intent(self, state: State) -> State:
        try:
            message = state["message"].lower().strip()
            logger.info(f"Classifying intent for message: {message}")
            prompt = (
                f"""You are an AI assistant for a laptop support platform.
                Given the user message: '{message}'
                Classify the intent into one of:
                - greeting: greetings like "hi", "hello", "hii", "bye", or asking about capabilities
                - query: questions about laptop issues or troubleshooting
                - list_devices: requests to list or show registered devices (e.g., "list my devices", "how many machines", "my device list is")
                - selection: selecting a device from a list (e.g., "HP Pavilion", "yes that")
                - chat_history: requests to see past conversation (e.g., "past conversation", "chat history", "past chat")
                - identity: questions about the chatbot's or user's identity (e.g., "my name is", "you are llm model of", "why you are")
                - unknown: anything unrelated to laptops (e.g., "cow", "car", "gift for my baby boy")
                Return only the intent name.
                Examples:
                - "hi" -> greeting
                - "hii" -> greeting
                - "bye" -> greeting
                - "my dell laptop screen is flickering" -> query
                - "list my devices" -> list_devices
                - "can you know how many machines was there" -> list_devices
                - "my device list is" -> list_devices
                - "select HP Pavilion" -> selection
                - "can you send the past chat" -> chat_history
                - "in previous we talk about which laptop" -> chat_history
                - "my cow was not working" -> unknown
                - "suggest a gift for my baby boy" -> unknown
                - "my car was not working" -> unknown
                - "my name is" -> identity
                - "why you are" -> identity
                - "you are llm model of" -> identity
                """
            )
            response = chat_model.generate_content(prompt)
            state["intent"] = response.text.strip()
            logger.info(f"Intent classified as: {state['intent']}")
            return state
        except Exception as e:
            logger.error(f"Error classifying intent: {e}")
            state["intent"] = "unknown"
            return state

    def _fetch_user_data(self, state: State) -> State:
        try:
            logger.info(f"Fetching user data for {state['username']}")
            user = self.customers_collection.find_one({"username": state["username"]})
            state["user_data"] = user or {}
            state["laptops"] = user.get("laptops", []) if user else []
            state["awaiting_laptop_selection"] = state.get("awaiting_laptop_selection", False)
            state["last_query"] = state.get("last_query", "")
            state["intent"] = state.get("intent", "unknown")
            try:
                history = MongoDBChatMessageHistory(
                    connection_string="mongodb://localhost:27017",
                    database_name="Ticketing_Platform",
                    collection_name="chat_history",
                    session_id=state["username"]
                )
                state["chat_history"] = [{"role": msg.type, "content": msg.content} for msg in history.messages[-10:]]
            except Exception as e:
                logger.warning(f"Failed to load chat history for {state['username']}: {e}")
                state["chat_history"] = []
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
            prompt = (
                f"""You are a friendly AI assistant here to support users with laptop-related issues on an AI ticketing platform.
                ---
                User input: '{state['message']}'
                ---
                Your task is to respond appropriately to the user's message.
                If the user sends a greeting like "hi", "hello", "hii", etc.:
                - Greet them in a natural, friendly way.
                - Ask how you can assist them today.
                If the input is a farewell like "bye":
                - Respond with a polite farewell and encourage returning for help.
                If the input asks about capabilities or features:
                - Briefly mention that you can help with laptop issues, device listing, or troubleshooting.
                - Encourage the user to describe their issue or list devices.
                ---
                Guidelines:
                - Keep the tone conversational, friendly, and concise (1–2 lines, max 20 words per line).
                - Vary phrasing to avoid repetition across responses.
                - Use clear, casual language that invites engagement.
                """
            )
            response = chat_model.generate_content(prompt)
            state["response"] = response.text.strip() if hasattr(response, "text") else str(response)
            state["awaiting_laptop_selection"] = False
            return state
        except Exception as e:
            logger.error(f"Error processing greeting: {e}")
            state["response"] = "Error processing your message. Please try again."
            return state

    def _list_devices(self, state: State) -> State:
        try:
            laptops = state["laptops"]
            logger.info(f"Listing devices for user: {state['username']}")
            valid_laptops = [
                laptop for laptop in laptops
                if isinstance(laptop, dict) and "name" in laptop and "model" in laptop
                and isinstance(laptop.get("name"), str) and isinstance(laptop.get("model"), str)
            ]
            if valid_laptops:
                laptop_list = sorted(set(f"{laptop['name']} ({laptop['model']})" for laptop in valid_laptops))
                state["response"] = (
                    f"Your registered devices:<br><ul>" +
                    "".join(f"<li>{laptop}</li>" for laptop in laptop_list) +
                    "</ul>Please select a device or describe an issue."
                )
                state["awaiting_laptop_selection"] = True
                state["last_query"] = ""
            else:
                prompt = (
                    """You are a friendly AI assistant on an AI ticketing platform that supports users with laptop-related issues.
                    ---
                    Your task is to inform users that no devices are registered and suggest visiting the registration page.
                    Respond warmly in 1–2 lines, each under 20 words.
                    ---
                    Use simple, clear language without jargon.
                    Vary phrasing for a fresh, engaging response.
                    """
                )
                response = chat_model.generate_content(prompt)
                state["response"] = response.text.strip() if hasattr(response, "text") else str(response)
                state["awaiting_laptop_selection"] = True
                state["last_query"] = ""
            return state
        except Exception as e:
            logger.error(f"Error listing devices: {e}")
            state["response"] = "Error listing your devices. Please try again."
            return state

    def _process_query(self, state: State) -> State:
        try:
            message = state["message"].lower().strip()
            laptops = state["laptops"]
            logger.info(f"Processing query: {message}, laptops: {len(laptops)}")

            valid_laptops = [
                laptop for laptop in laptops
                if isinstance(laptop, dict) and "name" in laptop and "model" in laptop
                and isinstance(laptop.get("name"), str) and isinstance(laptop.get("model"), str)
            ]
            laptop_names = [laptop["name"].lower() for laptop in valid_laptops]
            laptop_models = [f"{laptop['name']} {laptop['model']}".lower() for laptop in valid_laptops]

            available_brands = ["Apple", "HP", "Dell", "Lenovo", "Asus", "Acer", "Microsoft", "Samsung", "MSI"]
            mentioned_brand = next((brand.lower() for brand in available_brands if brand.lower() in message), None)

            # Check for irrelevant topics
            irrelevant_keywords = ["cow", "car", "weather", "milk", "animal", "vehicle", "gift", "baby", "child"]
            is_irrelevant = any(keyword in message for keyword in irrelevant_keywords)

            if is_irrelevant:
                state["response"] = "Sorry, I focus on laptop issues. How can I assist with your device?"
                state["awaiting_laptop_selection"] = False
                state["last_query"] = ""
            elif mentioned_brand or any(name in message for name in laptop_names) or any(model in message for model in laptop_models):
                result = self.rag.retrieve_answers(message, state["chat_history"])
                state["response"] = result["formatted_response"]
                state["awaiting_laptop_selection"] = False
                state["last_query"] = message
            elif "laptop" in message or any(brand.lower() in message for brand in available_brands):
                if valid_laptops:
                    laptop_list = sorted(set(f"{laptop['name']} ({laptop['model']})" for laptop in valid_laptops))
                    state["response"] = (
                        f"Your registered devices:<br><ul>" +
                        "".join(f"<li>{laptop}</li>" for laptop in laptop_list) +
                        "</ul>Please specify a device, e.g., 'HP Pavilion x360', or describe an issue."
                    )
                    state["awaiting_laptop_selection"] = True
                    state["last_query"] = message
                else:
                    prompt = (
                        """You are a friendly AI assistant for an AI ticketing platform focused on supporting laptop-related issues.
                        ---
                        Your task is to let users know that no devices are registered and suggest visiting the registration page.
                        Respond in a warm, natural tone using 1–2 lines, each under 20 words.
                        ---
                        Vary phrasing to keep responses fresh and engaging.
                        Use simple, clear language without jargon.
                        """
                    )
                    response = chat_model.generate_content(prompt)
                    state["response"] = response.text.strip() if hasattr(response, "text") else str(response)
                    state["awaiting_laptop_selection"] = True
                    state["last_query"] = ""
            else:
                prompt = (
                    """You are a friendly AI assistant for an AI ticketing platform that supports users with laptop-related issues.
                    ---
                    Your task is to ask users for more details about their request, encouraging them to specify the device or issue.
                    Respond in a warm, natural tone using 1–2 lines, each under 20 words.
                    ---
                    Vary phrasing to keep responses conversational and engaging.
                    Avoid jargon and ensure clarity.
                    """
                )
                response = chat_model.generate_content(prompt)
                state["response"] = response.text.strip() if hasattr(response, "text") else str(response)
                state["awaiting_laptop_selection"] = False
                state["last_query"] = ""

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

            valid_laptops = [
                laptop for laptop in laptops
                if isinstance(laptop, dict) and "name" in laptop and "model" in laptop
                and isinstance(laptop["name"], str) and isinstance(laptop["model"], str)
            ]
            laptop_models = [f"{laptop['name']} {laptop['model']}".lower() for laptop in valid_laptops]
            
            selected_laptop = next((model for model in laptop_models if model in message or message in model or message in ["yes that", "that one", "yes"]), None)
            
            if selected_laptop:
                query = f"{state['last_query']} {selected_laptop}" if state['last_query'] else message
                logger.info(f"Reconstructed query: {query}")
                result = self.rag.retrieve_answers(query, state["chat_history"])
                state["response"] = result["formatted_response"]
                state["awaiting_laptop_selection"] = False
                state["last_query"] = query
            else:
                laptop_list = sorted(set(f"{laptop['name']} ({laptop['model']})" for laptop in valid_laptops))
                state["response"] = (
                    f"Invalid selection. Please choose from your devices:<br><ul>" +
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

    def _show_chat_history(self, state: State) -> State:
        try:
            logger.info(f"Showing chat history for user: {state['username']}")
            chat_history = state["chat_history"][-10:]  # Limit to last 10 messages
            if chat_history:
                history_html = "<div>Recent conversation:<br><ul>"
                for msg in chat_history:
                    role = "You" if msg["role"] == "user" else "Assistant"
                    # Summarize long responses (e.g., ticket data)
                    content = msg["content"]
                    if len(content) > 100 and "Found similar issues" in content:
                        content = "Provided solutions for a laptop issue."
                    history_html += f"<li><strong>{role}:</strong> {content[:100]}</li>"
                history_html += "</ul></div>"
                state["response"] = history_html
            else:
                state["response"] = "No recent conversation found. How can I assist with your laptop today?"
            state["awaiting_laptop_selection"] = False
            state["last_query"] = ""
            logger.info(f"Chat history response: {state['response']}")
            return state
        except Exception as e:
            logger.error(f"Error showing chat history: {e}")
            state["response"] = "Error retrieving chat history. Please try again."
            return state

    def _handle_identity(self, state: State) -> State:
        try:
            logger.info(f"Handling identity query for user: {state['username']}")
            prompt = (
                """You are a friendly AI assistant for an AI ticketing platform focused on laptop support.
                ---
                Your task is to respond to queries about the chatbot's or user's identity.
                Explain you are an AI for laptop support and redirect to a laptop-related task.
                Respond in 1–2 lines, each under 20 words.
                ---
                Vary phrasing to keep responses fresh and conversational.
                Use simple, clear language without jargon.
                """
            )
            response = chat_model.generate_content(prompt)
            state["response"] = response.text.strip() if hasattr(response, "text") else str(response)
            state["awaiting_laptop_selection"] = False
            state["last_query"] = ""
            logger.info(f"Identity response: {state['response']}")
            return state
        except Exception as e:
            logger.error(f"Error handling identity query: {e}")
            state["response"] = "I'm an AI for laptop support. How can I help with your device?"
            return state

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
                "chat_history": [],
                "intent": "unknown"
            }
            result = self.graph.invoke(state, config={"recursion_limit": 50})
            response = result["response"] or "No response generated. Please try again."
            
            try:
                history = MongoDBChatMessageHistory(
                    connection_string="mongodb://localhost:27017",
                    database_name="Ticketing_Platform",
                    collection_name="chat_history",
                    session_id=username
                )
                history.add_user_message(message)
                history.add_ai_message(response)
            except Exception as e:
                logger.warning(f"Failed to save chat history for {username}: {e}")

            logger.info(f"Final response for {username}: {response}")
            logger.debug(f"Final state: {result}")
            return response
        except Exception as e:
            logger.error(f"Error in handle_message: {e}")
            return "An error occurred while processing your message. Please try again."