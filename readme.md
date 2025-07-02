# 🎉 Laptop Support Chatbot

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.4+-brightgreen.svg)](https://mongodb.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Latest-orange.svg)](https://langchain.com)

Welcome to the **Laptop Support Chatbot**, a live project by Codiste! This Flask-based web application offers intelligent laptop troubleshooting using a Retrieval-Augmented Generation (RAG) system, MongoDB, and the Gemini API. Let’s dive in! 🚀

---

## 📖 Table of Contents

- [Features](#features)
- [Folder Structure](#folder-structure)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Demo Database](#demo-database)
- [Demo Screenshots](#demo-screenshots)
- [Ending Message](#ending-message)
- [Acknowledgment](#acknowledgment)
- [Contact Information](#contact-information)

---

## 🎯 Features

- **Smart Chat Interface**: Engage with a user-friendly UI for login, chat, and device management. 🖱️
- **Intent Recognition**: Classifies greetings, queries, and device selections with Gemini API. 🧠
- **RAG Solutions**: Provides step-by-step troubleshooting using past ticket data. 📊
- **MongoDB Storage**: Manages user data, tickets, and chat history securely. 💾
- **Device Support**: Lists and selects registered laptops for targeted support. 💻
- **Scalable Design**: Modular architecture for easy updates and growth. 🛠️

---

## 📁 Folder Structure

```
laptop-support-chatbot/
├── app.py                    # Flask web server for routes and UI
├── chatbot.py                # Chatbot logic with LangGraph state machine
├── rag.py                    # RAG system for query processing
├── ticket_embeddings.json    # Cached embeddings for efficient retrieval
├── database_json_file        # MongoDB database collection json file
|   ├── Customers
|   ├── tickets
|   ├── chat_history
```

---

## 🖼️ System Architecture

![System Architecture   System Flow drawio](https://github.com/user-attachments/assets/85276e82-783a-4d2a-9314-6f2e084ea73f)

---

## 🛠️ Installation

### Clone the Repository
```bash
git clone https://github.com/Apurv090405/Ticketing-_Chatbot
cd laptop-support-chatbot
```

### Set Up Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install Libraries
```bash
pip install Flask==2.3.2
pip install pymongo==4.6.3
pip install google-generativeai==0.5.4
pip install numpy==1.26.4
pip install scikit-learn==1.4.2
pip install langchain-mongodb==0.1.6
pip install python-dotenv==1.0.1
```

### Set Up Gemini API Key
- Get a key from [Google Cloud](https://cloud.google.com).
- Set the environment variable:
  ```bash
  export GEMINI_API_KEY="your-api-key-here"  # On Windows: set GEMINI_API_KEY=your-api-key-here
  ```

---

## 🗃️ Demo Database

![Screenshot 2025-07-02 131922](https://github.com/user-attachments/assets/91e54c6d-f06d-4859-ba46-0186cc09a6bb)
all json file was there in database folder.

---

## 📸 Demo Screenshots

### Login Screen
![Recording 2025-07-02 125726](https://github.com/user-attachments/assets/6842c731-ce29-400e-9bbd-484ff60fdc63)


### Chat Interface
![Recording 2025-07-02 130104](https://github.com/user-attachments/assets/a76ef80b-6c6d-4d53-bfe1-9202a24a5108)

---

## 🌟 Ending Message

Thank you for exploring the Laptop Support Chatbot! A big shoutout to **Codiste** for bringing this live project to life. Let’s keep innovating together! 💻🎉

--- 
## 🙏 Acknowledgment

We extend our heartfelt gratitude to **Codiste** for initiating and supporting this live project. Special thanks to the development team, including [Your Name/Team], for their dedication and expertise. We also appreciate the open-source community and Google Cloud for providing the Gemini API, which powers our AI capabilities.

---

## 📧 Contact Information

- **Email**: apurvchudasama.tech@gmail.com
- **Website**: https://me.apurvchudasama.tech
- **GitHub**: https://github.com/Apurv090405/Ticketing-_Chatbot
- **Linkedin**: https://linkedin.com/apurv-chudasama
