from fastapi import APIRouter
from langserve import add_routes
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from ..services.pdf_processing import process_pdf

router = APIRouter()

# PDF Processing Route
@router.post("/process-pdf")
async def process_pdf_endpoint(file_path: str):
    return process_pdf(file_path)

# Q&A Chain
prompt = ChatPromptTemplate.from_template("""
Answer the question based only on the provided context.
Context: {context}
Question: {input}
Answer in markdown format with clear section headings.
""")

def get_qa_chain(vector_store):
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    return create_retrieval_chain(retriever, prompt)

add_routes(router, get_qa_chain, path="/qa")