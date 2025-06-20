# from flask import Flask, request, jsonify, render_template_string, redirect, url_for
# from pymongo import MongoClient
# from chatbot import TicketingChatbot
# import uuid
# import logging

# # Set up logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

# app = Flask(__name__)

# # MongoDB setup
# client = MongoClient("localhost", 27017)
# db = client["Ticketing_Platform"]
# customers_collection = db["Customers"]
# tickets_collection = db["tickets"]

# # Initialize chatbot
# try:
#     chatbot = TicketingChatbot()
#     logger.info("Chatbot initialized successfully")
# except Exception as e:
#     logger.error(f"Failed to initialize chatbot: {e}")
#     raise

# # HTML template with gradient design
# HTML_TEMPLATE = """
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>AI-Powered Ticketing Platform</title>
#     <script src="https://cdn.tailwindcss.com"></script>
#     <style>
#         body {
#             font-family: 'Inter', sans-serif;
#             margin: 0;
#             min-height: 100vh;
#             background: linear-gradient(135deg, #A3BFFA, #D2B4FC);
#             overflow: hidden;
#         }
#         .container {
#             display: flex;
#             height: 100vh;
#         }
#         .steps {
#             width: 250px;
#             background: linear-gradient(0deg, #A3BFFA, #B7C9FC);
#             padding: 20px;
#             box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
#             overflow-y: auto;
#         }
#         .step {
#             display: flex;
#             align-items: center;
#             padding: 10px;
#             margin-bottom: 10px;
#             border-radius: 8px;
#             transition: all 0.3s ease;
#             cursor: pointer;
#             background: rgba(255, 255, 255, 0.2);
#         }
#         .step.active {
#             background: linear-gradient(90deg, #6B46C1, #A3BFFA);
#             color: white;
#             transform: translateX(5px);
#         }
#         .step:hover {
#             background: rgba(255, 255, 255, 0.3);
#         }
#         .step.active:hover {
#             background: linear-gradient(90deg, #553C9A, #6B46C1);
#         }
#         .step-number {
#             width: 30px;
#             height: 30px;
#             background: rgba(255, 255, 255, 0.5);
#             color: #333;
#             border-radius: 50%;
#             display: flex;
#             align-items: center;
#             justify-content: center;
#             margin-right: 10px;
#             font-weight: bold;
#         }
#         .step.active .step-number {
#             background: #ffffff;
#             color: #6B46C1;
#         }
#         .chat-container {
#             flex: 1;
#             display: flex;
#             flex-direction: column;
#             padding: 20px;
#             background: linear-gradient(135deg, #D2B4FC, #E6CFFF);
#         }
#         .chat-header {
#             display: flex;
#             justify-content: space-between;
#             align-items: center;
#             margin-bottom: 20px;
#             background: rgba(255, 255, 255, 0.1);
#             padding: 10px;
#             border-radius: 8px;
#         }
#         #chatBox {
#             flex: 1;
#             overflow-y: auto;
#             border: 1px solid rgba(255, 255, 255, 0.2);
#             padding: 15px;
#             border-radius: 8px;
#             background: rgba(255, 255, 255, 0.05);
#             margin-bottom: 20px;
#             box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05);
#         }
#         #chatBox p {
#             margin: 10px 0;
#             padding: 10px;
#             border-radius: 8px;
#             animation: fadeIn 0.5s ease;
#         }
#         #chatBox p.user {
#             background: linear-gradient(90deg, #A3BFFA, #B7C9FC);
#             margin-left: 20%;
#             text-align: right;
#             color: #333;
#         }
#         #chatBox p.bot {
#             background: linear-gradient(90deg, #D2B4FC, #E6CFFF);
#             margin-right: 20%;
#             color: #333;
#         }
#         .ticket-result {
#             margin: 10px 0;
#             padding: 10px;
#             border: 1px solid rgba(255, 255, 255, 0.2);
#             border-radius: 5px;
#             background: rgba(255, 255, 255, 0.1);
#             color: #333;
#         }
#         #chatForm {
#             display: flex;
#             gap: 10px;
#         }
#         #userInput {
#             flex: 1;
#             padding: 10px;
#             border: 1px solid rgba(255, 255, 255, 0.3);
#             border-radius: 8px;
#             background: rgba(255, 255, 255, 0.2);
#             color: #333;
#             transition: border-color 0.3s ease, box-shadow 0.3s ease;
#         }
#         #userInput:focus {
#             outline: none;
#             border-color: #6B46C1;
#             box-shadow: 0 0 0 3px rgba(107, 70, 193, 0.2);
#         }
#         button {
#             padding: 10px 20px;
#             background: linear-gradient(90deg, #6B46C1, #A3BFFA);
#             color: white;
#             border: none;
#             border-radius: 8px;
#             cursor: pointer;
#             transition: background 0.3s ease, transform 0.2s ease;
#         }
#         button:hover {
#             background: linear-gradient(90deg, #553C9A, #8EACFF);
#             transform: translateY(-2px);
#         }
#         .login-container {
#             max-width: 400px;
#             margin: 100px auto;
#             padding: 20px;
#             background: rgba(255, 255, 255, 0.2);
#             border-radius: 12px;
#             box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
#             backdrop-filter: blur(5px);
#             animation: slideUp 0.5s ease;
#         }
#         .login-container h1 {
#             color: #333;
#         }
#         .login-container input {
#             background: rgba(255, 255, 255, 0.3);
#             color: #333;
#         }
#         .login-container button {
#             background: linear-gradient(90deg, #6B46C1, #A3BFFA);
#         }
#         .login-container button:hover {
#             background: linear-gradient(90deg, #553C9A, #8EACFF);
#         }
#         @keyframes fadeIn {
#             from { opacity: 0; transform: translateY(10px); }
#             to { opacity: 1; transform: translateY(0); }
#         }
#         @keyframes slideUp {
#             from { opacity: 0; transform: translateY(20px); }
#             to { opacity: 1; transform: translateY(0); }
#         }
#     </style>
# </head>
# <body>
#     {% if not username %}
#     <div class="login-container">
#         <h1 class="text-2xl font-bold mb-4 text-center">Login</h1>
#         <form id="loginForm" class="space-y-4">
#             <div>
#                 <label class="block text-sm font-medium text-gray-700">Username</label>
#                 <input type="text" id="username" name="username" class="mt-1 block w-full p-2 border border-gray-300 rounded-md focus:border-blue-500 focus:ring focus:ring-blue-200" placeholder="Enter username">
#             </div>
#             <button type="submit" class="w-full bg-blue-500 text-white p-2 rounded-md hover:bg-blue-600">Login</button>
#         </form>
#         <p id="message" class="mt-4 text-center text-red-500"></p>
#     </div>
#     {% else %}
#     <div class="container">
#         <div class="steps">
#             <h2 class="text-lg font-semibold mb-4 text-gray-800">Progress</h2>
#             <div class="step" data-step="login">
#                 <div class="step-number">1</div>
#                 <span>Login</span>
#             </div>
#             <div class="step" data-step="list-devices">
#                 <div class="step-number">2</div>
#                 <span>List Devices</span>
#             </div>
#             <div class="step" data-step="query-issue">
#                 <div class="step-number">3</div>
#                 <span>Query Issue</span>
#             </div>
            
