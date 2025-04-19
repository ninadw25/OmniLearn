import os
import shutil
from typing import List, Tuple, Dict, Any
from fastapi import HTTPException
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain.schema import Document
from .repo_scrape import scrape_textarea_content, convert_github_to_gitingest
from utils.logger import setup_logger
import time
# Set up logger
logger = setup_logger(__name__)

class GitHubRAGBot:
    def __init__(self, embeddings):
        logger.info("Initializing GitHubRAGBot")
        self.embeddings = embeddings
        self.chat_stores = {}
        self.vector_stores = {}
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        self.scraped_content_dir = os.path.join(self.base_dir, "scraped_content")
        
        try:
            os.makedirs(self.scraped_content_dir, exist_ok=True)
            logger.debug(f"Scraped content directory ensured at: {self.scraped_content_dir}")
        except Exception as e:
            logger.error(f"Failed to create scraped content directory: {str(e)}", exc_info=True)
            raise

    async def process_text_file(self, filename: str, session_id: str):
        logger.info(f"Processing text file: {filename} for session: {session_id}")
        try:
            file_path = os.path.join(self.scraped_content_dir, filename)
            logger.debug(f"Full file path: {file_path}")
            
            # More detailed file existence check
            if not os.path.exists(file_path):
                logger.error(f"File not found at path: {file_path}")
                logger.debug(f"Directory contents: {os.listdir(self.scraped_content_dir)}")
                raise HTTPException(
                    status_code=404, 
                    detail=f"File {filename} not found at {file_path}"
                )
            
            documents = []
            logger.debug("Loading text file with TextLoader")
            
            # Create TextLoader with explicit UTF-8 encoding
            loader = TextLoader(file_path, encoding='utf-8')
            
            try:
                docs = loader.load()
                documents.extend(docs)
                logger.info(f"Loaded {len(documents)} documents")
            except Exception as load_error:
                # If loading fails, try to read the file manually
                logger.warning(f"Standard loading failed, attempting manual file reading: {str(load_error)}")
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                        documents = [Document(page_content=text, metadata={"source": file_path})]
                    logger.info("Successfully loaded file manually")
                except Exception as manual_error:
                    logger.error(f"Manual file reading failed: {str(manual_error)}")
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Failed to read file content: {str(manual_error)}"
                    )

            logger.debug("Splitting text into chunks")
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=500)
            splits = text_splitter.split_documents(documents)
            logger.info(f"Created {len(splits)} text chunks")
            
            logger.debug("Creating vector store from documents")
            self.vector_stores[session_id] = Chroma.from_documents(
                documents=splits, 
                embedding=self.embeddings
            )
            logger.info(f"Vector store created for session: {session_id}")
            
            # Keep the file for future reference instead of deleting it
            # os.remove(file_path)  # Comment out file deletion
            logger.debug(f"Processed file saved at: {file_path}")
            
            return {"message": f"File {filename} processed successfully"}
        except Exception as e:
            logger.error(f"Error processing text file: {str(e)}", exc_info=True)
            raise HTTPException(status_code=400, detail=str(e))

    async def process_repository(self, url: str, session_id: str, wait_time: int = 10):
        logger.info(f"Processing repository URL: {url} for session: {session_id}")
        try:
            # Convert URL
            gitingest_url = convert_github_to_gitingest(url)
            logger.debug(f"Using GitIngest URL: {gitingest_url}")
            
            # Ensure scraped_content directory exists
            os.makedirs(self.scraped_content_dir, exist_ok=True)
            
            # Call the scraper function with the correct directory path
            textarea_texts, saved_file = scrape_textarea_content(
                gitingest_url, 
                wait_time=wait_time,
                output_dir=self.scraped_content_dir  # Pass the directory path
            )
            
            if not textarea_texts:
                logger.warning("No content found in repository")
                raise HTTPException(status_code=404, detail="No content found in repository")
            
            # Get just the filename without path
            filename = os.path.basename(saved_file)
            logger.debug(f"Processing file: {filename}")
            
            # Process the file
            result = await self.process_text_file(filename, session_id)
            result["repository"] = url
            result["content_items"] = len(textarea_texts)
            
            logger.info(f"Repository processed successfully with {len(textarea_texts)} content items")
            return result
            
        except Exception as e:
            logger.error(f"Error processing repository: {str(e)}", exc_info=True)
            # Include more debug information
            logger.error(f"Attempted file path: {self.scraped_content_dir}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_response(self, session_id: str, message: str, llm):
        logger.info(f"Generating response for session {session_id}")
        try:
            if session_id not in self.vector_stores:
                logger.error(f"No vector store found for session: {session_id}")
                raise HTTPException(status_code=400, detail="No documents uploaded")
            
            logger.debug("Setting up retriever and prompts")
            retriever = self.vector_stores[session_id].as_retriever()
            
            contextualize_q_prompt = ChatPromptTemplate.from_messages([
                ("system", self._get_contextualize_prompt()),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ])
            
            logger.debug("Creating history aware retriever")
            history_aware_retriever = create_history_aware_retriever(
                llm, retriever, contextualize_q_prompt
            )

            logger.debug("Setting up QA chain")
            qa_prompt = ChatPromptTemplate.from_messages([
                ("system", self._get_qa_prompt()),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ])
            
            question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
            rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
            
            if session_id not in self.chat_stores:
                logger.debug(f"Creating new chat history for session: {session_id}")
                self.chat_stores[session_id] = ChatMessageHistory()
            
            logger.debug("Setting up conversational RAG chain")
            conversational_rag_chain = RunnableWithMessageHistory(
                rag_chain,
                lambda session: self.chat_stores[session],
                input_messages_key="input",
                history_messages_key="chat_history",
                output_messages_key="answer"
            )
            
            logger.info("Generating response")
            response = conversational_rag_chain.invoke(
                {"input": message},
                config={"configurable": {"session_id": session_id}},
            )
            
            logger.debug("Response generated successfully")
            return response['answer'], self._format_history(session_id)
        
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}", exc_info=True)
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
            "After answering user's question create 3 sample questions of your own related to the question user asked"
            "\n\n{context}"
        )

    def _format_history(self, session_id: str):
        """Format the chat history for return."""
        history = []
        for msg in self.chat_stores[session_id].messages:
            history.append({
                "role": "user" if msg.type == "human" else "assistant",
                "content": msg.content
            })
        return history

    def clear_chat_history(self, session_id: str):
        """Clear the chat history for a session."""
        if session_id in self.chat_stores:
            self.chat_stores[session_id].clear()
            logger.info(f"Chat history for session {session_id} cleared successfully")
            return {"message": f"Chat history for session {session_id} cleared successfully"}
        logger.warning(f"No chat history found for session {session_id}")
        return {"message": f"No chat history found for session {session_id}"}

    def get_available_sessions(self):
        """Get a list of sessions with processed repositories."""
        logger.info("Fetching available sessions")
        return list(self.vector_stores.keys())