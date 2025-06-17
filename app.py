import streamlit as st
from graph import app as langgraph_app
from db import db
import uuid
import time

st.title("AI Ticketing Platform")

# Initialize session state
if "state" not in st.session_state:
    st.session_state.state = {
        "username": "",
        "customer": None,
        "new_user": False,
        "laptop_id": None,
        "laptop_details": None,
        "query": "",
        "result": {},
        "message": "",
        "step": "username",
        "output_history": []  # Store all messages
    }

# Function to add message to output history
def add_to_output_history(message, type="user"):
    timestamp = time.time()
    # Avoid duplicates
    if not any(entry["message"] == message and entry["type"] == type for entry in st.session_state.state["output_history"]):
        st.session_state.state["output_history"].append({"message": message, "type": type, "timestamp": timestamp})

# Function to run graph and update state
def run_graph(state):
    output = langgraph_app.invoke(state)
    st.session_state.state.update(output)
    if output.get("message"):
        add_to_output_history(output["message"], "system " + ("success" if "found" in output["message"] or "saved" in output["message"] else "warning"))
    return output

# Handle button actions in sidebar
with st.sidebar:
    if st.session_state.state["step"] == "username" and st.button("Send", key="username_send"):
        username = st.session_state.get("username_input", "")
        if username:
            st.session_state.state["username"] = username
            add_to_output_history(f"Username: {username}")
            output = run_graph(st.session_state.state)
            if output["customer"]:
                st.session_state.state["step"] = "laptop_select"
            elif output["new_user"]:
                st.session_state.state["step"] = "register"
            st.rerun()
        else:
            add_to_output_history("Please enter a username.", "system error")
            st.rerun()

    if st.session_state.state["step"] == "register" and st.button("Register", key="register"):
        name = st.session_state.get("name", "")
        laptop_name = st.session_state.get("laptop_name", "")
        laptop_model = st.session_state.get("laptop_model", "")
        cpu = st.session_state.get("cpu", "")
        ram = st.session_state.get("ram", "")
        storage = st.session_state.get("storage", "")
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
                add_to_output_history(f"Registered: {name} with {laptop_name} ({laptop_model})")
                add_to_output_history("Registration successful!", "system success")
            else:
                add_to_output_history("Failed to register. Try again.", "system error")
            st.rerun()
        else:
            add_to_output_history("Please fill all fields.", "system error")
            st.rerun()

    if st.session_state.state["step"] == "laptop_select":
        if st.button("Add Laptop", key="add_laptop") and st.session_state.get("add_new_laptop", False):
            new_laptop_name = st.session_state.get("new_laptop_name", "")
            new_laptop_model = st.session_state.get("new_laptop_model", "")
            new_cpu = st.session_state.get("new_cpu", "")
            new_ram = st.session_state.get("new_ram", "")
            new_storage = st.session_state.get("new_storage", "")
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
                ).modified_count:
                    st.session_state.state["customer"] = customer
                    add_to_output_history(f"Added laptop: {new_laptop_name} ({new_laptop_model})")
                    add_to_output_history("New laptop added!", "system success")
                else:
                    add_to_output_history("Failed to add laptop.", "system error")
            else:
                add_to_output_history("Please fill all fields.", "system error")
            st.rerun()
        
        if st.button("Proceed", key="laptop_proceed"):
            selected_laptop = st.session_state.get("selected_laptop", "Select a laptop")
            laptops = st.session_state.state["customer"]["laptops"]
            laptop_options = [f"{laptop['name']} ({laptop['model']})" for laptop in laptops]
            if selected_laptop in laptop_options:
                laptop_index = laptop_options.index(selected_laptop)
                st.session_state.state["laptop_id"] = laptops[laptop_index]["laptop_id"]
                st.session_state.state["laptop_details"] = laptops[laptop_index]
                st.session_state.state["step"] = "query_process"
                add_to_output_history(f"Selected laptop: {selected_laptop}")
                add_to_output_history("Laptop selected!", "system success")
            else:
                add_to_output_history("Please select a laptop.", "system error")
            st.rerun()

    if st.session_state.state["step"] == "query_process" and st.button("Send", key="query_send"):
        query = st.session_state.get("query_input", "")
        if query:
            laptop = st.session_state.state["laptop_details"]
            if laptop:
                laptop_context = f"{laptop['name']} {laptop['model']}, {laptop['specifications']['cpu']} query is: "
                enhanced_query = f"{laptop_context}{query}"
            else:
                enhanced_query = query
            add_to_output_history(f"Query: {query}")
            st.session_state.state["query"] = enhanced_query
            output = run_graph(st.session_state.state)
            if output["result"].get("solution"):
                add_to_output_history("Solution found!", "system success")
                add_to_output_history(f"Solution: {output['result']['solution']}", "system info")
                if output["result"].get("references"):
                    for ref in output["result"]["references"]:
                        add_to_output_history(f"Reference - Ticket ID: {ref['ticket_id']}, Query: {ref['query']}, Solution: {', '.join(ref['answers'])}", "system info")
                st.session_state.state["step"] = "query_options"
            else:
                add_to_output_history("Your query has been noted. We will follow up soon.", "system info")
                st.session_state.state["step"] = "query_options"
            st.rerun()
        else:
            add_to_output_history("Please enter a query.", "system error")
            st.rerun()

    if st.session_state.state["step"] == "query_options":
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Enter Another Query", key="another_query"):
                st.session_state.state["step"] = "query_process"
                add_to_output_history("Ready to enter another query.", "system info")
                st.rerun()
        with col2:
            if st.button("Exit", key="exit"):
                st.session_state.state = {
                    "username": "",
                    "customer": None,
                    "new_user": False,
                    "laptop_id": None,
                    "laptop_details": None,
                    "query": "",
                    "result": {},
                    "message": "",
                    "step": "username",
                    "output_history": []
                }
                add_to_output_history("Session ended. Start a new session.", "system info")
                st.rerun()

    # Display input for current state in sidebar
    if st.session_state.state["step"] == "username":
        st.text_input("Enter your username:", placeholder="e.g., john_doe", key="username_input")

    if st.session_state.state["step"] == "register":
        st.text_input("Full Name:", placeholder="e.g., John Doe", key="name")
        st.text_input("Laptop Name:", placeholder="e.g., HP Pavilion x360", key="laptop_name")
        st.text_input("Laptop Model:", placeholder="e.g., 14-dw1036TU", key="laptop_model")
        st.text_input("CPU:", placeholder="e.g., Intel i5-1135G7", key="cpu")
        st.text_input("RAM:", placeholder="e.g., 8GB", key="ram")
        st.text_input("Storage:", placeholder="e.g., 512GB SSD", key="storage")

    if st.session_state.state["step"] == "laptop_select":
        laptops = st.session_state.state["customer"]["laptops"]
        laptop_options = [f"{laptop['name']} ({laptop['model']})" for laptop in laptops]
        st.selectbox("Choose a laptop:", ["Select a laptop"] + laptop_options, key="selected_laptop")
        st.session_state.add_new_laptop = st.checkbox("Add a new laptop")
        if st.session_state.add_new_laptop:
            st.text_input("New Laptop Name:", placeholder="e.g., Dell XPS 13", key="new_laptop_name")
            st.text_input("New Laptop Model:", placeholder="e.g., XPS-9310", key="new_laptop_model")
            st.text_input("New CPU:", placeholder="e.g., Intel i7-1165G7", key="new_cpu")
            st.text_input("New RAM:", placeholder="e.g., 16GB", key="new_ram")
            st.text_input("New Storage:", placeholder="e.g., 1TB SSD", key="new_storage")

    if st.session_state.state["step"] == "query_process":
        st.text_area("Enter your query:", placeholder="e.g., How to fix blue screen error?", key="query_input")

# Display all output messages on main screen
for message in sorted(st.session_state.state["output_history"], key=lambda x: x["timestamp"]):
    if message["type"].startswith("system"):
        if message["type"].endswith("success"):
            st.success(message["message"])
        elif message["type"].endswith("warning"):
            st.warning(message["message"])
        elif message["type"].endswith("error"):
            st.error(message["message"])
        else:
            st.info(message["message"])
    else:
        st.write(f"You: {message['message']}")

if __name__ == "__main__":
    st.write("AI Ticketing Platform ready.")