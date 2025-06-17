import streamlit as st
from agents.graph import app as langgraph_app
from db import db
import uuid

st.title("AI Ticketing Platform")

# Initialize session state
if "state" not in st.session_state:
    st.session_state.state = {"username": "", "customer": None, "new_user": False, "step": "username"}
if "graph_output" not in st.session_state:
    st.session_state.graph_output = None

# Step 1: Username input
if st.session_state.state["step"] == "username":
    username = st.text_input("Enter your username:")
    if st.button("Submit Username"):
        if username:
            # Run Authentication Agent via LangGraph
            st.session_state.state["username"] = username
            output = langgraph_app.invoke(st.session_state.state)
            st.session_state.graph_output = output
            st.session_state.state = output
            if output["customer"]:
                st.success(f"Welcome, {output['customer']['name']}!")
                st.session_state.state["step"] = "laptop_select"  # Next step (implemented in Phase 2)
            elif output["new_user"]:
                st.warning("User not found. Please register.")
                st.session_state.state["step"] = "register"
        else:
            st.error("Please enter a username.")

# Step 2: New user registration
if st.session_state.state["step"] == "register":
    st.subheader("Register New User")
    name = st.text_input("Full Name:")
    laptop_name = st.text_input("Laptop Name (e.g., HP Pavilion x360):")
    laptop_model = st.text_input("Laptop Model (e.g., 14-dw1036TU):")
    cpu = st.text_input("CPU (e.g., Intel i5-1135G7):")
    ram = st.text_input("RAM (e.g., 8GB):")
    storage = st.text_input("Storage (e.g., 512GB SSD):")
    if st.button("Register"):
        if all([name, laptop_name, laptop_model, cpu, ram, storage]):
            customer = {
                "username": st.session_state.state["username"],
                "customer_id": f"CUST{str(uuid.uuid4())[:8]}",
                "name": name,
                "laptops": [{
                    "laptop_id": f"LAP{str(uuid.uuid4())[:8]}",
                    "name": laptop_name,
                    "model": laptop_model,
                    "specifications": {
                        "cpu": cpu,
                        "ram": ram,
                        "storage": storage
                    }
                }]
            }
            if db.add_customer(customer):
                st.session_state.state["customer"] = customer
                st.session_state.state["new_user"] = False
                st.session_state.state["step"] = "laptop_select"  # Next step
                st.success("Registration successful!")
            else:
                st.error("Failed to register. Try again.")
        else:
            st.error("Please fill all fields.")

if __name__ == "__main__":
    st.write("AI Ticketing Platform ready.")