#         </div>
#         <div class="chat-container">
#             <div class="chat-header">
#                 <h1 class="text-2xl font-bold text-gray-800">Chat with AI Platform</h1>
#                 <button id="logoutButton">Logout</button>
#             </div>
#             <p class="text-sm text-gray-600 mb-4">Logged in as: {{ username }}</p>
#             <div id="chatBox"></div>
#             <form id="chatForm">
#                 <input type="text" id="userInput" placeholder="Type your message..." autocomplete="off">
#                 <button type="submit">Send</button>
#             </form>
#         </div>
#     </div>
#     {% endif %}
#     <script>
#         // Login form submission
#         document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
#             e.preventDefault();
#             const username = document.getElementById('username').value;
#             const response = await fetch('/login', {
#                 method: 'POST',
#                 headers: {'Content-Type': 'application/json'},
#                 body: JSON.stringify({username})
#             });
#             const result = await response.json();
#             if (result.success) {
#                 window.location.href = '/?username=' + encodeURIComponent(result.username);
#             } else {
#                 document.getElementById('message').innerText = result.message;
#             }
#         });

#         // Logout button
#         document.getElementById('logoutButton')?.addEventListener('click', () => {
#             window.location.href = '/logout';
#         });

#         // Chat form submission
#         document.getElementById('chatForm')?.addEventListener('submit', async (e) => {
#             e.preventDefault();
#             const message = document.getElementById('userInput').value.trim();
#             if (!message) return;
#             const chatBox = document.getElementById('chatBox');
#             chatBox.innerHTML += `<p class="user"><strong>You:</strong> ${message}</p>`;
#             document.getElementById('userInput').value = '';
#             autoScroll(chatBox);

