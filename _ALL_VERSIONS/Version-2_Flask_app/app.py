from flask import Flask, render_template, request, session, redirect, url_for
from graph import app as langgraph_app
from db import db
import uuid
import time
import os
from dotenv import load_dotenv
from bson.objectid import ObjectId

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secure session key

# Helper function to convert ObjectId to string
def convert_objectid(data):
    if isinstance(data, ObjectId):
        return str(data)
    elif isinstance(data, dict):
        return {k: convert_objectid(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_objectid(item) for item in data]
    return data

# Initialize session state
def initialize_session():
    if "state" not in session:
        session["state"] = {
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
    session.modified = True

# Function to add message to output history
def add_to_output_history(message, type="user"):
    timestamp = time.time()
    # Avoid duplicates
    if not any(entry["message"] == message and entry["type"] == type for entry in session["state"]["output_history"]):
        session["state"]["output_history"].append({"message": message, "type": type, "timestamp": timestamp})
    session.modified = True

# Function to run graph and update state
def run_graph(state):
    output = langgraph_app.invoke(state)
    # Convert ObjectId in output
    output = convert_objectid(output)
    state.update(output)
    if output.get("message"):
        add_to_output_history(output["message"], "system " + ("success" if "found" in output["message"] or "saved" in output["message"] else "warning"))
    session["state"] = state
    session.modified = True
    return output

@app.route("/", methods=["GET", "POST"])
def index():
    initialize_session()
    state = session["state"]

    if request.method == "POST":
        if state["step"] == "username":
            if "send_username" in request.form:
                username = request.form.get("username", "").strip()
                if username:
                    add_to_output_history(f"Username: {username}")
                    state["username"] = username
                    output = run_graph(state)
                    if output["customer"]:
                        state["step"] = "laptop_select"
                    elif output["new_user"]:
                        state["step"] = "register"
                else:
                    add_to_output_history("Please enter a username.", "system error")
                session["state"] = state
                session.modified = True
                return redirect(url_for("index"))

        elif state["step"] == "register":
            if "register" in request.form:
                name = request.form.get("name", "").strip()
                laptop_name = request.form.get("laptop_name", "").strip()
                laptop_model = request.form.get("laptop_model", "").strip()
                cpu = request.form.get("cpu", "").strip()
                ram = request.form.get("ram", "").strip()
                storage = request.form.get("storage", "").strip()
                if all([name, laptop_name, laptop_model, cpu, ram, storage]):
                    customer = {
                        "username": state["username"],
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
                        # Convert ObjectId before storing
                        state["customer"] = convert_objectid(customer)
                        state["new_user"] = False
                        state["step"] = "laptop_select"
                        add_to_output_history(f"Registered: {name} with {laptop_name} ({laptop_model})")
                        add_to_output_history("Registration successful!", "system success")
                    else:
                        add_to_output_history("Failed to register. Try again.", "system error")
                else:
                    add_to_output_history("Please fill all fields.", "system error")
                session["state"] = state
                session.modified = True
                return redirect(url_for("index"))

        elif state["step"] == "laptop_select":
            if "add_laptop" in request.form and request.form.get("add_new_laptop"):
                new_laptop_name = request.form.get("new_laptop_name", "").strip()
                new_laptop_model = request.form.get("new_laptop_model", "").strip()
                new_cpu = request.form.get("new_cpu", "").strip()
                new_ram = request.form.get("new_ram", "").strip()
                new_storage = request.form.get("new_storage", "").strip()
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
                    customer = state["customer"]
                    customer["laptops"].append({"new_laptop": new_laptop})
                    if db.customers_collection.update_one(
                        {"username": customer["username"]},
                        {"$set": {"laptops": customer["laptops"]}}
                    ).modified_count:
                        # Convert ObjectId before storing
                        state["customer"] = convert_objectid(customer)
                        add_to_output_history(f"Added laptop: {new_laptop_name} ({new_laptop_model})")
                        add_to_output_history("New laptop added!", "system success")
                    else:
                        add_to_output_history("Failed to register. Try again.", "system error")
                else:
                    add_to_output_history("Please fill all fields.", "system error")
                session["state"] = state
                session.modified = True
                return redirect(url_for("index"))

            if "proceed" in request.form:
                selected_laptop = request.form.get("selected_laptop", "Select a laptop")
                laptops = state["customer"]["laptops"]
                laptop_options = [f"{laptop['name']} ({laptop['model']})" for laptop in laptops]
                if selected_laptop in laptop_options:
                    laptop_index = laptop_options.index(selected_laptop)
                    state["laptop_id"] = laptops[laptop_index]["laptop_id"]
                    state["laptop_details"] = convert_objectid(laptops[laptop_index])
                    state["step"] = "query_process"
                    add_to_output_history(f"Selected laptop: {selected_laptop}")
                    add_to_output_history("Laptop selected!", "system success")
                else:
                    add_to_output_history("Please select a laptop.", "system error")
                session["state"] = state
                session.modified = True
                return redirect(url_for("index"))

        elif state["step"] == "query_process":
            if "send_query" in request.form:
                query = request.form.get("query", "").strip()
                if query:
                    laptop = state["laptop_details"]
                    if laptop:
                        laptop_context = f" on {laptop['name']} ({laptop['model']}, {laptop['specifications']['cpu']}, {laptop['specifications']['ram']}, {laptop['specifications']['storage']})"
                        enhanced_query = f"{query}{laptop_context}"
                    else:
                        enhanced_query = query
                    add_to_output_history(f"Query: {query}")
                    state["query"] = enhanced_query
                    output = run_graph(state)
                    if output["result"].get("solution"):
                        add_to_output_history("Solution found!", "system success")
                        add_to_output_history(f"Solution: {output['result']['solution']}", "system info")
                        if output["result"].get("references"):
                            for ref in output["result"]["references"]:
                                add_to_output_history(f"Reference - Ticket ID: {ref['ticket_id']}, Query: {ref['query']}, Solution: {', '.join(ref['answers'])}", "system info")
                        state["step"] = "query_options"
                    else:
                        add_to_output_history("Your query has been noted. We will follow up soon.", "system info")
                        state["step"] = "query_options"
                else:
                    add_to_output_history("Please enter a query.", "system error")
                session["state"] = state
                session.modified = True
                return redirect(url_for("index"))

        elif state["step"] == "query_options":
            if "another_query" in request.form:
                state["step"] = "query_process"
                add_to_output_history("Ready to enter another query.", "system info")
                session["state"] = state
                session.modified = True
                return redirect(url_for("index"))
            if "exit" in request.form:
                session["state"] = {
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
                session.modified = True
                return redirect(url_for("index"))

    # Prepare data for template
    laptops = state["customer"]["laptops"] if state["customer"] else []
    laptop_options = [f"{laptop['name']} ({laptop['model']})" for laptop in laptops]
    add_new_laptop = request.form.get("add_new_laptop", "off") == "on" if request.method == "POST" else False

    return render_template(
        "base.html",
        step=state["step"],
        output_history=sorted(state["output_history"], key=lambda x: x["timestamp"]),
        laptop_options=laptop_options,
        add_new_laptop=add_new_laptop
    )

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)