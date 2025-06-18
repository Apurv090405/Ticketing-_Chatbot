from db import db

def auth_agent(state):
    username = state.get("username")
    if not username:
        return {"message": "No username provided", "step": "username"}
    
    customer = db.get_customer_by_username(username)
    if customer:
        return {
            "customer": customer,
            "new_user": False,
            "message": f"User {username} found.",
            "step": "laptop_select"
        }
    else:
        return {
            "customer": None,
            "new_user": True,
            "message": f"User {username} not found.",
            "step": "register"
        }