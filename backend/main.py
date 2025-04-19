from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
import time

from utils.embeddings import get_embeddings
from utils.logger import setup_logger
from rag.pdf_bot import PDFBot
from rag.github_rag import GitHubRAGBot

# Set up logger
logger = setup_logger(__name__)

# Load environment variables
load_dotenv()
logger.info("Environment variables loaded")

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("CORS middleware configured")

# Initialize RAG bots
try:
    pdf_bot = PDFBot(get_embeddings())
    github_bot = GitHubRAGBot(get_embeddings())
    logger.info("RAG bots initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize RAG bots: {str(e)}")
    raise

class ChatInput(BaseModel):     # using the pydantic basemodel to make a bucker
    session_id: str
    message: str
    groq_api_key: str

class ChatResponse(BaseModel):
    answer: str
    chat_history: List[Dict[str, str]]

class GitHubInput(BaseModel):
    url: str
    session_id: str

@app.post("/upload")
async def upload_files(
    files: List[UploadFile] = File(...),
    session_id: str = Form(...)
):
    logger.info(f"File upload request received for session: {session_id}")
    try:
        if not files:
            logger.warning("No files provided in upload request")
            raise HTTPException(status_code=400, detail="No files provided")

        file_contents = []
        for uploaded_file in files:
            logger.debug(f"Processing file: {uploaded_file.filename}")
            if not uploaded_file.filename.lower().endswith('.pdf'):
                logger.warning(f"Invalid file type attempted: {uploaded_file.filename}")
                raise HTTPException(status_code=400, detail="Only PDF files are allowed")
            content = await uploaded_file.read()
            file_contents.append(content)

        result = await pdf_bot.process_pdf(file_contents, session_id)
        logger.info(f"Successfully processed {len(files)} files for session {session_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error in upload_files: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
async def chat(chat_input: ChatInput):
    logger.info(f"Chat request received for session: {chat_input.session_id}")
    try:
        llm = ChatGroq(
            groq_api_key=chat_input.groq_api_key, 
            model_name="llama-3.3-70b-versatile"
        )
        logger.debug("LLM initialized successfully")
        
        answer, history = await pdf_bot.get_response(
            chat_input.session_id,
            chat_input.message,
            llm
        )
        logger.debug(f"Response generated for session {chat_input.session_id}")
        
        return ChatResponse(
            answer=answer,
            chat_history=history
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/github/process")
async def process_github(github_input: GitHubInput):
    logger.info(f"GitHub processing request received - URL: {github_input.url}, Session: {github_input.session_id}")
    try:
        # Log input validation
        logger.debug("Validating input parameters...")
        if not github_input.url:
            logger.warning("Empty URL provided")
            raise HTTPException(status_code=400, detail="URL cannot be empty")
        if not github_input.session_id:
            logger.warning("Empty session ID provided")
            raise HTTPException(status_code=400, detail="Session ID cannot be empty")

        # Log processing attempt
        logger.info(f"Starting repository processing - URL: {github_input.url}")
        start_time = time.time()
        
        result = await github_bot.process_repository(
            url=github_input.url,
            session_id=github_input.session_id
        )
        
        processing_time = time.time() - start_time
        logger.info(f"Repository processed successfully in {processing_time:.2f}s")
        return result

    except ValueError as ve:
        error_message = f"Invalid input: {str(ve)}"
        logger.error(error_message)
        raise HTTPException(status_code=400, detail=error_message)
    except HTTPException as he:
        logger.error(f"HTTP error occurred: {he.detail}")
        raise
    except Exception as e:
        error_message = f"Repository processing failed: {str(e)}"
        logger.error(error_message)
        logger.error("Full error details:", exc_info=True)
        raise HTTPException(status_code=500, detail=error_message)

@app.post("/api/github/chat", response_model=ChatResponse)
async def github_chat(chat_input: ChatInput):
    logger.info(f"GitHub chat request received for session: {chat_input.session_id}")
    try:
        llm = ChatGroq(
            groq_api_key=chat_input.groq_api_key,
            model_name="llama-3.3-70b-versatile"
        )
        logger.debug("LLM initialized for GitHub chat")
        
        answer, history = await github_bot.get_response(
            chat_input.session_id,
            chat_input.message,
            llm
        )
        logger.debug(f"GitHub chat response generated for session {chat_input.session_id}")
        
        return ChatResponse(
            answer=answer,
            chat_history=history
        )
    except Exception as e:
        error_message = f"Error with GitHub chat: {str(e)}"
        logger.error(error_message, exc_info=True)
        raise HTTPException(status_code=500, detail=error_message)

@app.get("/api/github/sessions")
async def get_github_sessions():
    logger.info("Request received for GitHub sessions")
    try:
        sessions = github_bot.get_available_sessions()
        logger.debug(f"Retrieved {len(sessions)} GitHub sessions")
        return {"sessions": sessions}
    except Exception as e:
        logger.error(f"Error retrieving GitHub sessions: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server")
    uvicorn.run(app, host="0.0.0.0", port=8000)