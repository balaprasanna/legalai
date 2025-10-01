"""
Case Summarizer for LawMate
Handles AI-powered summarization of legal cases
"""

import os
import json
from typing import Dict, List, Any
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CaseSummarizer:
    """AI-powered legal case summarizer"""
    
    def __init__(self, model_name: str = "gpt-4"):
        """Initialize the case summarizer"""
        self.model_name = model_name
        self.llm = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the language model"""
        try:
            self.llm = ChatOpenAI(
                model=self.model_name,
                temperature=0.1,
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
            logger.info(f"Case summarizer initialized with {self.model_name}")
        except Exception as e:
            logger.error(f"Error initializing summarizer: {str(e)}")
            raise
    
    def summarize_case(self, case_text: str) -> Dict[str, Any]:
        """Generate a comprehensive summary of a legal case"""
        try:
            # Split the case into manageable chunks if too long
            chunks = self._split_case_text(case_text)
            
            # Generate summary for each chunk
            summaries = []
            for i, chunk in enumerate(chunks):
                logger.info(f"Processing chunk {i+1}/{len(chunks)}")
                chunk_summary = self._summarize_chunk(chunk)
                summaries.append(chunk_summary)
            
            # Combine summaries into final result
            final_summary = self._combine_summaries(summaries, case_text)
            
            return final_summary
            
        except Exception as e:
            logger.error(f"Error summarizing case: {str(e)}")
            return {"error": str(e)}
    
    def _split_case_text(self, text: str, max_chunk_size: int = 4000) -> List[str]:
        """Split case text into manageable chunks"""
        if len(text) <= max_chunk_size:
            return [text]
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) <= max_chunk_size:
                current_chunk += paragraph + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _summarize_chunk(self, chunk: str) -> Dict[str, Any]:
        """Summarize a single chunk of case text"""
        system_prompt = self._get_system_prompt()
        human_prompt = f"Please analyze this legal case text and extract the key information:\n\n{chunk}"
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            summary_data = self._parse_summary_response(response.content)
            return summary_data
        except Exception as e:
            logger.error(f"Error summarizing chunk: {str(e)}")
            return {"error": str(e)}
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for case summarization"""
        return """You are an expert legal analyst specializing in Indian law. Your task is to analyze legal case texts and extract key information in a structured format.

For each case text provided, extract and summarize:

1. **FACTS**: Key factual background and circumstances of the case
2. **LEGAL ISSUES**: The main legal questions or issues being decided
3. **VERDICT**: The court's decision and reasoning
4. **KEY STATUTES**: Important laws, sections, or acts referenced
5. **PRECEDENTS**: Any previous cases cited as authority
6. **PLAIN ENGLISH**: A simple, non-legal explanation of what happened and why it matters

Format your response as a JSON object with these exact keys:
{
    "facts": "Brief summary of the facts...",
    "issues": "List of legal issues...",
    "verdict": "Court's decision and reasoning...",
    "statutes": ["List", "of", "key", "statutes"],
    "precedents": ["List", "of", "cited", "cases"],
    "plain_english": "Simple explanation for non-lawyers..."
}

Be concise but comprehensive. Focus on the most important aspects that would help lawyers, students, or citizens understand the case quickly."""
    
    def _parse_summary_response(self, response: str) -> Dict[str, Any]:
        """Parse the AI response into structured data"""
        try:
            # Try to extract JSON from the response
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "{" in response and "}" in response:
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                json_str = response[json_start:json_end]
            else:
                # Fallback: create a basic structure
                return {
                    "facts": response[:500] + "..." if len(response) > 500 else response,
                    "issues": "Analysis in progress",
                    "verdict": "Analysis in progress",
                    "statutes": [],
                    "precedents": [],
                    "plain_english": "Analysis in progress"
                }
            
            summary_data = json.loads(json_str)
            return summary_data
            
        except json.JSONDecodeError as e:
            logger.warning(f"Could not parse JSON response: {str(e)}")
            # Fallback: return the raw response
            return {
                "raw_response": response,
                "facts": "Could not parse structured response",
                "issues": "Could not parse structured response",
                "verdict": "Could not parse structured response",
                "statutes": [],
                "precedents": [],
                "plain_english": "Could not parse structured response"
            }
    
    def _combine_summaries(self, summaries: List[Dict[str, Any]], original_text: str) -> Dict[str, Any]:
        """Combine multiple chunk summaries into a final summary"""
        try:
            # If only one summary, return it
            if len(summaries) == 1:
                return summaries[0]
            
            # Combine multiple summaries
            combined_prompt = f"""You are combining multiple summaries of a legal case into one comprehensive summary.

Original case length: {len(original_text)} characters
Number of chunks analyzed: {len(summaries)}

Here are the individual summaries:
{json.dumps(summaries, indent=2)}

Please create a single, comprehensive summary that:
1. Combines all the facts without duplication
2. Identifies all unique legal issues
3. Provides a clear verdict and reasoning
4. Lists all unique statutes and precedents
5. Gives a clear plain English explanation

Format as JSON with these keys: facts, issues, verdict, statutes, precedents, plain_english
"""
            
            messages = [
                SystemMessage(content="You are an expert legal analyst combining case summaries."),
                HumanMessage(content=combined_prompt)
            ]
            
            response = self.llm.invoke(messages)
            final_summary = self._parse_summary_response(response.content)
            
            return final_summary
            
        except Exception as e:
            logger.error(f"Error combining summaries: {str(e)}")
            # Fallback: return the first summary
            return summaries[0] if summaries else {"error": "No summaries to combine"}
    
    def generate_plain_english_explanation(self, case_text: str) -> str:
        """Generate a plain English explanation of the case"""
        prompt = f"""Explain this legal case in simple, everyday language that a non-lawyer can understand. 
        Focus on what happened, why it matters, and what the outcome means for regular people.

        Case text: {case_text[:2000]}...

        Please provide a clear, concise explanation in 2-3 paragraphs."""
        
        try:
            messages = [
                SystemMessage(content="You are a legal expert who explains complex legal matters in simple terms for the general public."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating plain English explanation: {str(e)}")
            return "Unable to generate plain English explanation at this time."
    
    def extract_key_statutes(self, case_text: str) -> List[str]:
        """Extract key statutes and legal provisions from case text"""
        prompt = f"""Extract all the important laws, statutes, sections, and legal provisions mentioned in this case text.
        Return them as a simple list, one per line.

        Case text: {case_text[:2000]}..."""
        
        try:
            messages = [
                SystemMessage(content="You are a legal expert extracting key statutes and provisions from case text."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            statutes = [line.strip() for line in response.content.split('\n') if line.strip()]
            return statutes
            
        except Exception as e:
            logger.error(f"Error extracting statutes: {str(e)}")
            return []

