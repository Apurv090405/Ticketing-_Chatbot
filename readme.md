# 🎉 Laptop Support Chatbot

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.4+-brightgreen.svg)](https://mongodb.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Latest-orange.svg)](https://langchain.com)

Welcome to the **Laptop Support Chatbot**, a Flask-based web application that offers intelligent laptop troubleshooting using a Retrieval-Augmented Generation (RAG) system, LangGraph, MongoDB, and the Gemini API.

---

## 📖 Table of Contents

- [Features](#features)
- [System Architecture](#system-architecture)
- [Folder Structure](#folder-structure)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [How to Run](#how-to-run)
- [Demo Screenshots](#demo-screenshots)
- [Acknowledgment](#acknowledgment)

---

## 🎯 Features

- **Smart Chat Interface**: A dynamic and user-friendly UI for login, chat, and device management.
- **Intent Recognition**: Utilizes the Gemini API to classify user messages into intents like `greeting`, `query`, `list_devices`, `selection`, `chat_history`, and `identity` for more accurate responses.
- **RAG-Powered Solutions**: Provides step-by-step troubleshooting solutions by retrieving information from a knowledge base of past tickets. The RAG system uses cosine similarity to find the most relevant tickets and generates contextual answers.
- **Stateful Conversations**: Employs LangGraph to manage the conversation flow as a state machine, allowing for more complex and natural interactions.
- **MongoDB Integration**: Manages user data, tickets, and chat history using MongoDB.
- **Device Management**: Allows users to list their registered laptops for targeted support.
- **Scalable Design**: The modular architecture makes it easy to extend and improve the chatbot's capabilities.

---

## 🖼️ System Architecture

The application is composed of three main components: a Flask web server, a chatbot, and a RAG system.

![System Architecture   System Flow drawio](https://github.com/user-attachments/assets/85276e82-783a-4d2a-9314-6f2e084ea73f)

The system flow is as follows:
1.  The user interacts with the web interface, which is served by a Flask application (`app.py`).
2.  User messages are sent to the `TicketingChatbot` (`chatbot.py`), which manages the conversation state using LangGraph.
3.  The chatbot classifies the user's intent and, if it's a query, passes it to the `RAGSystem` (`rag.py`).
4.  The RAG system retrieves relevant information from the MongoDB `tickets` collection and uses the Gemini API to generate a response.
5.  The response is sent back to the user through the web interface.

---

## 📁 Folder Structure

```
.
├── app.py                  # Main Flask application
├── chatbot.py              # Chatbot logic using LangGraph
├── rag.py                  # RAG system for information retrieval
├── ticket_embeddings.json  # Cached embeddings for tickets
├── requirements.txt        # Python dependencies
├── readme.md               # This file
├── database_json_file/
│   ├── Ticketing_Platform.Customers.json
│   ├── Ticketing_Platform.tickets.json
│   └── Ticketing_Platform.chat_history.json
└── ...
```

---

## 💻 Technologies Used

-   **Backend:** Python, Flask
-   **AI & Machine Learning:**
    -   Google Gemini API (for intent classification, response generation, and embeddings)
    -   LangGraph (for managing conversation state)
    -   Scikit-learn (for cosine similarity)
-   **Database:** MongoDB
-   **Frontend:** HTML, CSS, JavaScript

---

## 🛠️ Installation

### Prerequisites

-   Python 3.8+
-   MongoDB

### 1. Clone the Repository

```bash
git clone https://github.com/Apurv090405/Ticketing-_Chatbot
cd Ticketing-_Chatbot
```

### 2. Set Up a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the root of the project and add your Gemini API key:

```
GEMINI_API_KEY="your-api-key-here"
```

### 5. Set Up MongoDB

1.  Make sure your MongoDB server is running.
2.  Create a database named `Ticketing_Platform`.
3.  Import the demo data from the `database_json_file` directory into your `Ticketing_Platform` database. You can use a tool like `mongoimport` or the MongoDB Compass UI.

    For example, using `mongoimport`:
    ```bash
    mongoimport --uri "mongodb://localhost:27017/Ticketing_Platform" --collection Customers --file database_json_file/Ticketing_Platform.Customers.json --jsonArray
    mongoimport --uri "mongodb://localhost:27017/Ticketing_Platform" --collection tickets --file database_json_file/Ticketing_Platform.tickets.json --jsonArray
    mongoimport --uri "mongodb://localhost:27017/Ticketing_Platform" --collection chat_history --file database_json_file/Ticketing_Platform.chat_history.json --jsonArray
    ```

---

## ▶️ How to Run

1.  Make sure your MongoDB server is running.
2.  Run the Flask application:

    ```bash
    python app.py
    ```

3.  Open your web browser and go to `http://127.0.0.1:5000`.

---

## 📸 Demo Screenshots

### Login Screen
![Recording 2025-07-02 125726](https://github.com/user-attachments/assets/6842c731-ce29-400e-9bbd-484ff60fdc63)


### Chat Interface
![Recording 2025-07-02 130104](https://github.com/user-attachments/assets/a76ef80b-6c6d-4d53-bfe1-9202a24a5108)

---
## 🙏 Acknowledgment

We extend our heartfelt gratitude to **Codiste** for initiating and supporting this project. We also appreciate the open-source community and Google Cloud for providing the Gemini API, which powers our AI capabilities.

---
