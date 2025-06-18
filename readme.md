# 🎫 AI Ticketing Platform - Intelligent Machine Support Chatbot

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.4+-brightgreen.svg)](https://mongodb.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Latest-orange.svg)](https://langchain.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> An intelligent AI-powered ticketing platform designed to provide automated support for machine-related issues through an advanced chatbot interface. Built with cutting-edge technologies including RAG (Retrieval-Augmented Generation), vector embeddings, and multi-agent workflows.

![Platform Screenshot](https://via.placeholder.com/800x400/c3dafe/1e293b?text=AI+Ticketing+Platform)

## 🌟 Features

### 🤖 **Intelligent AI Chatbot**
- **RAG-powered responses** using Google Gemini AI and FAISS vector store
- **Context-aware solutions** based on historical ticket data
- **Web search integration** for comprehensive problem-solving
- **Multi-agent workflow** using LangGraph for structured processing

### 👥 **User Management**
- **Seamless authentication** with automatic user registration
- **Multi-device support** - users can register multiple laptops
- **Persistent session management** with secure Flask sessions
- **Customer profile management** with device tracking

### 🎨 **Modern User Interface**
- **Beautiful gradient design** with responsive Bootstrap layout
- **Real-time chat interface** with message history
- **Interactive forms** for user registration and device management
- **Professional styling** with smooth animations and transitions

### 🗄️ **Advanced Data Management**
- **MongoDB integration** for scalable data storage
- **Vector embeddings** for semantic similarity search
- **Ticket lifecycle management** with automatic ID generation
- **JSON backup system** for data redundancy

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Flask Web     │    │   LangGraph      │    │   MongoDB       │
│   Application   │────│   Workflow       │────│   Database      │
│                 │    │                  │    │                 │
│ • Routes        │    │ • Auth Agent     │    │ • Customers     │
│ • Templates     │    │ • Query Agent    │    │ • Tickets       │
│ • Session Mgmt  │    │ • Solution Agent │    │ • Vector Store  │
└─────────────────┘    │ • Ticket Agent   │    └─────────────────┘
                       └──────────────────┘
                                │
                       ┌──────────────────┐
                       │   RAG Pipeline   │
                       │                  │
                       │ • FAISS Vector   │
                       │ • Gemini AI      │
                       │ • Web Search     │
                       └──────────────────┘
```

### 🔄 **Multi-Agent Workflow**

The platform uses LangGraph to orchestrate a sophisticated multi-agent system:

1. **Auth Agent** - Handles user authentication and registration
2. **Query Agent** - Processes user queries and searches vector store
3. **Solution Agent** - Generates AI-powered solutions using RAG
4. **Ticket Agent** - Manages ticket creation and storage

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- MongoDB 4.4 or higher
- Google Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Apurv090405/Ticketing-_Chatbot.git
   cd Ticketing-_Chatbot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install flask pymongo python-dotenv
   pip install langchain langchain-google-genai langchain-community
   pip install langgraph faiss-cpu google-generativeai
   pip install requests uuid
   ```

4. **Set up environment variables**
   ```bash
   # Create .env file
   echo "GEMINI_API_KEY=your_gemini_api_key_here" > .env
   ```

5. **Start MongoDB**
   ```bash
   # Make sure MongoDB is running on localhost:27017
   mongod
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Access the platform**
   Open your browser and navigate to `http://localhost:5000`

## 📁 Project Structure

```
Ticketing-_Chatbot/
├── 📁 agents/                 # AI agents for workflow processing
│   ├── auth_agent.py         # User authentication logic
│   ├── query_agent.py        # Query processing and vector search
│   ├── rag.py               # RAG pipeline implementation
│   ├── solution_agent.py    # AI solution generation
│   └── ticket_agent.py      # Ticket management
├── 📁 templates/             # HTML templates
│   └── base.html            # Main UI template with gradient design
├── 📁 _ALL_VERSIONS/         # Project evolution history
│   ├── Version-1_Streamlit/ # Original Streamlit implementation
│   ├── Version-2_Flask_app/ # Flask migration
│   └── Version-3_Flask-improved-version/ # Enhanced version
├── app.py                   # Main Flask application
├── db.py                    # MongoDB database operations
├── graph.py                 # LangGraph workflow definition
└── README.md               # This file
```

## 🔧 Configuration

### MongoDB Setup

The application expects MongoDB to be running on `localhost:27017` with the following collections:

- `Ticketing_Platform.Customers` - User and device information
- `Ticketing_Platform.tickets` - Support tickets and solutions

### Google Gemini API

1. Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Add it to your `.env` file:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

## 💡 Usage

### For End Users

1. **Registration**
   - Choose "New User" on the homepage
   - Enter your full name and laptop details
   - System generates a unique username

2. **Existing Users**
   - Enter your username to access the platform
   - Select your device for context-aware support

3. **Getting Support**
   - Describe your machine-related issue
   - Receive AI-generated solutions based on historical data
   - Automatic ticket creation for tracking

### For Developers

The platform is designed for easy extension:

```python
# Adding new agents to the workflow
from agents.custom_agent import custom_agent

workflow.add_node("custom_process", custom_agent)
workflow.add_edge("query_process", "custom_process")
```

## 🧪 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET/POST | Main application interface |
| Database operations handled internally through `db.py` |

## 🎯 Key Technologies

- **Flask** - Lightweight web framework
- **LangGraph** - Advanced workflow orchestration
- **Google Gemini AI** - Large language model for solution generation
- **FAISS** - Vector similarity search
- **MongoDB** - Document-based database
- **Bootstrap 5** - Responsive UI framework

## 📈 Performance Features

- **Vector-based similarity search** for fast ticket matching
- **Efficient MongoDB queries** with proper indexing
- **Session-based state management** for responsive user experience
- **Asynchronous AI processing** with graceful error handling

## 🔒 Security

- Secure session management with Flask's built-in session handling
- Environment variable protection for API keys
- Input validation and sanitization
- MongoDB connection security

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [LangChain](https://langchain.com) for the RAG framework
- [Google AI](https://ai.google.dev) for Gemini API
- [MongoDB](https://mongodb.com) for database solutions
- [Flask](https://flask.palletsprojects.com) community

## 📞 Support

If you encounter any issues or have questions:

- 📧 **Email**: [your-email@example.com]
- 🐛 **Issues**: [GitHub Issues](https://github.com/Apurv090405/Ticketing-_Chatbot/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/Apurv090405/Ticketing-_Chatbot/discussions)

---

<div align="center">

**⭐ Star this repository if you find it helpful!**

Made with ❤️ by [Apurv090405](https://github.com/Apurv090405)

</div>
