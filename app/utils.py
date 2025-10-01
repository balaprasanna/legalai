"""
Utility functions for LawMate
Helper functions for text processing, validation, and data handling
"""

import re
import os
import json
from typing import List, Dict, Any, Optional
import logging
import PyPDF2
import fitz  # PyMuPDF
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_case_text(text: str, min_length: int = 100) -> bool:
    """Validate that the case text is suitable for processing"""
    if not text or not isinstance(text, str):
        return False
    
    # Check minimum length
    if len(text.strip()) < min_length:
        return False
    
    # Check for basic legal content indicators
    legal_indicators = [
        'court', 'judgment', 'petition', 'appeal', 'section', 'act', 'law',
        'plaintiff', 'defendant', 'respondent', 'appellant', 'verdict'
    ]
    
    text_lower = text.lower()
    indicator_count = sum(1 for indicator in legal_indicators if indicator in text_lower)
    
    # At least 2 legal indicators should be present
    return indicator_count >= 2

def clean_case_text(text: str) -> str:
    """Clean and normalize case text"""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove page numbers and headers/footers
    text = re.sub(r'Page \d+ of \d+', '', text)
    text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
    
    # Remove common legal document artifacts
    artifacts = [
        r'IN THE [A-Z\s]+ COURT',
        r'BEFORE THE [A-Z\s]+ COURT',
        r'Case No\.?\s*\d+',
        r'Date:\s*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
        r'Order dated:\s*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}'
    ]
    
    for pattern in artifacts:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    return text.strip()

