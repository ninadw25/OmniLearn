import tempfile
import os
from typing import List
from fastapi import HTTPException
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

class PDFBot:
    def __init__(self, embeddings):
        self.embeddings = embeddings
        self.chat_stores = {}
        self.vector_stores = {}

    async def process_pdf(self, files: List[bytes], session_id: str):
        try:
            documents = []
            for file_content in files:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                    temp_file.write(file_content)
                    temp_file_path = temp_file.name
                
                try:
                    loader = PyPDFLoader(temp_file_path)
                    docs = loader.load()
                    documents.extend(docs)
                finally:
                    os.unlink(temp_file_path)

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=500)
            splits = text_splitter.split_documents(documents)
            
            self.vector_stores[session_id] = Chroma.from_documents(
                documents=splits, 
                embedding=self.embeddings
            )
            
            return {"message": "Files processed successfully"}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_response(self, session_id: str, message: str, llm):
        try:
            if session_id not in self.vector_stores:
                raise HTTPException(status_code=400, detail="No documents uploaded for this session")
            
            retriever = self.vector_stores[session_id].as_retriever()
            
            # Set up prompts and chains
            contextualize_q_prompt = ChatPromptTemplate.from_messages([
                ("system", self._get_contextualize_prompt()),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ])
            
            history_aware_retriever = create_history_aware_retriever(
                llm, 
                retriever, 
                contextualize_q_prompt
            )

            qa_prompt = ChatPromptTemplate.from_messages([
                ("system", self._get_qa_prompt()),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ])
            
            question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
            rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
            
            # Handle chat history
            if session_id not in self.chat_stores:
                self.chat_stores[session_id] = ChatMessageHistory()
            
            conversational_rag_chain = RunnableWithMessageHistory(
                rag_chain,
                lambda session: self.chat_stores[session],
                input_messages_key="input",
                history_messages_key="chat_history",
                output_messages_key="answer"
            )
            
            response = conversational_rag_chain.invoke(
                {"input": message},
                config={"configurable": {"session_id": session_id}},
            )
            
            return response['answer'], self._format_history(session_id)
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def _get_contextualize_prompt(self):
        return (
            "Given a chat history and the latest user question "
            "which might reference context in the chat history, "
            "formulate a standalone question which can be understood "
            "without the chat history. Do NOT answer the question, "
            "just reformulate it if needed and otherwise return it as is."
        )

    def _get_qa_prompt(self):
        return (
            "You are an assistant for question-answering tasks. "
            "Use the following pieces of retrieved context to answer "
            "the question. If you don't know the answer, say that you "
            "don't know. keep the answer concise and cover all the points."
            "After answering user's question create 3 sample questions of you own related to the question user asked"
            "\n\n{context}"
        )

    def _format_history(self, session_id: str):
        history = []
        for msg in self.chat_stores[session_id].messages:
            history.append({
                "role": "user" if msg.type == "human" else "assistant",
                "content": msg.content
            })
        return history