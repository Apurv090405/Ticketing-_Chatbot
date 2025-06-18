from agents.rag import rag_pipeline

def query_agent(state):
    query = state.get("query")
    customer = state.get("customer")
    laptop_id = state.get("laptop_id")
    if not query or not customer or not laptop_id:
        return {"result": {"message": "No query, customer, or laptop ID provided"}, "step": "query_process"}
    
    result = rag_pipeline.retrieve(query, customer, laptop_id)
    return {"result": result, "step": "query_process"}