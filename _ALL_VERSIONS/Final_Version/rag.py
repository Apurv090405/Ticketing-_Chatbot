import json
import os
import logging
from pymongo import MongoClient
import google.generativeai as genai
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Tuple, Dict

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY", "AIzaSyBwD8BX_kzPJXR4Lqzvv9aEQ5-JaFrtucw"))
chat_model = genai.GenerativeModel('gemini-2.5-flash-lite-preview-06-17')

class RAGSystem:
    def __init__(self):
        try:
            self.client = MongoClient("localhost", 27017)
            self.db = self.client["Ticketing_Platform"]
            self.tickets_collection = self.db["tickets"]
            self.embedding_file = "ticket_embeddings.json"
            self.embedding_model = "models/embedding-001"
            self.brand_keywords = {
                "Apple": ["macbook", "apple", "mac"],
                "HP": ["hp", "pavilion"],
                "Dell": ["dell", "inspiron", "xps"],
                "Lenovo": ["lenovo", "thinkpad"],
                "Asus": ["asus", "zenbook"],
                "Acer": ["acer", "aspire"],
                "Microsoft": ["surface", "microsoft"],
                "Samsung": ["samsung", "galaxy book"],
                "MSI": ["msi", "prestige"]
            }
            self._load_or_generate_embeddings()
            logger.info("RAGSystem initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RAGSystem: {e}")
            raise

    def _extract_keywords(self, query: str) -> Tuple[str, str, List[str]]:
        """Extract keywords from query using LLM while preserving context."""
        try:
            prompt = (
                f"""You are an AI assistant for a laptop support platform. 
                Given the query: '{query}'
                Task: Extract key technical terms, brand names, and issue-related keywords.
                Return a JSON object with:
                - 'processed_query': cleaned query without brand keywords
                - 'brand': detected brand name or 'Unknown'
                - 'keywords': list of relevant technical terms and issues
                Ensure no context is lost and keywords are specific to laptop issues.
                Example output:
                {
                    "processed_query": "screen flickering issue",
                    "brand": "Dell",
                    "keywords": ["screen", "flickering", "display", "issue"]
                }
                """
            )
            response = chat_model.generate_content(prompt)
            result = json.loads(response.text.strip())
            return (
                result.get("processed_query", query.lower()),
                result.get("brand", "Unknown"),
                result.get("keywords", [])
            )
        except Exception as e:
            logger.error(f"Failed to extract keywords for query '{query}': {e}")
            return query.lower(), "Unknown", []

    def _generate_embedding(self, text: str) -> list:
        try:
            logger.debug(f"Generating embedding for text: {text[:50]}...")
            result = genai.embed_content(model=self.embedding_model, content=text, task_type="retrieval_document")
            return result["embedding"]
        except Exception as e:
            logger.error(f"Failed to generate embedding for text '{text[:50]}...': {e}")
            return []

    def _batch_generate_embeddings(self, texts: List[str]) -> List[list]:
        """Generate embeddings for multiple texts in batch."""
        try:
            embeddings = []
            for text in texts:
                embedding = self._generate_embedding(text)
                embeddings.append(embedding)
            return embeddings
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            return [[] for _ in texts]

    def _generate_response(self, query: str, similar_data: list = None, chat_history: list = None, keywords: List[str] = None) -> str:
        try:
            if similar_data:
                similar_text = "\n".join([
                    f"Ticket ID: {item['ticket_id']}\nQuery: {item['query']}\nAnswers: {', '.join(item['answers'])}"
                    for item in similar_data[:5]
                ])
                prompt = (
                    f"""You are a helpful and neutral AI assistant for a laptop support ticketing platform. 
                    Your goal is to assist users by offering solutions based on these detail
                    - User query: '{query}'
                    - Keywords: {json.dumps(keywords)}
                    - Chat history: {json.dumps(chat_history[-2:] if chat_history else [])}
                    - Similar issues from past data: {similar_text}
                    Provide a step-by-step solution in a clear, ordered list, starting with the easiest steps and progressing to harder ones.
                    - Limit to 5–7 steps, each under 20 words.
                    - Use simple, non-technical language.
                    - Ensure steps are practical and ordered by complexity.
                    - Add a brief summary (1–2 lines, max 20 words each) explaining the approach.
                    ---
                    Do not use bold or italic text. Structure the output clearly with HTML <ol> tags for steps.
                    ---
                    If the user asks about something unrelated to laptop support, politely let them know it's beyond your scope.
                    ---
                    Vary phrasing across responses to avoid repetition. Keep the tone friendly and clear.
                    """
                )
                response = chat_model.generate_content(prompt)
                return response.text.strip()
            else:
                prompt = (
                    f"""You are a friendly AI assistant on an AI ticketing platform that helps users with laptop-related problems.
                    ---
                    User query: '{query}'
                    Keywords: {json.dumps(keywords)}
                    Chat history: {json.dumps(chat_history[-2:] if chat_history else [])}
                    ---
                    No matching records found. Provide a basic step-by-step troubleshooting guide in a clear, ordered list.
                    - Start with the easiest steps, progressing to harder ones (3–5 steps, each under 20 words).
                    - Use plain, non-technical language.
                    - After the steps, encourage the user to upload a support ticket for further help.
                    - Add a brief summary (1–2 lines, max 20 words each) explaining the approach.
                    ---
                    Use HTML <ol> tags for steps.
                    ---
                    If the user's question is unrelated to laptop issues, politely explain that it's outside the platform's scope in 1–2 lines.
                    ---
                    Keep the tone calm, neutral, and conversational. Vary phrasing to prevent repetition.
                    """
                )
                response = chat_model.generate_content(prompt)
                return response.text.strip()
        except Exception as e:
            logger.error(f"Failed to generate response for query '{query}': {e}")
            return "Error generating response. Please try again."

    def _load_or_generate_embeddings(self):
        try:
            # Initialize embeddings structure
            self.embeddings = {"by_brand": {}, "by_id": {}}

            # Check if embedding file exists
            if os.path.exists(self.embedding_file):
                with open(self.embedding_file, 'r') as f:
                    self.embeddings = json.load(f)
                logger.info(f"Loaded embeddings from {self.embedding_file}")
                return

            # If no file exists, generate embeddings for all tickets
            logger.info("No embedding file found. Generating embeddings for all tickets.")
            tickets = self.tickets_collection.find()
            queries = []
            ticket_data = []

            # Collect valid tickets and infer brand from query
            for ticket in tickets:
                query = ticket.get("query", "")
                ticket_id = str(ticket["_id"])
                answers = ticket.get("answers", [])
                if not isinstance(query, str) or not query.strip():
                    logger.warning(f"Skipping ticket {ticket_id} with invalid query: {query}")
                    continue

                # Infer brand from query using brand_keywords
                brand = "Unknown"
                query_lower = query.lower()
                for brand_name, keywords in self.brand_keywords.items():
                    if any(keyword in query_lower for keyword in keywords):
                        brand = brand_name
                        break

                queries.append(query)
                ticket_data.append((ticket_id, query, answers, brand))

            if not queries:
                logger.info("No valid tickets found to generate embeddings.")
                with open(self.embedding_file, 'w') as f:
                    json.dump(self.embeddings, f)
                return

            # Generate embeddings for all queries
            embeddings = self._batch_generate_embeddings(queries)

            # Store embeddings and metadata
            for (ticket_id, query, answers, brand), embedding in zip(ticket_data, embeddings):
                if not embedding:
                    logger.warning(f"Skipping ticket {ticket_id} due to embedding failure")
                    continue
                self.embeddings["by_id"][ticket_id] = {
                    "query": query,
                    "processed_query": query.lower(),
                    "embedding": embedding,
                    "answers": answers,
                    "brand": brand,
                    "keywords": []
                }
                if brand not in self.embeddings["by_brand"]:
                    self.embeddings["by_brand"][brand] = []
                self.embeddings["by_brand"][brand].append(ticket_id)

            # Save embeddings to file
            with open(self.embedding_file, 'w') as f:
                json.dump(self.embeddings, f)
            logger.info(f"Generated and saved embeddings to {self.embedding_file}")

        except Exception as e:
            logger.error(f"Error loading or generating embeddings: {e}")
            # Save empty embeddings to prevent repeated failures
            with open(self.embedding_file, 'w') as f:
                json.dump(self.embeddings, f)
            raise

    def retrieve_answers(self, query: str, chat_history: list = None, top_k: int = 5, similarity_threshold: float = 0.9) -> dict:
        try:
            if not isinstance(query, str) or not query.strip():
                logger.error(f"Invalid query: {query}")
                return {"formatted_response": "Invalid query provided."}
            
            processed_query, brand, keywords = self._extract_keywords(query)
            query_embedding = self._generate_embedding(processed_query)
            if not query_embedding:
                logger.warning(f"No embedding for query: {query}")
                return {"formatted_response": self._generate_response(query, chat_history=chat_history, keywords=keywords)}
            
            logger.info(f"Query brand: {brand}, Processed query: {processed_query}, Keywords: {keywords}")
            
            # Prioritize brand and keyword matches
            candidate_ids = set()
            if brand != "Unknown":
                candidate_ids.update(self.embeddings["by_brand"].get(brand, []))
            for keyword in keywords:
                for ticket_id, ticket in self.embeddings["by_id"].items():
                    if any(kw in ticket["keywords"] for kw in keywords):
                        candidate_ids.add(ticket_id)
            candidate_ids.update(self.embeddings["by_id"].keys())  # Fallback to all tickets

            similarities = []
            for ticket_id in candidate_ids:
                ticket = self.embeddings["by_id"][ticket_id]
                try:
                    similarity = cosine_similarity([query_embedding], [ticket["embedding"]])[0][0]
                    if similarity >= similarity_threshold:
                        similarities.append((ticket_id, similarity))
                except Exception as e:
                    logger.error(f"Error computing similarity for ticket {ticket_id}: {e}")
                    continue
            similarities.sort(key=lambda x: x[1], reverse=True)
            top_matches = similarities[:top_k]
            
            if not top_matches:
                logger.info(f"No tickets with similarity >= {similarity_threshold} for query: {query}")
                return {"formatted_response": self._generate_response(query, chat_history=chat_history, keywords=keywords)}
            
            similar_data = [
                {
                    "ticket_id": ticket_id,
                    "query": self.embeddings["by_id"][ticket_id]["query"],
                    "answers": self.embeddings["by_id"][ticket_id]["answers"],
                    "similarity": similarity
                }
                for ticket_id, similarity in top_matches
            ]
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
            response = self._generate_response(query, similar_data, chat_history, keywords)
            result_html += f"<strong>Solution:</strong><br>{response}"
            logger.info(f"Retrieved answers for query '{query}' with {len(top_matches)} matches")
            return {"formatted_response": result_html}
        except Exception as e:
            logger.error(f"Error retrieving answers for query '{query}': {e}")
            return {"formatted_response": self._generate_response(query, chat_history=chat_history, keywords=keywords)}