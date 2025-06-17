from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import Document
import google.generativeai as genai
from db import db
from dotenv import load_dotenv
import os
import json
import requests
from bs4 import BeautifulSoup

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
            ticket_details = ""
            for ticket in matched_tickets:
                ticket_details += f"Ticket ID: {ticket['ticket_id']}\n"
                ticket_details += f"Query: {ticket['query']}\n"
                ticket_details += f"Answers: {', '.join(ticket['answers'])}\n\n"
            
            web_info = f"Web Search Results:\n{web_content}\n\n" if web_content else ""
            
            prompt = f"""
User Query: {user_query}

The following are related tickets from the database:
{ticket_details}
{web_info}
Based on the user query, provided tickets, and web search results (if any), generate a concise and accurate solution to the user's issue.
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

    def retrieve(self, query, k=3):
        try:
            if not self.vector_store:
                return {"message": "No tickets available in the database."}
            results = self.vector_store.similarity_search_with_score(query, k=k)
            matched_tickets = [
                {
                    "ticket_id": doc.metadata["ticket_id"],
                    "query": doc.metadata["query"],
                    "answers": doc.metadata["answers"]
                }
                for doc, score in results if score <= 0.80
            ]
            if not matched_tickets:
                return {"message": "No matching query found."}
            solution = self._generate_gemini_solution(query, matched_tickets)
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
            new_query = {
                "query": query,
                "laptop_id": laptop_id,
                "customer_id": customer["customer_id"],
                "solution": solution
            }
            self._save_to_json(new_query)
            return {
                "query": query,
                "solution": solution,
                "references": []
            }
        except Exception as e:
            print(f"Error generating solution with web search: {e}")
            return {"message": "Unable to generate a solution at this time."}

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

rag_pipeline = RAGPipeline()