def extract_case_metadata(text: str) -> Dict[str, Any]:
    """Extract metadata from case text"""
    metadata = {
        'court': None,
        'case_number': None,
        'date': None,
        'judges': [],
        'parties': []
    }
    
    # Extract court name
    court_patterns = [
        r'IN THE ([A-Z\s]+ COURT)',
        r'BEFORE THE ([A-Z\s]+ COURT)',
        r'([A-Z\s]+ COURT) OF'
    ]
    
    for pattern in court_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            metadata['court'] = match.group(1).strip()
            break
    
    # Extract case number
    case_number_patterns = [
        r'Case No\.?\s*([A-Z0-9/-]+)',
        r'C\.A\.\s*No\.?\s*([A-Z0-9/-]+)',
        r'Criminal Appeal No\.?\s*([A-Z0-9/-]+)'
    ]
    
    for pattern in case_number_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            metadata['case_number'] = match.group(1).strip()
            break
    
    # Extract date
    date_patterns = [
        r'Date:\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'Order dated:\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            metadata['date'] = match.group(1).strip()
            break
    
    # Extract judges (simplified)
    judge_patterns = [
        r'Hon\'ble\s+([A-Z\s]+)',
        r'Justice\s+([A-Z\s]+)',
        r'J\.\s+([A-Z\s]+)'
    ]
    
    for pattern in judge_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        metadata['judges'].extend([match.strip() for match in matches])
    
    # Remove duplicates
    metadata['judges'] = list(set(metadata['judges']))
    
    return metadata

def load_sample_cases() -> List[Dict[str, Any]]:
    """Load sample cases from the data directory"""
    sample_cases = []
    sample_dir = "./data/sample_cases"
    
    if not os.path.exists(sample_dir):
        logger.warning(f"Sample cases directory not found: {sample_dir}")
        return sample_cases
    
    try:
        for filename in os.listdir(sample_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(sample_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    case_data = json.load(f)
                    sample_cases.append(case_data)
        
        logger.info(f"Loaded {len(sample_cases)} sample cases")
        
    except Exception as e:
        logger.error(f"Error loading sample cases: {str(e)}")
    
    return sample_cases

def save_sample_case(case_data: Dict[str, Any], filename: str) -> bool:
    """Save a sample case to the data directory"""
    sample_dir = "./data/sample_cases"
    
    try:
        os.makedirs(sample_dir, exist_ok=True)
        
        filepath = os.path.join(sample_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(case_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved sample case: {filename}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving sample case: {str(e)}")
        return False

def extract_legal_sections(text: str) -> List[str]:
    """Extract legal sections and acts mentioned in the text"""
    sections = []
    
    # Common patterns for legal sections
    patterns = [
        r'Section\s+(\d+[A-Z]?)',
        r'Section\s+(\d+[A-Z]?)\s+of\s+([A-Z\s]+)',
        r'(\d+[A-Z]?)\s+of\s+([A-Z\s]+)',
        r'([A-Z\s]+)\s+Act\s+(\d{4})',
        r'([A-Z\s]+)\s+Code\s+of\s+([A-Z\s]+)'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                section = ' '.join(match).strip()
            else:
                section = match.strip()
            
            if section and section not in sections:
                sections.append(section)
    
    return sections

def calculate_text_complexity(text: str) -> Dict[str, float]:
    """Calculate various complexity metrics for the text"""
    if not text:
        return {}
    
    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    
    # Basic metrics
    word_count = len(words)
    sentence_count = len([s for s in sentences if s.strip()])
    avg_words_per_sentence = word_count / sentence_count if sentence_count > 0 else 0
    
    # Legal complexity indicators
    legal_terms = [
        'section', 'act', 'code', 'statute', 'precedent', 'jurisdiction',
        'constitutional', 'criminal', 'civil', 'contract', 'tort', 'property',
        'appeal', 'petition', 'writ', 'mandamus', 'certiorari', 'prohibition'
    ]
    
    legal_term_count = sum(1 for word in words if word.lower() in legal_terms)
    legal_complexity = legal_term_count / word_count if word_count > 0 else 0
    
    # Sentence complexity (average words per sentence)
    sentence_complexity = avg_words_per_sentence / 20  # Normalize to 0-1 scale
    
    return {
        'word_count': word_count,
        'sentence_count': sentence_count,
        'avg_words_per_sentence': avg_words_per_sentence,
        'legal_complexity': legal_complexity,
        'sentence_complexity': min(sentence_complexity, 1.0),
        'overall_complexity': (legal_complexity + min(sentence_complexity, 1.0)) / 2
    }

def format_legal_citation(citation: str) -> str:
    """Format a legal citation for better readability"""
    if not citation:
        return ""
    
    # Common formatting patterns
    citation = re.sub(r'\s+', ' ', citation.strip())
    
    # Format case names
    citation = re.sub(r'([A-Z][a-z]+)\s+v\.?\s+([A-Z][a-z]+)', r'\1 v. \2', citation)
    
    # Format years in parentheses
    citation = re.sub(r'\((\d{4})\)', r'(\1)', citation)
    
    # Format court names
    citation = re.sub(r'([A-Z\s]+)\s+COURT', r'\1 COURT', citation)
    
    return citation

def extract_key_phrases(text: str, max_phrases: int = 10) -> List[str]:
    """Extract key phrases from legal text"""
    if not text:
        return []
    
    # Simple key phrase extraction based on legal terminology
    legal_phrases = [
        'constitutional validity', 'fundamental rights', 'due process',
        'equal protection', 'freedom of speech', 'right to privacy',
        'criminal liability', 'civil liability', 'contractual obligation',
        'tortious liability', 'property rights', 'intellectual property',
        'administrative law', 'judicial review', 'separation of powers'
    ]
    
    found_phrases = []
    text_lower = text.lower()
    
    for phrase in legal_phrases:
        if phrase in text_lower:
            found_phrases.append(phrase)
    
    # Add some basic n-gram extraction
    words = text.split()
    for i in range(len(words) - 2):
        phrase = ' '.join(words[i:i+3]).lower()
        if len(phrase) > 10 and phrase not in found_phrases:
            found_phrases.append(phrase)
    
    return found_phrases[:max_phrases]

def validate_api_key(api_key: str) -> bool:
    """Validate API key format"""
    if not api_key or not isinstance(api_key, str):
        return False
    
    # Basic validation for OpenAI API key format
    if api_key.startswith('sk-') and len(api_key) > 20:
        return True
    
    # Basic validation for other API keys
    if len(api_key) > 10:
        return True
    
    return False

def get_file_size_mb(file_path: str) -> float:
    """Get file size in MB"""
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except OSError:
        return 0.0

def is_valid_pdf(file_path: str) -> bool:
    """Check if file is a valid PDF"""
    try:
        with open(file_path, 'rb') as f:
            header = f.read(4)
            return header == b'%PDF'
    except (OSError, IOError):
        return False

def extract_text_from_pdf(file_path: str, method: str = "pymupdf") -> str:
    """Extract text from PDF file using specified method"""
    if not is_valid_pdf(file_path):
        raise ValueError(f"Invalid PDF file: {file_path}")
    
    try:
        if method == "pymupdf":
            return _extract_text_pymupdf(file_path)
        elif method == "pypdf2":
            return _extract_text_pypdf2(file_path)
        else:
            raise ValueError(f"Unsupported PDF extraction method: {method}")
    except Exception as e:
        logger.error(f"Error extracting text from PDF {file_path}: {str(e)}")
        raise

def _extract_text_pymupdf(file_path: str) -> str:
    """Extract text using PyMuPDF (fitz) - better for complex layouts"""
    try:
        doc = fitz.open(file_path)
        text = ""
        
        for page_num in range(doc.page_count):
            page = doc[page_num]
            text += page.get_text()
            text += "\n\n"  # Add spacing between pages
        
        doc.close()
        return text.strip()
    except Exception as e:
        logger.error(f"PyMuPDF extraction failed: {str(e)}")
        raise

def _extract_text_pypdf2(file_path: str) -> str:
    """Extract text using PyPDF2 - fallback method"""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
                text += "\n\n"  # Add spacing between pages
            
            return text.strip()
    except Exception as e:
        logger.error(f"PyPDF2 extraction failed: {str(e)}")
        raise

def process_pdf_case(file_path: str) -> Dict[str, Any]:
    """Process a PDF case file and extract metadata and content"""
    try:
        # Extract text from PDF
        text = extract_text_from_pdf(file_path)
        
        # Clean the text
        cleaned_text = clean_case_text(text)
        
        # Extract metadata
        metadata = extract_case_metadata(cleaned_text)
        
        # Add file-specific metadata
        file_path_obj = Path(file_path)
        metadata.update({
            'file_name': file_path_obj.name,
            'file_size_mb': get_file_size_mb(file_path),
            'source': 'pdf_upload',
            'extraction_method': 'pymupdf'
        })
        
        # Calculate text complexity
        complexity = calculate_text_complexity(cleaned_text)
        
        return {
            'title': metadata.get('case_number', file_path_obj.stem),
            'content': cleaned_text,
            'metadata': metadata,
            'complexity': complexity,
            'file_path': file_path
        }
        
    except Exception as e:
        logger.error(f"Error processing PDF case {file_path}: {str(e)}")
        raise

def load_pdf_cases(directory: str = "./data/sample_cases_pdf") -> List[Dict[str, Any]]:
    """Load all PDF cases from the specified directory"""
    pdf_cases = []
    pdf_dir = Path(directory)
    
    if not pdf_dir.exists():
        logger.warning(f"PDF cases directory not found: {directory}")
        return pdf_cases
    
    try:
        # Find all PDF files
        pdf_files = list(pdf_dir.glob("*.pdf")) + list(pdf_dir.glob("*.PDF"))
        
        for pdf_file in pdf_files:
            try:
                logger.info(f"Processing PDF: {pdf_file.name}")
                case_data = process_pdf_case(str(pdf_file))
                pdf_cases.append(case_data)
            except Exception as e:
                logger.error(f"Failed to process {pdf_file.name}: {str(e)}")
                continue
        
        logger.info(f"Successfully loaded {len(pdf_cases)} PDF cases")
        return pdf_cases
        
    except Exception as e:
        logger.error(f"Error loading PDF cases: {str(e)}")
        return []

def save_pdf_case_as_json(case_data: Dict[str, Any], output_dir: str = "./data/sample_cases") -> bool:
    """Save processed PDF case data as JSON file"""
    try:
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Create filename from case title or file name
        title = case_data.get('title', 'unknown_case')
        safe_title = re.sub(r'[^\w\s-]', '', title).strip()
        safe_title = re.sub(r'[-\s]+', '_', safe_title)
        
        filename = f"{safe_title}.json"
        filepath = output_path / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(case_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved PDF case as JSON: {filename}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving PDF case as JSON: {str(e)}")
        return False

def convert_pdf_to_json(pdf_file_path: str, output_dir: str = "./data/sample_cases") -> bool:
    """Convert a single PDF case to JSON format"""
    try:
        # Process the PDF
        case_data = process_pdf_case(pdf_file_path)
        
        # Save as JSON
        return save_pdf_case_as_json(case_data, output_dir)
        
    except Exception as e:
        logger.error(f"Error converting PDF to JSON: {str(e)}")
        return False

def batch_convert_pdfs_to_json(pdf_dir: str = "./data/sample_cases_pdf", output_dir: str = "./data/sample_cases") -> int:
    """Convert all PDFs in directory to JSON format"""
    converted_count = 0
    pdf_cases = load_pdf_cases(pdf_dir)
    
    for case_data in pdf_cases:
        if save_pdf_case_as_json(case_data, output_dir):
            converted_count += 1
    
    logger.info(f"Converted {converted_count} PDF cases to JSON format")
    return converted_count

