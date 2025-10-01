#!/usr/bin/env python3
"""
LawMate - AI Legal Case Summarizer & Precedent Finder
Simple runner script for the application
"""

import sys
import os
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

def main():
    """Main entry point for the application"""
    try:
        # Import and run the Streamlit app
        from main import main as streamlit_main
        streamlit_main()
    except ImportError as e:
        print(f"Error importing required modules: {e}")
        print("Please install the required dependencies using: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error running the application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

