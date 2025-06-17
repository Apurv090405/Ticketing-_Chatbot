from db import db
import uuid

def ticket_agent(state):
    query = state.get("query")
    customer = state.get("customer")
    laptop_id = state.get("laptop_id")
    result = state.get("result")
    
    if not query or not customer or not laptop_id or not result:
        return {"message": "Cannot save ticket: missing data", "step": "ticket_save"}
    
    # Ticket already saved in rag.py, so skip if solution exists
    if result.get("solution"):
        return {"message": "Ticket already saved", "step": "ticket_save"}
    
    ticket = {
        "ticket_id": f"TICK{str(uuid.uuid4())[:8]}",
        "customer_id": customer["customer_id"],
        "laptop_id": laptop_id,
        "query": query,
        "answers": [result.get("solution", "No solution provided")]
    }
    
    if db.add_ticket(ticket):
        return {"message": "Ticket saved successfully", "step": "ticket_save"}
    return {"message": "Failed to save ticket", "step": "ticket_save"}