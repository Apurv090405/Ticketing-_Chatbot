from langgraph.graph import StateGraph, END
from typing import TypedDict
from agents.auth_agent import auth_agent
from agents.query_agent import query_agent
from agents.solution_agent import solution_agent
from agents.ticket_agent import ticket_agent

class State(TypedDict):
    username: str
    customer: dict
    new_user: bool
    laptop_id: str
    query: str
    result: dict
    message: str
    step: str

def route_auth(state):
    if state["new_user"]:
        return "register"
    elif state["customer"]:
        return "laptop_select"
    return "auth"

def route_query(state):
    if state["result"].get("solution"):
        return "ticket_save"
    return "solution_generate"

workflow = StateGraph(State)
workflow.add_node("auth", auth_agent)
workflow.add_node("register", lambda x: x)  # Placeholder, handled in app.py
workflow.add_node("laptop_select", lambda x: x)  # Placeholder, handled in app.py
workflow.add_node("query_process", query_agent)
workflow.add_node("solution_generate", solution_agent)
workflow.add_node("ticket_save", ticket_agent)

workflow.set_entry_point("auth")
workflow.add_conditional_edges(
    "auth",
    route_auth,
    {
        "register": "register",
        "laptop_select": "laptop_select",
        "auth": "auth"
    }
)
workflow.add_edge("register", "laptop_select")
workflow.add_edge("laptop_select", "query_process")
workflow.add_conditional_edges(
    "query_process",
    route_query,
    {
        "solution_generate": "solution_generate",
        "ticket_save": "ticket_save"
    }
)
workflow.add_edge("solution_generate", "ticket_save")
workflow.add_edge("ticket_save", END)

app = workflow.compile()