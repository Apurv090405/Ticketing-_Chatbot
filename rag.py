from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import Document
import google.generativeai as genai
from db import db
from dotenv import load_dotenv
import os

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
            # Fetch all tickets from MongoDB
            tickets = db.get_tickets()
            if not tickets:
                print("Vector store not initialized: No tickets available.")
                return None
            # Create documents for LangChain
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
            # Create FAISS vector store
            return FAISS.from_documents(documents, self.embeddings)
        except Exception as e:
            print(f"Error initializing vector store: {e}")
            return None

    def _generate_gemini_solution(self, user_query, matched_tickets):
        try:
            # Format ticket details outside f-string
            ticket_details = ""
            for ticket in matched_tickets:
                ticket_details += f"Ticket ID: {ticket['ticket_id']}\n"
                ticket_details += f"Query: {ticket['query']}\n"
                ticket_details += f"Answers: {', '.join(ticket['answers'])}\n\n"
            
            # Prepare prompt for Gemini
            prompt = f"""
User Query: {user_query}

The following are related tickets from the database:
{ticket_details}
Based on the user query and the provided tickets, generate a concise and accurate solution to the user's issue.
"""
            response = self.gemini_model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error generating Gemini solution: {e}")
            return "Unable to generate a solution at this time."

    def retrieve(self, query, k=3):
        try:
            if not self.vector_store:
                return {"message": "No tickets available in the database."}
            # Search for similar tickets
            results = self.vector_store.similarity_search_with_score(query, k=k)
            # Filter relevant results (threshold 0.80)
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
            # Generate consolidated solution with Gemini
            gemini_solution = self._generate_gemini_solution(query, matched_tickets)
            return {
                "query": query,
                "solution": gemini_solution,
                "references": matched_tickets
            }
        except Exception as e:
            print(f"Error retrieving query: {e}")
            return {"message": "Error processing query."}

rag_pipeline = RAGPipeline()