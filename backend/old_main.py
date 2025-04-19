# from fastapi import FastAPI, UploadFile, File, HTTPException, Form
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from typing import List, Dict
# from langchain_groq import ChatGroq
# from dotenv import load_dotenv
# import os

# from utils.embeddings import get_embeddings
# from rag.pdf_bot import PDFBot
# from rag.github_rag import GitHubRAGBot  # Update import

# # Load environment variables
# load_dotenv()

# app = FastAPI()

# # Enable CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Initialize RAG bots
# pdf_bot = PDFBot(get_embeddings())
# github_bot = GitHubRAGBot(get_embeddings())  # Update initialization

# class ChatInput(BaseModel):     # using the pydantic basemodel to make a bucker
#     session_id: str
#     message: str
#     groq_api_key: str

# class ChatResponse(BaseModel):
#     answer: str
#     chat_history: List[Dict[str, str]]

# class GitHubInput(BaseModel):
#     url: str
#     session_id: str

# @app.post("/upload")
# async def upload_files(
#     files: List[UploadFile] = File(...),    #Expects one or more files uploaded under the form field name "files". FastAPI provides each file as an UploadFile object.
#     session_id: str = Form(...)
# ):
#     try:
#         if not files:
#             raise HTTPException(status_code=400, detail="No files provided")

#         file_contents = []
#         for uploaded_file in files:
#             if not uploaded_file.filename.lower().endswith('.pdf'):
#                 raise HTTPException(status_code=400, detail="Only PDF files are allowed")
#             content = await uploaded_file.read()
#             file_contents.append(content)

#         return await pdf_bot.process_pdf(file_contents, session_id)
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/chat", response_model=ChatResponse)
# async def chat(chat_input: ChatInput):
#     try:
#         llm = ChatGroq(
#             groq_api_key=chat_input.groq_api_key, 
#             model_name="llama-3.3-70b-versatile"
#         )
        
#         answer, history = await pdf_bot.get_response(
#             chat_input.session_id,
#             chat_input.message,
#             llm
#         )
        
#         return ChatResponse(
#             answer=answer,
#             chat_history=history
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/api/github/process")
# async def process_github(github_input: GitHubInput):
#     try:
#         return await github_bot.process_github_repo(
#             github_input.url,
#             github_input.session_id
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/api/github/chat", response_model=ChatResponse)
# async def github_chat(chat_input: ChatInput):
#     try:
#         llm = ChatGroq(
#             groq_api_key=chat_input.groq_api_key, 
#             model_name="llama-3.3-70b-versatile"
#         )
        
#         answer, history = await github_bot.get_response(
#             chat_input.session_id,
#             chat_input.message,
#             llm
#         )
        
#         return ChatResponse(
#             answer=answer,
#             chat_history=history
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)