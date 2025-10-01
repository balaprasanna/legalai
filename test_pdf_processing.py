#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for PDF processing functionality
"""

import sys
import os
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

from utils import load_pdf_cases, process_pdf_case, batch_convert_pdfs_to_json

def test_pdf_processing():
    """Test PDF processing functionality"""
    print("Testing PDF Processing Functionality")
    print("=" * 50)
    
    # Test loading PDF cases
    print("\n1. Loading PDF cases from sample_cases_pdf folder...")
    pdf_cases = load_pdf_cases()
    
    if not pdf_cases:
        print("No PDF cases found. Please check if PDFs exist in data/sample_cases_pdf/")
        return
    
    print(f"Found {len(pdf_cases)} PDF cases:")
    for i, case in enumerate(pdf_cases, 1):
        print(f"   {i}. {case['title']}")
        print(f"      File: {case['metadata'].get('file_name', 'Unknown')}")
        print(f"      Size: {case['metadata'].get('file_size_mb', 0):.2f} MB")
        print(f"      Content length: {len(case['content'])} characters")
        print()
    
    # Test processing individual PDF
    print("2. Testing individual PDF processing...")
    if pdf_cases:
        first_case = pdf_cases[0]
        print(f"   Processing: {first_case['title']}")
        
        # Show sample content
        content_preview = first_case['content'][:500] + "..." if len(first_case['content']) > 500 else first_case['content']
        print(f"   Content preview: {content_preview}")
        print()
    
    # Test converting PDFs to JSON
    print("3. Converting PDFs to JSON format...")
    try:
        converted_count = batch_convert_pdfs_to_json()
        print(f"Successfully converted {converted_count} PDF cases to JSON format")
    except Exception as e:
        print(f"Error converting PDFs: {str(e)}")
    
    print("\nPDF processing test completed!")

def test_individual_pdf(pdf_path: str):
    """Test processing a specific PDF file"""
    print(f"Testing individual PDF: {pdf_path}")
    print("=" * 50)
    
    try:
        case_data = process_pdf_case(pdf_path)
        
        print(f"Successfully processed PDF:")
        print(f"   Title: {case_data['title']}")
        print(f"   File: {case_data['metadata'].get('file_name', 'Unknown')}")
        print(f"   Size: {case_data['metadata'].get('file_size_mb', 0):.2f} MB")
        print(f"   Content length: {len(case_data['content'])} characters")
        
        # Show metadata
        print(f"\nMetadata:")
        for key, value in case_data['metadata'].items():
            print(f"   {key}: {value}")
        
        # Show complexity metrics
        if 'complexity' in case_data:
            print(f"\nText Complexity:")
            for key, value in case_data['complexity'].items():
                print(f"   {key}: {value}")
        
        # Show content preview
        content_preview = case_data['content'][:1000] + "..." if len(case_data['content']) > 1000 else case_data['content']
        print(f"\nContent Preview:")
        print(content_preview)
        
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Test specific PDF file
        pdf_path = sys.argv[1]
        test_individual_pdf(pdf_path)
    else:
        # Test all PDFs
        test_pdf_processing()
