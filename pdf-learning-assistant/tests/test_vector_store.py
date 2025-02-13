def test_create_vector_store():
    from src.database.vector_store import create_vector_store
    from src.embeddings.model import HuggingFaceEmbeddings

    # Mock data
    pdf_docs = ["This is a test document.", "This is another test document."]
    embeddings_model = HuggingFaceEmbeddings(model_name="your_model_name")

    # Create vector store
    vector_store = create_vector_store(pdf_docs)

    # Check if the vector store is created successfully
    assert vector_store is not None
    assert len(vector_store.documents) == len(pdf_docs)

def test_add_documents():
    from src.database.vector_store import create_vector_store

    # Mock data
    pdf_docs = ["Document 1", "Document 2"]
    vector_store = create_vector_store(pdf_docs)

    # Add new document
    new_doc = "Document 3"
    vector_store.add_documents([new_doc])

    # Check if the new document is added
    assert len(vector_store.documents) == 3
    assert new_doc in vector_store.documents

def test_retrieve_documents():
    from src.database.vector_store import create_vector_store

    # Mock data
    pdf_docs = ["Document 1", "Document 2"]
    vector_store = create_vector_store(pdf_docs)

    # Retrieve documents
    retrieved_docs = vector_store.retrieve_documents(query="Document 1")

    # Check if the correct document is retrieved
    assert len(retrieved_docs) == 1
    assert retrieved_docs[0] == "Document 1"