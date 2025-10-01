"""
RAG Pipeline for LawMate
Handles document chunking, embedding, and retrieval for legal cases
"""

import os
import chromadb
from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from typing import List, Dict, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGPipeline:
    """RAG Pipeline for legal document processing and retrieval"""
    
    def __init__(self, persist_directory: str = "./data/embeddings"):
        """Initialize the RAG pipeline"""
        self.persist_directory = persist_directory
        self.embeddings = None
        self.vectorstore = None
        self.text_splitter = None
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all RAG components"""
        try:
            # Initialize embeddings
            self.embeddings = OpenAIEmbeddings(
                model="text-embedding-3-small",
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
            
            # Initialize text splitter for legal documents
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
                separators=["\n\n", "\n", ". ", " ", ""]
            )
            
            # Initialize ChromaDB
            self.vectorstore = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            self.collection = self.vectorstore.get_or_create_collection(
                name="legal_cases",
                metadata={"description": "Legal case documents and precedents"}
            )
            
            logger.info("RAG Pipeline initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing RAG pipeline: {str(e)}")
            raise
    
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to the vector store"""
        try:
            # Split documents into chunks
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"Split {len(documents)} documents into {len(chunks)} chunks")
            
            # Prepare data for ChromaDB
            texts = [chunk.page_content for chunk in chunks]
            metadatas = [chunk.metadata for chunk in chunks]
            ids = [f"chunk_{i}" for i in range(len(chunks))]
            
            # Generate embeddings
            embeddings = self.embeddings.embed_documents(texts)
            
            # Add to collection
            self.collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids,
                embeddings=embeddings
            )
            
            logger.info(f"Added {len(chunks)} chunks to vector store")
            
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise
    
    def add_case_text(self, case_text: str, metadata: Dict[str, Any] = None) -> None:
        """Add a single case text to the vector store"""
        if metadata is None:
            metadata = {}
        
        # Create document
        document = Document(
            page_content=case_text,
            metadata=metadata
        )
        
        # Add to vector store
        self.add_documents([document])
    
    def search_similar_cases(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for similar cases based on query"""
        try:
            # Generate query embedding
            query_embedding = self.embeddings.embed_query(query)
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            similar_cases = []
            for i in range(len(results['documents'][0])):
                similar_cases.append({
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'similarity': 1 - results['distances'][0][i]  # Convert distance to similarity
                })
            
            logger.info(f"Found {len(similar_cases)} similar cases")
            return similar_cases
            
        except Exception as e:
            logger.error(f"Error searching similar cases: {str(e)}")
            return []
    
    def find_precedents(self, case_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Find legal precedents for a given case"""
        try:
            # Extract key legal terms and concepts
            legal_terms = self._extract_legal_terms(case_text)
            
            # Search for similar cases
            query = f"legal case precedent {case_text[:500]}"
            precedents = self.search_similar_cases(query, n_results)
            
            # Filter and rank precedents
            filtered_precedents = self._filter_precedents(precedents, legal_terms)
            
            return filtered_precedents
            
        except Exception as e:
            logger.error(f"Error finding precedents: {str(e)}")
            return []
    
    def _extract_legal_terms(self, text: str) -> List[str]:
        """Extract key legal terms from case text"""
        # Simple keyword extraction (can be enhanced with NLP)
        legal_keywords = [
            "section", "act", "code", "statute", "law", "court", "judgment",
            "precedent", "ruling", "verdict", "appeal", "petition", "writ",
            "constitutional", "criminal", "civil", "contract", "tort", "property"
        ]
        
        found_terms = []
        text_lower = text.lower()
        
        for keyword in legal_keywords:
            if keyword in text_lower:
                found_terms.append(keyword)
        
        return found_terms
    
    def _filter_precedents(self, precedents: List[Dict[str, Any]], legal_terms: List[str]) -> List[Dict[str, Any]]:
        """Filter and rank precedents based on relevance"""
        # Simple filtering based on legal terms overlap
        filtered = []
        
        for precedent in precedents:
            content = precedent['content'].lower()
            term_matches = sum(1 for term in legal_terms if term in content)
            
            if term_matches > 0:
                precedent['relevance_score'] = term_matches / len(legal_terms)
                filtered.append(precedent)
        
        # Sort by relevance score
        filtered.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return filtered
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store collection"""
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": self.collection.name
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            return {"error": str(e)}
    
    def clear_collection(self) -> None:
        """Clear all documents from the collection"""
        try:
            # Delete the collection and recreate it
            self.vectorstore.delete_collection("legal_cases")
            self.collection = self.vectorstore.create_collection(
                name="legal_cases",
                metadata={"description": "Legal case documents and precedents"}
            )
            logger.info("Collection cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing collection: {str(e)}")
            raise

