from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
import google.generativeai as genai
from db import db
from dotenv import load_dotenv
import os
import json
import requests
import uuid

load_dotenv()

class RAGPipeline:
    def __init__(self):
        try:
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=os.getenv("GEMINI_API_KEY")
            )
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            self.gemini_model = genai.GenerativeModel("gemini-1.5-flash")
            self.vector_store = self._initialize_vector_store()
        except Exception as e:
            raise Exception(f"Failed to initialize RAG pipeline: {e}")

    def _initialize_vector_store(self):
        try:
            tickets = db.get_tickets()
            if not tickets:
                print("Vector store not initialized: No tickets available.")
                return None
            documents = [
                Document(
                    page_content=ticket["query"] + " " + " ".join(ticket["answers"]),
                    metadata={
                        "ticket_id": ticket["ticket_id"],
                        "query": ticket["query"],
                        "answers": ticket["answers"]
                    }
                )
                for ticket in tickets
            ]
            return FAISS.from_documents(documents, self.embeddings)
        except Exception as e:
            print(f"Error initializing vector store: {e}")
            return None

    def _generate_gemini_solution(self, user_query, matched_tickets, web_content=None):
        try:
            if not matched_tickets:
                return "In our past data, there are no similar records. Our technical team will look into this and call back soon with a solution."
            
            ticket_details = ""
            for ticket in matched_tickets:
                ticket_details += f"Ticket ID: {ticket['ticket_id']}\n"
                ticket_details += f"Query: {ticket['query']}\n"
                ticket_details += f"Answers: {', '.join(ticket['answers'])}\n\n"
            
            web_info = f"Web Search Results:\n{web_content}\n\n" if web_content else ""
            
            prompt = f"""
User Query: {user_query}

Related tickets from the database:
{ticket_details}
{web_info}
Instructions:
- If no ticket details are provided or they indicate "No matching query found in database.", return: "In our past data, there are no similar records. Our technical team will look into this and call back soon with a solution."
- Otherwise, generate a concise solution to the user's issue in 3-4 lines, with each line not exceeding 10 words. foe example, "1. some solution 1\n 2. some solution 2\n 3. some solution 3"
- Do not request additional information or tickets.
"""
            response = self.gemini_model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error generating Gemini solution: {e}")
            return "Unable to generate a solution at this time."

    def _web_search(self, query):
        try:
            url = f"https://api.duckduckgo.com/?q={query}&format=json"
            response = requests.get(url)
            data = response.json()
            results = data.get("RelatedTopics", [])
            web_content = ""
            for result in results[:3]:
                if "Text" in result:
                    web_content += result["Text"] + "\n"
            return web_content if web_content else None
        except Exception as e:
            print(f"Error during web search: {e}")
            return None

    def _save_to_db(self, query, solution, customer, laptop_id):
        try:
            ticket = {
                "ticket_id": f"TICK{str(uuid.uuid4())[:8]}",
                "customer_id": customer["customer_id"],
                "laptop_id": laptop_id,
                "query": query,
                "answers": [solution]
            }
            db.add_ticket(ticket)
        except Exception as e:
            print(f"Error saving to database: {e}")

    def _save_to_json(self, query_data):
        try:
            json_file = "new_queries.json"
            queries = []
            if os.path.exists(json_file):
                with open(json_file, "r") as f:
                    queries = json.load(f)
            queries.append(query_data)
            with open(json_file, "w") as f:
                json.dump(queries, f, indent=2)
        except Exception as e:
            print(f"Error saving to JSON: {e}")

    def retrieve(self, query, customer, laptop_id, k=3):
        try:
            if not self.vector_store:
                return {"message": "No tickets available in database."}
            
            # Find laptop details
            laptop = next((l for l in customer["laptops"] if l["laptop_id"] == laptop_id), None)
            if laptop:
                query_with_context = f"{query} for {laptop['name']} {laptop['model']}"
            else:
                query_with_context = query

            # Perform similarity search
            results = self.vector_store.similarity_search_with_score(query_with_context, k=k)
            matched_tickets = []
            
            for doc, score in results:
                if score > 0.5:  # Only include matches with ~70% similarity
                    continue
                # Check if laptop model matches
                ticket_query = doc.metadata["query"].lower()
                if laptop and (laptop['name'].lower() not in ticket_query and laptop['model'].lower() not in ticket_query):
                    continue
                matched_tickets.append({
                    "ticket_id": doc.metadata["ticket_id"],
                    "query": doc.metadata["query"],
                    "answers": doc.metadata["answers"]
                })
            
            if not matched_tickets:
                return {"message": "No matching query found in database."}
            
            solution = self._generate_gemini_solution(query_with_context, matched_tickets)
            self._save_to_db(query, solution, customer, laptop_id)
            self._save_to_json({
                "query": query,
                "laptop_id": laptop_id,
                "customer_id": customer["customer_id"],
                "solution": solution
            })
            return {
                "query": query,
                "solution": solution,
                "references": matched_tickets
            }
        except Exception as e:
            print(f"Error retrieving query: {e}")
            return {"message": "Error processing query."}

    def generate_solution_with_web(self, query, customer, laptop_id):
        try:
            web_content = self._web_search(query)
            matched_tickets = []
            laptop = next((l for l in customer["laptops"] if l["laptop_id"] == laptop_id), None)
            if laptop:
                query_with_context = f"{query} for {laptop['name']} {laptop['model']}"
            else:
                query_with_context = query
            solution = self._generate_gemini_solution(query_with_context, matched_tickets, web_content)
            self._save_to_db(query, solution, customer, laptop_id)
            self._save_to_json({
                "query": query,
                "laptop_id": laptop_id,
                "customer_id": customer["customer_id"],
                "solution": solution
            })
            return {
                "query": query,
                "solution": solution,
                "references": []
            }
        except Exception as e:
            print(f"Error generating solution with web search: {e}")
            return {"message": "Unable to generate a solution at this time."}

rag_pipeline = RAGPipeline()