def load_environment_variables():
    """Load environment variables from the .env file."""
    from dotenv import load_dotenv
    import os

    load_dotenv()

    return {
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
        "LANGSMITH_API_KEY": os.getenv("LANGSMITH_API_KEY"),
        "ASTRADB_API_KEY": os.getenv("ASTRADB_API_KEY"),
        "HF_TOKEN": os.getenv("HF_TOKEN"),
    }

def validate_file_extension(file_path):
    """Validate the file extension for supported document types."""
    valid_extensions = ['.pdf', '.ppt', '.pptx']
    if not any(file_path.endswith(ext) for ext in valid_extensions):
        raise ValueError(f"Unsupported file type: {file_path}. Supported types are: {valid_extensions}")

def split_text_into_chunks(text, chunk_size=500, chunk_overlap=50):
    """Split text into chunks with specified size and overlap."""
    import re

    words = re.split(r'\s+', text)
    chunks = []
    for i in range(0, len(words), chunk_size - chunk_overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

def format_document_for_storage(document):
    """Format the document for storage in the vector store."""
    return {
        "content": document.page_content,
        "metadata": {
            "source": document.metadata.get("source", "unknown"),
            "timestamp": document.metadata.get("timestamp", None),
        }
    }