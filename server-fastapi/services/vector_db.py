from langchain_community.vectorstores import Cassandra
from langchain_huggingface import HuggingFaceEmbeddings
from config.settings import settings

def get_vector_store():
    embeddings = HuggingFaceEmbeddings (
        model_name=settings.EMBEDDING_MODEL,
        cache_folder="./model_cache",  # Specify a persistent cache location
        encode_kwargs={'normalize_embeddings': True}  # Optional performance optimization
    )
    
    return Cassandra(
        embedding=embeddings,
        table_name=settings.VECTOR_STORE_TABLE,
        **settings.astra_db_config
    )

# # For FAISS (alternative to AstraDB)
# from langchain_community.vectorstores import FAISS

# def get_vector_store():
#     embeddings = HuggingFaceEmbeddings(
#         model_name=settings.EMBEDDING_MODEL
#     )
#     return FAISS.load_local("vectorstore", embeddings)