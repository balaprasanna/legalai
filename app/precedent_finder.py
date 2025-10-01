"""
Precedent Finder for LawMate
Handles finding and analyzing legal precedents for cases
"""

import os
import re
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PrecedentFinder:
    """AI-powered legal precedent finder and analyzer"""
    
    def __init__(self, model_name: str = "gpt-4"):
        """Initialize the precedent finder"""
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
            logger.info(f"Precedent finder initialized with {self.model_name}")
        except Exception as e:
            logger.error(f"Error initializing precedent finder: {str(e)}")
            raise
    
    def find_precedents(self, case_text: str, max_precedents: int = 5) -> List[Dict[str, Any]]:
        """Find legal precedents mentioned in the case text"""
        try:
            # Extract cited cases from the text
            cited_cases = self._extract_cited_cases(case_text)
            
            # Analyze each cited case
            precedents = []
            for case in cited_cases[:max_precedents]:
                precedent_info = self._analyze_precedent(case, case_text)
                if precedent_info:
                    precedents.append(precedent_info)
            
            # If no cited cases found, try to find similar legal concepts
            if not precedents:
                precedents = self._find_conceptual_precedents(case_text, max_precedents)
            
            logger.info(f"Found {len(precedents)} precedents")
            return precedents
            
        except Exception as e:
            logger.error(f"Error finding precedents: {str(e)}")
            return []
    
    def _extract_cited_cases(self, case_text: str) -> List[Dict[str, str]]:
        """Extract cases cited in the legal text"""
        cited_cases = []
        
        # Common patterns for case citations in Indian law
        patterns = [
            # Pattern: Case Name v. Another Party, (Year) Court Citation
            r'([A-Z][^,]+(?:v\.|vs\.|versus)\s+[^,]+),\s*\((\d{4})\)\s*([A-Z\s]+)\s*(\d+)',
            # Pattern: In re Case Name, (Year) Court Citation
            r'In re\s+([^,]+),\s*\((\d{4})\)\s*([A-Z\s]+)\s*(\d+)',
            # Pattern: Case Name, (Year) Court Citation
            r'([A-Z][^,]+),\s*\((\d{4})\)\s*([A-Z\s]+)\s*(\d+)',
            # Pattern: AIR Year Court Page
            r'AIR\s+(\d{4})\s+([A-Z\s]+)\s+(\d+)',
            # Pattern: SCC Year Volume Page
            r'SCC\s+(\d{4})\s+(\d+)\s+(\d+)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, case_text, re.IGNORECASE)
            for match in matches:
                groups = match.groups()
                if len(groups) >= 3:
                    cited_case = {
                        'case_name': groups[0] if groups[0] else f"Case from {groups[1]}",
                        'year': groups[1] if len(groups) > 1 else groups[0],
                        'court': groups[2] if len(groups) > 2 else groups[1],
                        'citation': groups[3] if len(groups) > 3 else groups[2],
                        'full_citation': match.group(0)
                    }
                    cited_cases.append(cited_case)
        
        # Remove duplicates based on full citation
        unique_cases = []
        seen_citations = set()
        for case in cited_cases:
            if case['full_citation'] not in seen_citations:
                unique_cases.append(case)
                seen_citations.add(case['full_citation'])
        
        return unique_cases
    
    def _analyze_precedent(self, cited_case: Dict[str, str], original_case_text: str) -> Optional[Dict[str, Any]]:
        """Analyze a cited case to understand its relevance"""
        try:
            prompt = f"""Analyze this legal precedent and explain its relevance to the current case.

Cited Case: {cited_case['full_citation']}
Case Name: {cited_case['case_name']}
Year: {cited_case['year']}
Court: {cited_case['court']}

Context from current case: {original_case_text[:1000]}...

Please provide:
1. A brief summary of what this precedent case was about
2. Why it's relevant to the current case
3. The legal principle it establishes
4. How it supports or influences the current case

Format as JSON with keys: title, summary, relevance, legal_principle, influence
"""
            
            messages = [
                SystemMessage(content="You are a legal expert analyzing case precedents and their relevance."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            precedent_info = self._parse_precedent_response(response.content)
            
            # Add original citation info
            precedent_info.update({
                'citation': cited_case['full_citation'],
                'year': cited_case['year'],
                'court': cited_case['court']
            })
            
            return precedent_info
            
        except Exception as e:
            logger.error(f"Error analyzing precedent: {str(e)}")
            return None
    
    def _parse_precedent_response(self, response: str) -> Dict[str, Any]:
        """Parse the AI response for precedent analysis"""
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
                    "title": "Unknown Case",
                    "summary": response[:200] + "..." if len(response) > 200 else response,
                    "relevance": "Analysis in progress",
                    "legal_principle": "Analysis in progress",
                    "influence": "Analysis in progress"
                }
            
            import json
            precedent_data = json.loads(json_str)
            return precedent_data
            
        except Exception as e:
            logger.warning(f"Could not parse precedent response: {str(e)}")
            return {
                "title": "Unknown Case",
                "summary": response[:200] + "..." if len(response) > 200 else response,
                "relevance": "Could not parse structured response",
                "legal_principle": "Could not parse structured response",
                "influence": "Could not parse structured response"
            }
    
    def _find_conceptual_precedents(self, case_text: str, max_precedents: int) -> List[Dict[str, Any]]:
        """Find precedents based on legal concepts when no direct citations are found"""
        try:
            prompt = f"""Based on this legal case text, suggest 3-5 important legal precedents that would be relevant to understanding this case.

Case text: {case_text[:2000]}...

For each precedent, provide:
1. The case name and citation
2. A brief summary of what it established
3. Why it's relevant to the current case

Format as JSON array with objects containing: title, citation, summary, relevance
"""
            
            messages = [
                SystemMessage(content="You are a legal expert suggesting relevant precedents based on case content."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            precedents = self._parse_precedents_list(response.content)
            
            return precedents[:max_precedents]
            
        except Exception as e:
            logger.error(f"Error finding conceptual precedents: {str(e)}")
            return []
    
    def _parse_precedents_list(self, response: str) -> List[Dict[str, Any]]:
        """Parse a list of precedents from AI response"""
        try:
            # Try to extract JSON array
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "[" in response and "]" in response:
                json_start = response.find("[")
                json_end = response.rfind("]") + 1
                json_str = response[json_start:json_end]
            else:
                # Fallback: create a basic precedent
                return [{
                    "title": "Suggested Precedent",
                    "citation": "N/A",
                    "summary": response[:200] + "..." if len(response) > 200 else response,
                    "relevance": "Analysis in progress"
                }]
            
            import json
            precedents = json.loads(json_str)
            return precedents if isinstance(precedents, list) else [precedents]
            
        except Exception as e:
            logger.warning(f"Could not parse precedents list: {str(e)}")
            return [{
                "title": "Suggested Precedent",
                "citation": "N/A",
                "summary": response[:200] + "..." if len(response) > 200 else response,
                "relevance": "Could not parse structured response"
            }]
    
    def get_precedent_summary(self, precedent_citation: str) -> Dict[str, Any]:
        """Get a detailed summary of a specific precedent"""
        try:
            prompt = f"""Provide a comprehensive summary of this legal precedent:

Citation: {precedent_citation}

Please include:
1. Case background and facts
2. Legal issues involved
3. Court's decision and reasoning
4. Legal principles established
5. Significance in Indian law
6. How it's commonly cited

Format as JSON with keys: background, issues, decision, principles, significance, common_usage
"""
            
            messages = [
                SystemMessage(content="You are a legal expert providing detailed precedent summaries."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            summary = self._parse_precedent_response(response.content)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting precedent summary: {str(e)}")
            return {"error": str(e)}
    
    def compare_precedents(self, precedent1: str, precedent2: str) -> Dict[str, Any]:
        """Compare two legal precedents"""
        try:
            prompt = f"""Compare these two legal precedents and highlight their similarities and differences:

Precedent 1: {precedent1}
Precedent 2: {precedent2}

Please analyze:
1. Similar legal issues
2. Different approaches or reasoning
3. How they complement or contradict each other
4. Which is more influential
5. When each would be more applicable

Format as JSON with keys: similarities, differences, relationship, influence_comparison, applicability
"""
            
            messages = [
                SystemMessage(content="You are a legal expert comparing legal precedents."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            comparison = self._parse_precedent_response(response.content)
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing precedents: {str(e)}")
            return {"error": str(e)}
