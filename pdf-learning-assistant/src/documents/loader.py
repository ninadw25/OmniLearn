import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import UnstructuredPPTLoader
from typing import List

def load_pdf(file_path: str) -> List[str]:
    """Load PDF file and extract text."""
    loader = PyPDFLoader(file_path)
    pdf_docs = loader.load()
    return pdf_docs

def load_ppt(file_path: str) -> List[str]:
    """Load PPT file and extract text."""
    loader = UnstructuredPPTLoader(file_path)
    ppt_docs = loader.load()
    return ppt_docs

def load_documents(file_paths: List[str]) -> List[str]:
    """Load documents from given file paths."""
    documents = []
    for file_path in file_paths:
        if file_path.endswith('.pdf'):
            documents.extend(load_pdf(file_path))
        elif file_path.endswith('.ppt') or file_path.endswith('.pptx'):
            documents.extend(load_ppt(file_path))
        else:
            print(f"Unsupported file type: {file_path}")
    return documents