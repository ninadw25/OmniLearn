import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
load_dotenv()

# os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["ASTRADB_API_KEY"] = os.getenv("ASTRADB_API_KEY")
os.environ["LANGSMITH_TRACING_V2"]="true"
os.environ['HF_TOKEN']=os.getenv("HF_TOKEN")

llm = ChatGroq(
    # model="deepseek-r1-distill-llama-70b",
    model="llama-3.3-70b-versatile",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)


# Loading the PDF 

from langchain_community.document_loaders import PyPDFLoader
# pdf_path = 'attention.pdf'
file_path = "attention.pdf"
loader = PyPDFLoader(file_path)
pdf_docs = loader.load()

# TEXT SPLITTING OF THE PDF INTO CHUNKS
from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter  = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

final_doc = text_splitter.split_documents(pdf_docs)
print(final_doc)

from langchain_huggingface import HuggingFaceEmbeddings


import cassio
from typing import Tuple, Optional

# def init_astradb_connection(token: str, database_id: str) -> bool:
#     """Initialize connection to AstraDB."""
#     try:
#         cassio.init(token=token, database_id=database_id)
#         return True
#     except Exception as e:
#         print(f"Error connecting to AstraDB: {e}")
#         return False

def create_vector_store(pdf_docs: List) -> Cassandra:
    """Create and populate vector store with documents."""
    try:
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        
        vector_store = Cassandra(
            embedding=embeddings,
            table_name=VECTOR_STORE_TABLE,
            session=None,
            keyspace=None
        )
        
        vector_store.add_documents(pdf_docs)
        return vector_store
    except Exception as e:
        print(f"Error creating vector store: {e}")
        raise

from langchain_huggingface import HuggingFaceEmbeddings
from langchain.vectorstores.cassandra import Cassandra
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from typing import List, Any
from config.settings import EMBEDDING_MODEL, VECTOR_STORE_TABLE, CONSISTENCY_LEVEL


def create_retriever(vector_store: Cassandra):
    """Create a retriever from the vector store."""
    try:
        return vector_store.as_retriever(
            search_kwargs={"k": 3},  # Number of documents to retrieve
            consistency_level=CONSISTENCY_LEVEL
        )
    except Exception as e:
        print(f"Error creating retriever: {e}")
        raise

def perform_search(vector_store: Cassandra, query: str) -> Any:
    """Perform search query on vector store."""
    try:
        retriever = create_retriever(vector_store)
        return retriever.invoke(query)
    except Exception as e:
        print(f"Error performing search: {e}")
        raise

from langchain_community.vectorstores import FAISS
vectorstoredb = FAISS.from_documents(document,embeddings)
vectorstoredb

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
prompt = ChatPromptTemplate.from_template (
    """ 
Answer the following question based only on the provided context:
<context>
{context}
</context>

"""
)

document_chain = create_stuff_documents_chain(llm,prompt) 
type(document_chain)

from langchain_core.documents import Document

document_chain.invoke ({
    "input":"LangSmith has two usage limits: total traces and extended",
    "context":[Document(page_content="LangSmith has two usage limits: total traces and extended traces. These correspond to the two metrics we've been tracking on our usage graph. ")]
})
