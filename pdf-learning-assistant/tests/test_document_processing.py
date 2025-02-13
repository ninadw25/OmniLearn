import unittest
from src.documents.loader import load_pdf, load_ppt
from src.documents.splitter import RecursiveCharacterTextSplitter

class TestDocumentProcessing(unittest.TestCase):

    def setUp(self):
        self.pdf_file_path = 'path/to/sample.pdf'
        self.ppt_file_path = 'path/to/sample.ppt'
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

    def test_load_pdf(self):
        documents = load_pdf(self.pdf_file_path)
        self.assertIsInstance(documents, list)
        self.assertGreater(len(documents), 0)

    def test_load_ppt(self):
        documents = load_ppt(self.ppt_file_path)
        self.assertIsInstance(documents, list)
        self.assertGreater(len(documents), 0)

    def test_split_documents(self):
        sample_text = "This is a sample text that will be split into chunks. " * 10
        chunks = self.text_splitter.split(sample_text)
        self.assertIsInstance(chunks, list)
        self.assertGreater(len(chunks), 1)

if __name__ == '__main__':
    unittest.main()