import os
import pytest
from io import BytesIO
from unittest.mock import patch, MagicMock

# Import the Flask app from your app.py
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@patch('app.PyPDFLoader')
@patch('app.vector_store')
def test_upload_pdf_success(mock_vector_store, mock_pdf_loader, client):
    """Test the document ingestion endpoint."""
    
    # Mock the PDF loading and embedding process
    mock_doc = MagicMock()
    mock_doc.page_content = "dummy document content"
    mock_doc.metadata = {"source": "test_doc.pdf"}
    
    mock_instance = MagicMock()
    mock_instance.load.return_value = [mock_doc]
    mock_pdf_loader.return_value = mock_instance
    
    # Create a fake PDF file in memory
    data = {
        'file': (BytesIO(b"%PDF-1.4 fake pdf content"), 'test_doc.pdf')
    }
    
    response = client.post('/api/upload', data=data, content_type='multipart/form-data')
    
    assert response.status_code == 200
    assert b"Successfully indexed test_doc.pdf" in response.data
    mock_vector_store.add_documents.assert_called_once_with([mock_doc])

def test_multiple_uploads_preserve_searchable_documents_and_update_stats(client, tmp_path, monkeypatch):
    class InMemoryVectorStore:
        def __init__(self):
            self.documents = []
            self._collection = self

        def add_documents(self, documents):
            self.documents.extend(documents)

        def count(self):
            return len(self.documents)

        def similarity_search(self, query, k):
            return [doc for doc in self.documents if query.lower() in doc.page_content.lower()][:k]

    vector_store = InMemoryVectorStore()
    monkeypatch.setattr('app.UPLOAD_FOLDER', str(tmp_path))
    monkeypatch.setattr('app.vector_store', vector_store)

    for filename, content in (
        ('first.txt', 'The observatory telescope uses a cobalt filter.'),
        ('second.txt', 'The greenhouse irrigation schedule runs at dawn.'),
    ):
        response = client.post(
            '/api/upload',
            data={'file': (BytesIO(content.encode('utf-8')), filename)},
            content_type='multipart/form-data',
        )
        assert response.status_code == 200

    assert len(vector_store.documents) == 2
    assert [doc.page_content for doc in vector_store.similarity_search('cobalt filter', k=4)] == [
        'The observatory telescope uses a cobalt filter.'
    ]
    assert [doc.page_content for doc in vector_store.similarity_search('irrigation schedule', k=4)] == [
        'The greenhouse irrigation schedule runs at dawn.'
    ]

    stats_response = client.get('/api/stats')
    assert stats_response.status_code == 200
    assert stats_response.get_json()['total_chunks_indexed'] == 2

    with patch('app.llm') as mock_llm, patch('app.history_collection') as mock_history:
        mock_llm.invoke.return_value.content = 'The telescope uses a cobalt filter.'
        mock_history.find_one.return_value = {'history': []}

        chat_response = client.post('/api/chat', json={'message': 'cobalt filter'})

    assert chat_response.status_code == 200
    assert 'The observatory telescope uses a cobalt filter.' in mock_llm.invoke.call_args.args[0]

def test_upload_no_file(client):
    """Test upload endpoint with missing file."""
    response = client.post('/api/upload', data={})
    
    assert response.status_code == 400
    assert b"No file part" in response.data

@patch('app.vector_store')
@patch('app.llm')
@patch('app.history_collection')
def test_chat_query(mock_history, mock_llm, mock_vector_store, client):
    """Test the RAG chat retrieval endpoint."""
    
    # Mock the vector DB search results
    mock_doc = MagicMock()
    mock_doc.page_content = "This is the retrieved context from the PDF."
    mock_vector_store.similarity_search.return_value = [mock_doc]
    
    # Mock the LLM response
    mock_response = MagicMock()
    mock_response.content = "Based on the context, this is the answer."
    mock_llm.invoke.return_value = mock_response
    
    # Mock database history
    mock_history.find_one.return_value = {"history": []}
    
    payload = {
        "message": "What is in the document?",
        "session_id": "test_session_123"
    }
    
    response = client.post('/api/chat', json=payload)
    
    assert response.status_code == 200
    assert b"Based on the context, this is the answer." in response.data

def test_chat_missing_message(client):
    """Test chat endpoint with empty payload."""
    response = client.post('/api/chat', json={"session_id": "123"})
    
    assert response.status_code == 400
    assert b"Message is required" in response.data