from langgraph.graph import StateGraph, END
from typing import TypedDict
from agents.auth_agent import auth_agent

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
    return "username"

workflow = StateGraph(State)
workflow.add_node("auth", auth_agent)
# Placeholder nodes for future phases
workflow.add_node("register", lambda x: x)  # No-op for now, handled by app.py
workflow.add_node("laptop_select", lambda x: x)  # Placeholder

workflow.set_entry_point("auth")
workflow.add_conditional_edges(
    "auth",
    route_auth,
    {
        "register": "register",
        "laptop_select": "laptop_select",
        "username": "auth"  # Loop back if invalid
    }
)
workflow.add_edge("register", END)  # End after registration (updated in app.py)
workflow.add_edge("laptop_select", END)  # Placeholder for Phase 2

app = workflow.compile()