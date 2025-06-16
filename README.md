# AI-Powered Ticketing Platform Documentation

## Project Overview

**Title**: AI-Powered Ticketing Platform for Machine-Related Issues  
**Objective**: Develop an AI-driven platform to handle machine-related issues via a chatbot interface, leveraging historical ticket data for resolutions, retrieving user and machine details from a database, and creating new tickets when needed.  
**Version**: 1.0  
**Date**: June 16, 2025

### Key Features
1. **User Authentication**: Users provide username and ID to access their profile and machine details.
2. **Machine Selection**: Users select a machine from a list of associated machines retrieved from the database.
3. **RAG-Based Resolution**: A Retrieval-Augmented Generation (RAG) system uses historical ticket data to suggest resolutions or generates new tickets for unresolved issues.
4. **Ticket Management**: Creates and stores new tickets with resolutions for future use.
5. **User Interface**: A Streamlit-based chatbot interface for seamless interaction.
6. **Agent Orchestration**: LangGraph manages multiple AI agents for authentication, machine retrieval, RAG processing, and ticket management.

### Tech Stack
- **Programming Language**: Python
- **AI Model**: Gemini 1.5 Flash (free tier, used for NLP tasks)
- **RAG Framework**: LangChain (for retrieval, embedding, and vector store)
- **Vector Store**: FAISS (lightweight similarity search for ticket data)
- **Database**: MongoDB (separate collections for customers and tickets)
- **UI Framework**: Streamlit (chatbot interface)
- **Agent Orchestration**: LangGraph (multi-agent workflows)

### Conflict Resolutions
1. **Ambiguity in Machine Selection**:
   - *Issue*: Users with multiple machines may face ambiguity in selecting the correct one.
   - *Solution*: Display a numbered list of machines in the chatbot UI, requiring users to select a machine by number or name before proceeding.
2. **RAG Data Quality**:
   - *Issue*: RAG effectiveness depends on well-structured historical data.
   - *Solution*: Use JSON-formatted ticket data with clear fields for problem, machine, and resolution (see dummy data example).
3. **Database Scalability**:
   - *Issue*: MongoDB must handle growing customer and ticket data efficiently.
   - *Solution*: Design separate collections (`customers` and `tickets`) with proper indexing on `username`, `customer_id`, and `machine_id`.
4. **Gemini 1.5 Flash Dependency**:
   - *Issue*: Potential limitations with Gemini 1.5 Flash availability.
   - *Solution*: Confirmed free tier usage ensures no issues; Gemini’s speed supports fast responses.
5. **LangGraph Complexity**:
   - *Issue*: Orchestrating multiple agents with LangGraph may be complex.
   - *Solution*: Mandatory use of LangGraph with clearly defined agent roles to streamline workflows.

## System Architecture

### Components
1. **Streamlit UI**: Frontend for user interaction, displaying chatbot conversations and machine selection options.
2. **Authentication Agent**: Validates user credentials (username, ID) against MongoDB.
3. **Machine Retrieval Agent**: Fetches user’s machine list or adds new machines.
4. **RAG Agent**: Retrieves similar past tickets using LangChain and FAISS; generates responses via Gemini 1.5 Flash if needed.
5. **Ticket Management Agent**: Creates new tickets for unresolved issues and stores resolutions.
6. **MongoDB**: Stores `customers` (user profiles, machines) and `tickets` (historical queries, resolutions).
7. **FAISS Vector Store**: Stores ticket embeddings for RAG retrieval.

### Workflow
1. User inputs username and ID via Streamlit chatbot.
2. Authentication Agent validates credentials and retrieves customer data.
3. Machine Retrieval Agent lists user’s machines; user selects a machine by number.
4. User describes the issue; RAG Agent searches historical tickets for similar issues.
5. If a match is found, the resolution is sent to the user. If not, the Ticket Management Agent creates a new ticket.
6. After resolution (manual or AI-generated), the ticket is stored in MongoDB and FAISS for future use.

## Setup Instructions

### Prerequisites
- Python 3.10+
- MongoDB (local or cloud instance)
- Gemini 1.5 Flash API key (free tier)
- Git (for repository cloning)

### Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repo/ticketing-platform.git
   cd ticketing-platform
   ```
2. **Set Up Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install streamlit langchain pymongo faiss-cpu google-generativeai langgraph
   ```
4. **Configure Environment Variables**:
   Create a `.env` file:
   ```plaintext
   MONGODB_URI=mongodb://localhost:27017/ticketing_platform
   GEMINI_API_KEY=your_gemini_api_key
   ```
5. **Set Up MongoDB**:
   - Start MongoDB server.
   - Create database `ticketing_platform` with collections `customers` and `tickets`.
   - Import dummy data (see below):
     ```bash
     mongoimport --db ticketing_platform --collection customers --file dummy_data.json --jsonArray --arrayName customers
     mongoimport --db ticketing_platform --collection tickets --file dummy_data.json --jsonArray --arrayName tickets
     ```
