"""
Tests for RAG Pipeline
"""

import pytest
import os
from unittest.mock import Mock, patch
from app.rag_pipeline import RAGPipeline
from langchain.schema import Document

class TestRAGPipeline:
    """Test cases for RAG Pipeline"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.sample_documents = [
            Document(
                page_content="This is a test legal case about contract law.",
                metadata={"title": "Test Case 1", "court": "Supreme Court"}
            ),
            Document(
                page_content="Another case involving property rights and constitutional law.",
                metadata={"title": "Test Case 2", "court": "High Court"}
            )
        ]
    
    @patch('app.rag_pipeline.OpenAIEmbeddings')
    @patch('app.rag_pipeline.chromadb.PersistentClient')
    def test_rag_pipeline_initialization(self, mock_chroma, mock_embeddings):
        """Test RAG pipeline initialization"""
        # Mock the dependencies
        mock_embeddings.return_value = Mock()
        mock_chroma.return_value.get_or_create_collection.return_value = Mock()
        
        # Test initialization
        rag = RAGPipeline()
        
        assert rag.embeddings is not None
        assert rag.vectorstore is not None
        assert rag.text_splitter is not None
    
    @patch('app.rag_pipeline.OpenAIEmbeddings')
    @patch('app.rag_pipeline.chromadb.PersistentClient')
    def test_add_documents(self, mock_chroma, mock_embeddings):
        """Test adding documents to vector store"""
        # Mock the dependencies
        mock_embeddings.return_value = Mock()
        mock_collection = Mock()
        mock_chroma.return_value.get_or_create_collection.return_value = mock_collection
        
        rag = RAGPipeline()
        
        # Test adding documents
        rag.add_documents(self.sample_documents)
        
        # Verify collection.add was called
        mock_collection.add.assert_called_once()
    
    @patch('app.rag_pipeline.OpenAIEmbeddings')
    @patch('app.rag_pipeline.chromadb.PersistentClient')
    def test_search_similar_cases(self, mock_chroma, mock_embeddings):
        """Test searching for similar cases"""
        # Mock the dependencies
        mock_embeddings.return_value = Mock()
        mock_embeddings.return_value.embed_query.return_value = [0.1, 0.2, 0.3]
        
        mock_collection = Mock()
        mock_collection.query.return_value = {
            'documents': [['Test document 1', 'Test document 2']],
            'metadatas': [[{'title': 'Case 1'}, {'title': 'Case 2'}]],
            'distances': [[0.1, 0.2]]
        }
        mock_chroma.return_value.get_or_create_collection.return_value = mock_collection
        
        rag = RAGPipeline()
        
        # Test search
        results = rag.search_similar_cases("contract law", n_results=2)
        
        assert len(results) == 2
        assert 'content' in results[0]
        assert 'metadata' in results[0]
        assert 'similarity' in results[0]
    
    def test_extract_legal_terms(self):
        """Test legal term extraction"""
        rag = RAGPipeline.__new__(RAGPipeline)  # Create without __init__
        
        text = "This case involves Section 123 of the Indian Contract Act and constitutional law principles."
        terms = rag._extract_legal_terms(text)
        
        assert 'section' in terms
        assert 'act' in terms
        assert 'constitutional' in terms
        assert 'law' in terms
    
    def test_filter_precedents(self):
        """Test precedent filtering"""
        rag = RAGPipeline.__new__(RAGPipeline)  # Create without __init__
        
        precedents = [
            {'content': 'This case involves contract law and property rights', 'similarity': 0.8},
            {'content': 'A criminal case about theft and robbery', 'similarity': 0.6},
            {'content': 'Constitutional law case about fundamental rights', 'similarity': 0.7}
        ]
        
        legal_terms = ['contract', 'property', 'constitutional']
        filtered = rag._filter_precedents(precedents, legal_terms)
        
        assert len(filtered) > 0
        assert all('relevance_score' in p for p in filtered)
    
    @patch('app.rag_pipeline.OpenAIEmbeddings')
    @patch('app.rag_pipeline.chromadb.PersistentClient')
    def test_get_collection_stats(self, mock_chroma, mock_embeddings):
        """Test getting collection statistics"""
        # Mock the dependencies
        mock_embeddings.return_value = Mock()
        mock_collection = Mock()
        mock_collection.count.return_value = 42
        mock_chroma.return_value.get_or_create_collection.return_value = mock_collection
        
        rag = RAGPipeline()
        stats = rag.get_collection_stats()
        
        assert stats['total_documents'] == 42
        assert 'collection_name' in stats

if __name__ == "__main__":
    pytest.main([__file__])

