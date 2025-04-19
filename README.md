# OmniLearn - AI Powered Teaching Assistant

OmniLearn is an advanced AI teaching assistant platform that transforms the learning experience through intelligent document analysis and interactive learning capabilities. The platform uses state-of-the-art RAG (Retrieval Augmented Generation) technology to provide precise, context-aware responses to user queries.

## Features

### 1. Document Analysis (PDF Support)
- Upload and analyze PDF documents
- Intelligent text chunking and embedding
- Context-aware question answering
- Session-based document management
- Drag-and-drop file upload interface

### 2. Conversational AI
- Context-aware responses using RAG
- Chat history management
- Real-time message streaming
- Session-based conversations
- Intelligent question reformulation

### 3. User Interface
- Modern, responsive design
- Dark mode interface
- Intuitive chat interface
- Real-time status updates
- Session management
- API key management with secure storage

### 4. Coming Soon Features
- GitHub Repository Learning
- Web Source Integration
- Video Content Analysis
- Interactive Learning Materials

## Technology Stack

### Frontend
- **Framework**: Express.js (serving as a middle-tier server or API gateway )
- **UI**: HTML5, CSS3, JavaScript
- **Libraries**:
  - axios (HTTP client)
  - multer (file upload handling)
  - cors (Cross-Origin Resource Sharing)
  - form-data (form data handling)

### Backend
- **Framework**: FastAPI (Python)
- **AI/ML Components**:
  - LangChain
  - Groq LLM Integration
  - HuggingFace Embeddings
  - ChromaDB (Vector Store)
- **Document Processing**:
  - PyPDF (PDF processing)
  - LangChain Text Splitters
  - Vector Embeddings

### Key Dependencies
- langchain_groq
- langchain_community
- langchain_huggingface
- fastapi
- uvicorn
- python-multipart
- chromadb

## Setup and Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/OmniLearn.git
cd OmniLearn