6. **Initialize FAISS**:
   - Run a script to embed historical tickets into FAISS (provided in repository).

### Running the Application
```bash
streamlit run app.py
```
Access the UI at `http://localhost:8501`.

## Dummy Data

The following JSON provides sample data for testing:

```json
{
  "customers": [
    {
      "username": "john_doe",
      "customer_id": "CUST001",
      "name": "John Doe",
      "machines": [
        {"machine_id": "M001", "type": "CNC Lathe", "model": "XYZ-100"},
        {"machine_id": "M002", "type": "3D Printer", "model": "Prusa MK3"}
      ]
    },
    {
      "username": "jane_smith",
      "customer_id": "CUST002",
      "name": "Jane Smith",
      "machines": [
        {"machine_id": "M003", "type": "Milling Machine", "model": "Haas VF-2"}
      ]
    }
  ],
  "tickets": [
    {
      "ticket_id": "TICK001",
      "customer_id": "CUST001",
      "machine_id": "M001",
      "problem": "CNC Lathe spindle not rotating",
      "resolution": "Check spindle motor connections and reset control panel.",
      "timestamp": "2025-01-10T10:00:00Z"
    },
    {
      "ticket_id": "TICK002",
      "customer_id": "CUST001",
      "machine_id": "M002",
      "problem": "3D Printer extruder jammed",
      "resolution": "Clear nozzle with a 0.4mm needle and recalibrate filament feed.",
      "timestamp": "2025-02-15T14:30:00Z"
    },
    {
      "ticket_id": "TICK003",
      "customer_id": "CUST002",
      "machine_id": "M003",
      "problem": "Milling Machine tool change error",
      "resolution": "Inspect tool changer alignment and update firmware.",
      "timestamp": "2025-03-20T09:15:00Z"
    }
  ]
}
```

## Usage Guide

### For Users
1. Open the Streamlit app in your browser.
2. Enter your username and customer ID.
3. Select a machine from the listed options (e.g., by entering the number).
4. Describe the machine issue in the chatbot.
5. Receive a resolution (if available) or confirmation of a new ticket creation.
6. Follow any provided instructions to resolve the issue.

### For Developers
- **Directory Structure**:
  ```
  ticketing-platform/
  ├── app.py               # Streamlit main app
  ├── agents/             # LangGraph agent scripts
  ├── rag/                # RAG pipeline (LangChain, FAISS)
  ├── db/                 # MongoDB connection and queries
  ├── dummy_data.json     # Sample data
  ├── .env                # Environment variables
  └── README.md           # Project overview
  ```
- **Extending Agents**: Add new LangGraph agents in the `agents/` directory with clear input/output schemas.
- **RAG Tuning**: Adjust embedding models or similarity thresholds in `rag/` for better retrieval accuracy.
- **Database Schema**:
  - `customers`: `{username, customer_id, name, machines: [{machine_id, type, model}]}`
  - `tickets`: `{ticket_id, customer_id, machine_id, problem, resolution, timestamp}`

## Testing

### Test Cases
1. **Authentication**: Verify correct/incorrect username-ID pairs.
2. **Machine Selection**: Ensure users can select a machine from multiple options.
3. **RAG Retrieval**: Test retrieval of existing tickets with similar issues.
4. **Ticket Creation**: Confirm new tickets are stored correctly.
5. **UI Responsiveness**: Check Streamlit UI on different devices.

### Running Tests
```bash
pytest tests/
```

## Deployment

### Local Deployment
Run `streamlit run app.py` for local testing.

### Cloud Deployment
1. Use Streamlit Cloud:
   - Push code to GitHub.
   - Connect repository to Streamlit Cloud.
   - Configure `.env` variables in the cloud dashboard.
2. Alternative: Deploy on a VPS (e.g., AWS EC2) with Docker:
   ```dockerfile
   FROM python:3.10
   WORKDIR /app
   COPY . .
   RUN pip install -r requirements.txt
   CMD ["streamlit", "run", "app.py"]
   ```

## Maintenance

- **Monitoring**: Log user interactions and errors to `logs/` directory.
- **Updates**: Regularly update ticket embeddings in FAISS as new tickets are added.
- **Backups**: Schedule MongoDB backups weekly.
- **Security**: Rotate Gemini API keys and MongoDB credentials periodically.

## Future Enhancements
- Add multi-language support for the chatbot.
- Integrate real-time notifications for ticket updates.
- Implement a feedback system for users to rate resolutions.
- Scale FAISS to Pinecone for larger datasets.

## Contact
For support, contact the development team at `support@ticketingplatform.com`.
