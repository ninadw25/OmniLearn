from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
import tempfile
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage for chat histories and vector stores
chat_stores = {}
vector_stores = {}      # Need to make this on cloud to deploy

# Initialize embeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

class ChatInput(BaseModel):
    session_id: str
    message: str
    groq_api_key: str

class ChatResponse(BaseModel):
    answer: str
    chat_history: List[Dict[str, str]]

@app.post("/chat", response_model=ChatResponse)
async def chat(chat_input: ChatInput):
    try:
        session_id = chat_input.session_id
       
        # Initialize LLM
        llm = ChatGroq(groq_api_key=chat_input.groq_api_key, model_name="llama-3.3-70b-versatile")
        
        if session_id not in vector_stores:
            raise HTTPException(status_code=400, detail="No documents uploaded for this session")
        
        retriever = vector_stores[session_id].as_retriever()
        
        # Set up the retriever and chains
        contextualize_q_system_prompt = (       # make changes in this
            "Given a chat history and the latest user question "
            "which might reference context in the chat history, "
            "formulate a standalone question which can be understood "
            "without the chat history. Do NOT answer the question, "
            "just reformulate it if needed and otherwise return it as is."
        )
         
        contextualize_q_prompt = ChatPromptTemplate.from_messages([
            # instructs the model to reframe the question by considering the chat history.
            # From all the context present in the history pass only the relavent context to the answer prompt
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        
        # Pura vector store le and contextualize_q_prompt use karke usme se relavent context  
        # nikal ke ex history aware retriever bana so as it does not get confused by the current query.
        history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)

        system_prompt = (
            "You are an assistant for question-answering tasks. "
            "Use the following pieces of retrieved context to answer "
            "the question. If you don't know the answer, say that you "
            "don't know. keep the answer concise and cover all the points."
            "\n\n{context}"
        )
        
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        
        question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
        
        # Get or create chat history
        if session_id not in chat_stores:
            chat_stores[session_id] = ChatMessageHistory()
        
        def get_session_history(session: str):
            return chat_stores[session]
        
        conversational_rag_chain = RunnableWithMessageHistory(
            rag_chain,
            get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer"
        )
        
        # Process the message
        response = conversational_rag_chain.invoke(
            {"input": chat_input.message},
            config={"configurable": {"session_id": session_id}},
        )
        
        # Format chat history for response
        history = []
        for msg in chat_stores[session_id].messages:
            history.append({
                "role": "user" if msg.type == "human" else "assistant",
                "content": msg.content
            })
        
        return ChatResponse(
            answer=response['answer'],
            chat_history=history
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_files(
    files: List[UploadFile] = File(...),
    session_id: str = Form(...)
):
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")

        documents = []
        
        for uploaded_file in files:
            # Verify file is PDF
            if not uploaded_file.filename.lower().endswith('.pdf'):
                raise HTTPException(status_code=400, detail="Only PDF files are allowed")
                
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                content = await uploaded_file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            try:
                # Load and process the PDF
                loader = PyPDFLoader(temp_file_path)
                docs = loader.load()
                documents.extend(docs)
                
                # Clean up temp file
                os.unlink(temp_file_path)
            except Exception as e:
                # Clean up temp file
                os.unlink(temp_file_path)
                raise HTTPException(status_code=400, detail=f"Error processing PDF: {str(e)}")
        
        # Process documents
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=500)
        splits = text_splitter.split_documents(documents)
        
        # Create or update vector store for session
        vector_stores[session_id] = Chroma.from_documents(documents=splits, embedding=embeddings)
        
        return {"message": "Files processed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)