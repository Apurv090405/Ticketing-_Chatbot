from agents.rag import rag_pipeline

def query_agent(state):
    query = state.get("query")
    if not query:
        return {"result": {"message": "No query provided"}, "step": "query_process"}
    
    result = rag_pipeline.retrieve(query)
    return {"result": result, "step": "query_process"}