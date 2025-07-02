import json
import os
import logging
from pymongo import MongoClient
import google.generativeai as genai
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY", "AIzaSyA6G0a178pQgJ_rkGxKWz-gXieGOeMNteA"))
chat_model = genai.GenerativeModel('gemini-1.5-flash')

class RAGSystem:
    def __init__(self):
        try:
            self.client = MongoClient("localhost", 27017)
            self.db = self.client["Ticketing_Platform"]
            self.tickets_collection = self.db["tickets"]
            self.embedding_file = "ticket_embeddings.json"
            self.embedding_model = "models/embedding-001"
            self._load_or_generate_embeddings()
            logger.info("RAGSystem initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RAGSystem: {e}")
            raise

    def _generate_embedding(self, text: str) -> list:
        try:
            result = genai.embed_content(model=self.embedding_model, content=text, task_type="retrieval_document")
            logger.debug(f"Generated embedding for text: {text[:50]}...")
            return result["embedding"]
        except Exception as e:
            logger.error(f"Failed to generate embedding for text '{text[:50]}...': {e}")
            return []

    def _generate_response(self, query: str, similar_data: list = None, chat_history: list = None) -> str:
        try:
            if similar_data:
                # Format similar data for Gemini
                similar_text = ""
                for item in similar_data[:5]:
                    similar_text += (
                        f"Ticket ID: {item['ticket_id']}<br>"
                        f"Query: {item['query']}<br>"
                        f"Answers: {', '.join(item['answers'])}<br><br>"
                    )
                prompt = (
                    f"User query: '{query}'<br>"
                    f"Chat history: {chat_history[-2:] if chat_history else []}<br>"
                    f"Similar issues from past data:<br>{similar_text}<br>"
                    "Generate a concise solution in 3-4 lines, max 20 words per line."
                )
                response = chat_model.generate_content(prompt)
                lines = response.text.strip().split('\n')[:4]
                lines = [' '.join(line.split()[:20]) for line in lines]
                return "".join(f"{line}<br>" for line in lines)
            else:
                prompt = (
                    f"User query: '{query}'<br>"
                    f"Chat history: {chat_history[-2:] if chat_history else []}<br>"
                    "No similar records found. Provide a general solution in 3-4 lines, max 20 words per line."
                )
                response = chat_model.generate_content(prompt)
                lines = response.text.strip().split('\n')[:4]
                lines = [' '.join(line.split()[:20]) for line in lines]
                return (
                    "In our past data, no similar record found.<br>"
                    "As per AI knowledge, basic steps to resolve:<br>" +
                    "".join(f"{line}<br>" for line in lines)
                )
        except Exception as e:
            logger.error(f"Failed to generate response for query '{query}': {e}")
            return "Error generating response. Please try again."

    def _load_or_generate_embeddings(self):
        try:
            if os.path.exists(self.embedding_file):
                with open(self.embedding_file, 'r') as f:
                    self.embeddings = json.load(f)
                logger.info(f"Loaded embeddings from {self.embedding_file}")
            else:
                self.embeddings = {"by_brand": {}, "by_id": {}}
                tickets = self.tickets_collection.find()
                for ticket in tickets:
                    query = ticket.get("query", "")
                    ticket_id = str(ticket["_id"])
                    answers = ticket.get("answers", [])
                    
                    if not isinstance(query, str) or not query.strip():
                        logger.warning(f"Skipping ticket {ticket_id} with invalid query: {query}")
                        continue
                    
                    embedding = self._generate_embedding(query)
                    if not embedding:
                        logger.warning(f"Skipping ticket {ticket_id} due to embedding failure")
                        continue
                    
                    brand = "Unknown"
                    query_lower = query.lower()
                    if "macbook" in query_lower:
                        brand = "Apple"
                    elif "hp" in query_lower:
                        brand = "HP"
                    elif "dell" in query_lower:
                        brand = "Dell"
                    
                    self.embeddings["by_id"][ticket_id] = {
                        "query": query,
                        "embedding": embedding,
                        "answers": answers,
                        "brand": brand
                    }
                    if brand not in self.embeddings["by_brand"]:
                        self.embeddings["by_brand"][brand] = []
                    self.embeddings["by_brand"][brand].append(ticket_id)
                
                with open(self.embedding_file, 'w') as f:
                    json.dump(self.embeddings, f)
                logger.info(f"Saved embeddings to {self.embedding_file}")
        except Exception as e:
            logger.error(f"Error loading or generating embeddings: {e}")
            raise

    def retrieve_answers(self, query: str, chat_history: list, top_k: int = 3, similarity_threshold: float = 0.9) -> dict:
        try:
            if not isinstance(query, str) or not query.strip():
                logger.error(f"Invalid query: {query}")
                return {"formatted_response": "Invalid query provided."}
            
            query_embedding = self._generate_embedding(query)
            if not query_embedding:
                logger.warning(f"No embedding for query: {query}")
                return {"formatted_response": self._generate_response(query, chat_history=chat_history)}
            
            brand = "Unknown"
            query_lower = query.lower()
            if "macbook" in query_lower:
                brand = "Apple"
            elif "hp" in query_lower:
                brand = "HP"
            elif "dell" in query_lower:
                brand = "Dell"
            logger.info(f"Query brand: {brand}")
            
            candidate_ids = self.embeddings["by_brand"].get(brand, list(self.embeddings["by_id"].keys()))
            similarities = []
            for ticket_id in candidate_ids:
                ticket = self.embeddings["by_id"][ticket_id]
                try:
                    similarity = cosine_similarity(
                        [query_embedding],
                        [ticket["embedding"]]
                    )[0][0]
                    if similarity >= similarity_threshold:
                        similarities.append((ticket_id, similarity))
                except Exception as e:
                    logger.error(f"Error computing similarity for ticket {ticket_id}: {e}")
                    continue
            
            similarities.sort(key=lambda x: x[1], reverse=True)
            top_matches = similarities[:top_k]
            
            if not top_matches:
                logger.info(f"No tickets with similarity >= {similarity_threshold} for query: {query}")
                return {"formatted_response": self._generate_response(query, chat_history=chat_history)}
            
            # Format results
            similar_data = []
            result_html = "<div>Found similar issues:<br>"
            for ticket_id, similarity in top_matches:
                ticket = self.embeddings["by_id"][ticket_id]
                result_html += (
                    "<div class='ticket-result'>"
                    f"<strong>Ticket ID:</strong> {ticket_id}<br>"
                    f"<strong>Query:</strong> {ticket['query']}<br>"
                    f"<strong>Answers:</strong><ul>" +
                    "".join(f"<li>{answer}</li>" for answer in ticket["answers"]) +
                    f"</ul><strong>Similarity:</strong> {similarity:.2%}<br>"
                    "</div>"
                )
                similar_data.append({
                    "ticket_id": ticket_id,
                    "query": ticket["query"],
                    "answers": ticket["answers"],
                    "similarity": similarity
                })
            
            # Generate concise response
            response = self._generate_response(query, similar_data, chat_history)
            result_html += f"<strong>Solution:</strong><br>{response}</div>"
            
            logger.info(f"Retrieved answers for query '{query}' with {len(top_matches)} matches")
            return {"formatted_response": result_html}
        except Exception as e:
            logger.error(f"Error retrieving answers for query '{query}': {e}")
            return {"formatted_response": self._generate_response(query, chat_history=chat_history)}