#             // Update step indicator
#             updateStepIndicator(message.toLowerCase());

#             const response = await fetch('/chat?username={{ username }}', {
#                 method: 'POST',
#                 headers: {'Content-Type': 'application/json'},
#                 body: JSON.stringify({message})
#             });
#             const result = await response.json();
#             chatBox.innerHTML += `<p class="bot"><strong>Bot:</strong> ${result.response}</p>`;
#             autoScroll(chatBox);
#         });

#         // Auto-scroll function
#         function autoScroll(element) {
#             element.scrollTo({ top: element.scrollHeight, behavior: 'smooth' });
#         }

#         // Update step indicator
#         function updateStepIndicator(message) {
#             const steps = document.querySelectorAll('.step');
#             steps.forEach(step => step.classList.remove('active'));
#             if (message.includes('list my') && (message.includes('laptop') || message.includes('device'))) {
#                 document.querySelector('[data-step="list-devices"]').classList.add('active');
#             } else if (message.includes('laptop') || message.includes('macbook') || message.includes('hp') || message.includes('dell')) {
#                 document.querySelector('[data-step="query-issue"]').classList.add('active');
#             } else if (message.includes('resolve') || message.includes('solution')) {
#                 document.querySelector('[data-step="resolve"]').classList.add('active');
#             } else {
#                 document.querySelector('[data-step="login"]').classList.add('active');
#             }
#         }

#         // Initialize step indicator
#         document.querySelector('[data-step="login"]').classList.add('active');
#     </script>
# </body>
# </html>
# """

# @app.route('/')
# def index():
#     username = request.args.get('username')
#     if username and customers_collection.find_one({"username": username}):
#         logger.info(f"User {username} accessed chat interface")
#         return render_template_string(HTML_TEMPLATE, username=username)
#     logger.info("No username provided, showing login page")
#     return render_template_string(HTML_TEMPLATE)

# @app.route('/login', methods=['POST'])
# def login():
#     try:
#         data = request.get_json()
#         username = data.get('username')
#         if not username:
#             logger.warning("Login attempted with empty username")
#             return jsonify({"success": False, "message": "Username is required"})

#         user = customers_collection.find_one({"username": username})
#         if user:
#             logger.info(f"User {username} logged in successfully")
#             return jsonify({"success": True, "username": username, "message": f"Welcome back, {username}!"})

#         new_username = f"user_{uuid.uuid4().hex[:8]}"
#         customer_id = f"CUST{str(uuid.uuid4())[:6]}"
#         customers_collection.insert_one({
#             "username": new_username,
#             "customer_id": customer_id,
#             "name": username,
#             "laptops": []
#         })
#         logger.info(f"Created new user with username {new_username}")
#         return jsonify({"success": True, "username": new_username, "message": f"New user created! Your username is {new_username}."})
#     except Exception as e:
#         logger.error(f"Error during login: {e}")
#         return jsonify({"success": False, "message": "An error occurred during login"})

# @app.route('/logout')
# def logout():
#     logger.info("User logged out")
#     return redirect(url_for('index'))

# @app.route('/chat', methods=['POST'])
# def chat():
#     try:
#         data = request.get_json()
#         message = data.get('message')
#         username = request.args.get('username', 'unknown')
#         if not message:
#             logger.warning(f"Empty message from user {username}")
#             return jsonify({"response": "Please enter a message"})
#         logger.info(f"Processing message from {username}: {message}")
#         response = chatbot.handle_message(username, message)
#         logger.info(f"Response to {username}: {response}")
#         return jsonify({"response": response})
#     except Exception as e:
#         logger.error(f"Error processing chat message: {e}")
#         return jsonify({"response": "An error occurred. Please try again."})

# if __name__ == '__main__':
#     logger.info("Starting Flask application")
#     app.run(debug=True)

