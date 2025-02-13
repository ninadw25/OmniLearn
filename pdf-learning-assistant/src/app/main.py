from flask import Flask, request, jsonify
from documents.loader import load_documents
from documents.splitter import split_text
from database.vector_store import add_to_vector_store
from embeddings.model import create_embeddings
import os

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Load and process the document
    documents = load_documents(file)
    chunks = split_text(documents)

    # Create embeddings and store in vector store
    embeddings = create_embeddings(chunks)
    add_to_vector_store(embeddings)

    return jsonify({"message": "File processed successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)