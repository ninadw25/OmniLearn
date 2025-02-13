# README.md

# PDF Learning Assistant

## Overview

The PDF Learning Assistant is a tutor application designed to automate the student learning process by allowing students to upload PDF or PPT files of their notes, books, assignments, and other relevant course materials. The application processes these documents, splits the text into manageable chunks, creates vector embeddings using a Hugging Face model, and stores the vectorized chunks in a cloud database, specifically Astra DB.

## Features

- Upload and process PDF and PPT files.
- Recursive text splitting to manage large documents.
- Vector embeddings generation using Hugging Face models.
- Storage of vectorized chunks in Astra DB for efficient retrieval.

## Project Structure

```
pdf-learning-assistant
├── src
│   ├── app
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── config.py
│   ├── database
│   │   ├── __init__.py
│   │   ├── astra_client.py
│   │   └── vector_store.py
│   ├── documents
│   │   ├── __init__.py
│   │   ├── loader.py
│   │   └── splitter.py
│   ├── embeddings
│   │   ├── __init__.py
│   │   └── model.py
│   ├── utils
│   │   ├── __init__.py
│   │   └── helpers.py
├── tests
│   ├── __init__.py
│   ├── test_document_processing.py
│   └── test_vector_store.py
├── config
│   └── settings.py
├── .env
├── requirements.txt
├── setup.py
└── README.md
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/pdf-learning-assistant.git
   cd pdf-learning-assistant
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up your environment variables in the `.env` file.

## Usage

To run the application, execute the following command:
```
python src/app/main.py
```

## Testing

To run the tests, use:
```
pytest tests/
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.