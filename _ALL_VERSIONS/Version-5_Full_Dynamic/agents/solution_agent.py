from agents.rag import rag_pipeline

def solution_agent(state):
    query = state.get("query")
    customer = state.get("customer")
    laptop_id = state.get("laptop_id")
    if not query or not customer or not laptop_id:
        return {"result": {"message": "Missing query, customer, or laptop ID"}, "step": "solution_generate"}
    
    result = rag_pipeline.generate_solution_with_web(query, customer, laptop_id)
    return {"result": result, "step": "solution_generate"}