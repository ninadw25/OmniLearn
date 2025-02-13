from langchain.vectorstores.cassandra import Cassandra
from langchain_huggingface import HuggingFaceEmbeddings
from config.settings import settings

def get_vector_store():
    embeddings = HuggingFaceEmbeddings(
        model_name=settings.EMBEDDING_MODEL
    )
    
    return Cassandra(
        embedding=embeddings,
        table_name=settings.VECTOR_STORE_TABLE,
        **settings.astra_db_config
    )

# For FAISS (alternative to AstraDB)
from langchain_community.vectorstores import FAISS

def get_vector_store():
    embeddings = HuggingFaceEmbeddings(
        model_name=settings.EMBEDDING_MODEL
    )
    return FAISS.load_local("vectorstore", embeddings)