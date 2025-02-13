from langchain_huggingface import HuggingFaceEmbeddings

def create_embeddings(model_name: str, documents: list) -> list:
    """Create vector embeddings for a list of documents using a Hugging Face model."""
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    vectorized_chunks = embeddings.embed_documents(documents)
    return vectorized_chunks