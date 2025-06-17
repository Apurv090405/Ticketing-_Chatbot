import streamlit as st
from agents.graph import app as langgraph_app
from db import db
import uuid

st.title("AI Ticketing Platform")

# Initialize session state
if "state" not in st.session_state:
    st.session_state.state = {
        "username": "",
        "customer": None,
        "new_user": False,
        "laptop_id": None,
        "query": "",
        "result": {},
        "message": "",
        "step": "username",
        "output_display": None  # To persist output
    }

# Function to update state and run graph
def run_graph(state):
    output = langgraph_app.invoke(state)
    st.session_state.state.update(output)
    return output

# Step 1: Username input
if st.session_state.state["step"] == "username":
    username = st.text_input("Enter your username:")
    if st.button("Submit Username"):
        if username:
            st.session_state.state["username"] = username
            output = run_graph(st.session_state.state)
            st.session_state.state["output_display"] = output
            if output["customer"]:
                st.success(f"Welcome, {output['customer']['name']}!")
                st.session_state.state["step"] = "laptop_select"
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
                st.session_state.state["step"] = "laptop_select"
                st.success("Registration successful!")
            else:
                st.error("Failed to register. Try again.")
        else:
            st.error("Please fill all fields.")

# Step 3: Laptop selection
if st.session_state.state["step"] == "laptop_select":
    st.subheader("Select Your Laptop")
    laptops = st.session_state.state["customer"]["laptops"]
    laptop_options = [f"{laptop['name']} ({laptop['model']})" for laptop in laptops]
    selected_laptop = st.selectbox("Choose a laptop:", laptop_options)
    add_new_laptop = st.checkbox("Add a new laptop")
    
    if add_new_laptop:
        st.subheader("Add New Laptop")
        new_laptop_name = st.text_input("New Laptop Name:")
        new_laptop_model = st.text_input("New Laptop Model:")
        new_cpu = st.text_input("New CPU:")
        new_ram = st.text_input("New RAM:")
        new_storage = st.text_input("New Storage:")
        if st.button("Add Laptop"):
            if all([new_laptop_name, new_laptop_model, new_cpu, new_ram, new_storage]):
                new_laptop = {
                    "laptop_id": f"LAP{str(uuid.uuid4())[:8]}",
                    "name": new_laptop_name,
                    "model": new_laptop_model,
                    "specifications": {
                        "cpu": new_cpu,
                        "ram": new_ram,
                        "storage": new_storage
                    }
                }
                customer = st.session_state.state["customer"]
                customer["laptops"].append(new_laptop)
                if db.customers_collection.update_one(
                    {"username": customer["username"]},
                    {"$set": {"laptops": customer["laptops"]}}
                ):
                    st.session_state.state["customer"] = customer
                    st.success("New laptop added!")
                else:
                    st.error("Failed to add laptop.")
            else:
                st.error("Please fill all fields.")
    
    if st.button("Proceed with Selected Laptop"):
        if selected_laptop:
            laptop_index = laptop_options.index(selected_laptop)
            st.session_state.state["laptop_id"] = laptops[laptop_index]["laptop_id"]
            st.session_state.state["step"] = "query_process"
            st.success("Laptop selected!")
        else:
            st.error("Please select a laptop.")

# Step 4: Query input
if st.session_state.state["step"] == "query_process":
    st.subheader("Submit Your Query")
    query = st.text_area("Enter your query:")
    if st.button("Submit Query"):
        if query:
            st.session_state.state["query"] = query
            output = run_graph(st.session_state.state)
            st.session_state.state["output_display"] = output
            if output["result"].get("solution"):
                st.success("Solution found!")
                st.write("**Solution**:")
                st.write(output["result"]["solution"])
                if output["result"].get("references"):
                    st.write("**References**:")
                    for ref in output["result"]["references"]:
                        st.write(f"- Ticket ID: {ref['ticket_id']}, Query: {ref['query']}")
            else:
                st.info("Your query has been noted. We will follow up soon.")
        else:
            st.error("Please enter a query.")

# Display persisted output if available
if st.session_state.state["output_display"]:
    output = st.session_state.state["output_display"]
    if output.get("message") and st.session_state.state["step"] in ["username", "register"]:
        if "found" in output["message"]:
            st.success(output["message"])
        else:
            st.warning(output["message"])

if __name__ == "__main__":
    st.write("AI Ticketing Platform ready.")