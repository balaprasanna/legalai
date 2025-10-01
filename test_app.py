#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify LawMate application components
"""

import sys
import os
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from utils import load_pdf_cases, process_pdf_case
        print("✅ utils module imported successfully")
    except Exception as e:
        print(f"❌ Error importing utils: {e}")
        return False
    
    try:
        from rag_pipeline import RAGPipeline
        print("✅ rag_pipeline module imported successfully")
    except Exception as e:
        print(f"❌ Error importing rag_pipeline: {e}")
        return False
    
    try:
        from summarizer import CaseSummarizer
        print("✅ summarizer module imported successfully")
    except Exception as e:
        print(f"❌ Error importing summarizer: {e}")
        return False
    
    try:
        from precedent_finder import PrecedentFinder
        print("✅ precedent_finder module imported successfully")
    except Exception as e:
        print(f"❌ Error importing precedent_finder: {e}")
        return False
    
    return True

def test_pdf_processing():
    """Test PDF processing functionality"""
    print("\nTesting PDF processing...")
    
    try:
        from utils import load_pdf_cases
        pdf_cases = load_pdf_cases()
        
        if pdf_cases:
            print(f"✅ Found {len(pdf_cases)} PDF cases")
            return True
        else:
            print("⚠️ No PDF cases found")
            return False
    except Exception as e:
        print(f"❌ Error in PDF processing: {e}")
        return False

def test_environment():
    """Test environment setup"""
    print("\nTesting environment...")
    
    # Check if .env file exists
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file found")
    else:
        print("⚠️ .env file not found - you'll need to create one with your API keys")
    
    # Check if data directories exist
    data_dir = Path("data")
    if data_dir.exists():
        print("✅ data directory found")
    else:
        print("❌ data directory not found")
        return False
    
    pdf_dir = Path("data/sample_cases_pdf")
    if pdf_dir.exists():
        print("✅ PDF samples directory found")
    else:
        print("❌ PDF samples directory not found")
        return False
    
    return True

def main():
    """Run all tests"""
    print("LawMate Application Test")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_imports),
        ("Environment Test", test_environment),
        ("PDF Processing Test", test_pdf_processing)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print(f"\n{'='*40}")
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready to run.")
        print("\nTo start the application, run:")
        print("streamlit run app/main.py")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