##----------------------------------Final Code----------------------------------##
from flask import Flask, request, jsonify, render_template_string, redirect, url_for
from pymongo import MongoClient
from chatbot import TicketingChatbot
import uuid
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# MongoDB setup
client = MongoClient("localhost", 27017)
db = client["Ticketing_Platform"]
customers_collection = db["Customers"]
tickets_collection = db["tickets"]

# Initialize chatbot
try:
    chatbot = TicketingChatbot()
    logger.info("Chatbot initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize chatbot: {e}")
    raise

# HTML template with step indicator and full-screen chat
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI-Powered Ticketing Platform</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #f3f4f6, #e5e7eb);
            min-height: 100vh;
            margin: 0;
            overflow: hidden;
        }
        .container {
            display: flex;
            height: 100vh;
        }
        .steps {
            width: 250px;
            background: #ffffff;
            padding: 20px;
            box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
            overflow-y: auto;
        }
        .step {
            display: flex;
            align-items: center;
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 8px;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        .step.active {
            background: #3b82f6;
            color: white;
            transform: translateX(5px);
        }
        .step:hover {
            background: #e5e7eb;
        }
        .step.active:hover {
            background: #2563eb;
        }
        .step-number {
            width: 30px;
            height: 30px;
            background: #d1d5db;
            color: #333;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 10px;
            font-weight: bold;
        }
        .step.active .step-number {
            background: #ffffff;
            color: #3b82f6;
        }
        .chat-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            padding: 20px;
            background: #f9fafb;
        }
        .chat-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        #chatBox {
            flex: 1;
            overflow-y: auto;
            border: 1px solid #e5e7eb;
            padding: 15px;
            border-radius: 8px;
            background: #ffffff;
            margin-bottom: 20px;
            box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        #chatBox p {
            margin: 10px 0;
            padding: 10px;
            border-radius: 8px;
            animation: fadeIn 0.5s ease;
        }
        #chatBox p.user {
            background: #e0f2fe;
            margin-left: 20%;
            text-align: right;
        }
        #chatBox p.bot {
            background: #f3f4f6;
            margin-right: 20%;
        }
        .ticket-result {
            margin: 10px 0;
            padding: 10px;
            border: 1px solid #e5e7eb;
            border-radius: 5px;
            background: #fafafa;
        }
        #chatForm {
            display: flex;
            gap: 10px;
        }
        #userInput {
            flex: 1;
            padding: 10px;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            transition: border-color 0.3s ease;
        }
        #userInput:focus {
            outline: none;
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
        button {
            padding: 10px 20px;
            background: #3b82f6;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: background 0.3s ease, transform 0.2s ease;
        }
        button:hover {
            background: #2563eb;
            transform: translateY(-2px);
        }
        .login-container {
            max-width: 400px;
            margin: auto;
            padding: 20px;
            background: #ffffff;
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            animation: slideUp 0.5s ease;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body>
    {% if not username %}
    <div class="login-container">
        <h1 class="text-2xl font-bold mb-4 text-center text-gray-800">Login</h1>
        <form id="loginForm" class="space-y-4">
            <div>
                <label class="block text-sm font-medium text-gray-700">Username</label>
                <input type="text" id="username" name="username" class="mt-1 block w-full p-2 border border-gray-300 rounded-md focus:border-blue-500 focus:ring focus:ring-blue-200" placeholder="Enter username">
            </div>
            <button type="submit" class="w-full bg-blue-500 text-white p-2 rounded-md hover:bg-blue-600">Login</button>
        </form>
        <p id="message" class="mt-4 text-center text-red-500"></p>
    </div>
    {% else %}
    <div class="container">
        <div class="steps">
            <h2 class="text-lg font-semibold mb-4">Progress</h2>
            <div class="step" data-step="login">
                <div class="step-number">1</div>
                <span>Login</span>
            </div>
            <div class="step" data-step="list-devices">
                <div class="step-number">2</div>
                <span>List Devices</span>
            </div>
            <div class="step" data-step="query-issue">
                <div class="step-number">3</div>
                <span>Query Issue</span>
            </div>
            <div class="step" data-step="resolve">
                <div class="step-number">4</div>
                <span>Resolve Issue</span>
            </div>
        </div>
        <div class="chat-container">
            <div class="chat-header">
                <h1 class="text-2xl font-bold text-gray-800">Chat with AI Platform</h1>
                <button id="logoutButton" class="bg-red-500 hover:bg-red-600">Logout</button>
            </div>
            <p class="text-sm text-gray-600 mb-4">Logged in as: {{ username }}</p>
            <div id="chatBox"></div>
            <form id="chatForm">
                <input type="text" id="userInput" placeholder="Type your message..." autocomplete="off">
                <button type="submit">Send</button>
            </form>
        </div>
    </div>
    {% endif %}
    <script>
        // Login form submission
        document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const response = await fetch('/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username})
            });
            const result = await response.json();
            if (result.success) {
                window.location.href = '/?username=' + encodeURIComponent(result.username);
            } else {
                document.getElementById('message').innerText = result.message;
            }
        });

        // Logout button
        document.getElementById('logoutButton')?.addEventListener('click', () => {
            window.location.href = '/logout';
        });

        // Chat form submission
        document.getElementById('chatForm')?.addEventListener('submit', async (e) => {
            e.preventDefault();
            const message = document.getElementById('userInput').value.trim();
            if (!message) return;
            const chatBox = document.getElementById('chatBox');
            chatBox.innerHTML += `<p class="user"><strong>You:</strong> ${message}</p>`;
            document.getElementById('userInput').value = '';
            autoScroll(chatBox);

            // Update step indicator
            updateStepIndicator(message.toLowerCase());

            const response = await fetch('/chat?username={{ username }}', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message})
            });
            const result = await response.json();
            chatBox.innerHTML += `<p class="bot"><strong>Bot:</strong> ${result.response}</p>`;
            autoScroll(chatBox);
        });

        // Auto-scroll function
        function autoScroll(element) {
            element.scrollTo({ top: element.scrollHeight, behavior: 'smooth' });
        }

        // Update step indicator
        function updateStepIndicator(message) {
            const steps = document.querySelectorAll('.step');
            steps.forEach(step => step.classList.remove('active'));
            if (message.includes('list my') && (message.includes('laptop') || message.includes('device'))) {
                document.querySelector('[data-step="list-devices"]').classList.add('active');
            } else if (message.includes('laptop') || message.includes('macbook') || message.includes('hp') || message.includes('dell')) {
                document.querySelector('[data-step="query-issue"]').classList.add('active');
            } else {
                document.querySelector('[data-step="login"]').classList.add('active');
            }
        }

        // Initialize step indicator
        document.querySelector('[data-step="login"]').classList.add('active');
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    username = request.args.get('username')
    if username and customers_collection.find_one({"username": username}):
        logger.info(f"User {username} accessed chat interface")
        return render_template_string(HTML_TEMPLATE, username=username)
    logger.info("No username provided, showing login page")
    return render_template_string(HTML_TEMPLATE)

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        if not username:
            logger.warning("Login attempted with empty username")
            return jsonify({"success": False, "message": "Username is required"})

        user = customers_collection.find_one({"username": username})
        if user:
            logger.info(f"User {username} logged in successfully")
            return jsonify({"success": True, "username": username, "message": f"Welcome back, {username}!"})

        new_username = f"user_{uuid.uuid4().hex[:8]}"
        customer_id = f"CUST{str(uuid.uuid4())[:6]}"
        customers_collection.insert_one({
            "username": new_username,
            "customer_id": customer_id,
            "name": username,
            "laptops": []
        })
        logger.info(f"Created new user with username {new_username}")
        return jsonify({"success": True, "username": new_username, "message": f"New user created! Your username is {new_username}."})
    except Exception as e:
        logger.error(f"Error during login: {e}")
        return jsonify({"success": False, "message": "An error occurred during login"})

@app.route('/logout')
def logout():
    logger.info("User logged out")
    return redirect(url_for('index'))

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message')
        username = request.args.get('username', 'unknown')
        if not message:
            logger.warning(f"Empty message from user {username}")
            return jsonify({"response": "Please enter a message"})
        logger.info(f"Processing message from {username}: {message}")
        response = chatbot.handle_message(username, message)
        logger.info(f"Response to {username}: {response}")
        return jsonify({"response": response})
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        return jsonify({"response": "An error occurred. Please try again."})

if __name__ == '__main__':
    logger.info("Starting Flask application")
    app.run(debug=True)