"""
Tests for Case Summarizer
"""

import pytest
import json
from unittest.mock import Mock, patch
from app.summarizer import CaseSummarizer

class TestCaseSummarizer:
    """Test cases for Case Summarizer"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.sample_case_text = """
        IN THE SUPREME COURT OF INDIA
        
        Case No: 12345 of 2023
        
        Petitioner: John Doe
        Respondent: State of Maharashtra
        
        This case involves a dispute over property rights under the Transfer of Property Act, 1882.
        The petitioner claims ownership of a piece of land based on adverse possession.
        The respondent argues that the land belongs to the state.
        
        The court considered various precedents including Smith v. Jones (2020) and Brown v. White (2019).
        Section 27 of the Limitation Act, 1963 was also relevant.
        
        After considering all arguments, the court ruled in favor of the petitioner.
        The judgment established that adverse possession requires continuous possession for 12 years.
        """
    
    @patch('app.summarizer.ChatOpenAI')
    def test_summarizer_initialization(self, mock_chat_openai):
        """Test case summarizer initialization"""
        mock_llm = Mock()
        mock_chat_openai.return_value = mock_llm
        
        summarizer = CaseSummarizer()
        
        assert summarizer.llm is not None
        assert summarizer.model_name == "gpt-4"
    
    def test_split_case_text(self):
        """Test case text splitting"""
        summarizer = CaseSummarizer.__new__(CaseSummarizer)  # Create without __init__
        
        # Test short text (should not split)
        short_text = "This is a short case."
        chunks = summarizer._split_case_text(short_text)
        assert len(chunks) == 1
        assert chunks[0] == short_text
        
        # Test long text (should split)
        long_text = "This is a very long case text. " * 1000  # Create long text
        chunks = summarizer._split_case_text(long_text, max_chunk_size=1000)
        assert len(chunks) > 1
        assert all(len(chunk) <= 1000 for chunk in chunks)
    
    def test_parse_summary_response(self):
        """Test parsing of AI response"""
        summarizer = CaseSummarizer.__new__(CaseSummarizer)  # Create without __init__
        
        # Test valid JSON response
        valid_json = """
        {
            "facts": "Test facts",
            "issues": "Test issues",
            "verdict": "Test verdict",
            "statutes": ["Section 123"],
            "precedents": ["Case v. Case"],
            "plain_english": "Test explanation"
        }
        """
        
        result = summarizer._parse_summary_response(valid_json)
        assert result['facts'] == "Test facts"
        assert result['issues'] == "Test issues"
        assert result['statutes'] == ["Section 123"]
    
    def test_parse_summary_response_with_code_blocks(self):
        """Test parsing response with code blocks"""
        summarizer = CaseSummarizer.__new__(CaseSummarizer)  # Create without __init__
        
        response_with_code = """
        Here's the analysis:
        
        ```json
        {
            "facts": "Test facts",
            "issues": "Test issues",
            "verdict": "Test verdict",
            "statutes": ["Section 123"],
            "precedents": ["Case v. Case"],
            "plain_english": "Test explanation"
        }
        ```
        """
        
        result = summarizer._parse_summary_response(response_with_code)
        assert result['facts'] == "Test facts"
        assert result['issues'] == "Test issues"
    
    def test_parse_summary_response_invalid_json(self):
        """Test parsing invalid JSON response"""
        summarizer = CaseSummarizer.__new__(CaseSummarizer)  # Create without __init__
        
        invalid_response = "This is not a valid JSON response."
        result = summarizer._parse_summary_response(invalid_response)
        
        assert 'raw_response' in result
        assert result['facts'] == "Could not parse structured response"
    
    @patch('app.summarizer.ChatOpenAI')
    def test_generate_plain_english_explanation(self, mock_chat_openai):
        """Test plain English explanation generation"""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "This is a simple explanation of the case."
        mock_llm.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_llm
        
        summarizer = CaseSummarizer()
        result = summarizer.generate_plain_english_explanation("Test case text")
        
        assert result == "This is a simple explanation of the case."
        mock_llm.invoke.assert_called_once()
    
    @patch('app.summarizer.ChatOpenAI')
    def test_extract_key_statutes(self, mock_chat_openai):
        """Test key statutes extraction"""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "Section 123\nIndian Contract Act\nProperty Law"
        mock_llm.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_llm
        
        summarizer = CaseSummarizer()
        result = summarizer.extract_key_statutes("Test case text")
        
        assert "Section 123" in result
        assert "Indian Contract Act" in result
        assert "Property Law" in result
    
    @patch('app.summarizer.ChatOpenAI')
    def test_combine_summaries(self, mock_chat_openai):
        """Test combining multiple summaries"""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = """
        {
            "facts": "Combined facts",
            "issues": "Combined issues",
            "verdict": "Combined verdict",
            "statutes": ["Section 123", "Section 456"],
            "precedents": ["Case 1", "Case 2"],
            "plain_english": "Combined explanation"
        }
        """
        mock_llm.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_llm
        
        summarizer = CaseSummarizer()
        
        summaries = [
            {
                "facts": "Facts 1",
                "issues": "Issues 1",
                "verdict": "Verdict 1",
                "statutes": ["Section 123"],
                "precedents": ["Case 1"],
                "plain_english": "Explanation 1"
            },
            {
                "facts": "Facts 2",
                "issues": "Issues 2",
                "verdict": "Verdict 2",
                "statutes": ["Section 456"],
                "precedents": ["Case 2"],
                "plain_english": "Explanation 2"
            }
        ]
        
        result = summarizer._combine_summaries(summaries, "Original text")
        
        assert result['facts'] == "Combined facts"
        assert "Section 123" in result['statutes']
        assert "Section 456" in result['statutes']

if __name__ == "__main__":
    pytest.main([__file__])

