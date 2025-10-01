"""
LawMate - AI Legal Case Summarizer & Precedent Finder
Main Streamlit application entry point
"""

import streamlit as st
import os
from dotenv import load_dotenv
from rag_pipeline import RAGPipeline
from summarizer import CaseSummarizer
from precedent_finder import PrecedentFinder
from utils import load_sample_cases, validate_case_text, load_pdf_cases, process_pdf_case, batch_convert_pdfs_to_json

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="LawMate - AI Legal Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1f4e79;
        margin: 1rem 0;
    }
    .summary-section {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'rag_pipeline' not in st.session_state:
        st.session_state.rag_pipeline = None
    if 'summarizer' not in st.session_state:
        st.session_state.summarizer = None
    if 'precedent_finder' not in st.session_state:
        st.session_state.precedent_finder = None
    if 'case_text' not in st.session_state:
        st.session_state.case_text = ""
    if 'summary' not in st.session_state:
        st.session_state.summary = None
    if 'precedents' not in st.session_state:
        st.session_state.precedents = []

def load_models():
    """Load AI models and initialize components"""
    try:
        with st.spinner("Loading AI models..."):
            # Initialize RAG pipeline
            st.session_state.rag_pipeline = RAGPipeline()
            
            # Initialize summarizer
            st.session_state.summarizer = CaseSummarizer()
            
            # Initialize precedent finder
            st.session_state.precedent_finder = PrecedentFinder()
            
        st.success("✅ Models loaded successfully!")
        return True
    except Exception as e:
        st.error(f"❌ Error loading models: {str(e)}")
        return False

def main():
    """Main application function"""
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">⚖️ LawMate</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">AI Legal Case Summarizer & Precedent Finder</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # API Key input
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Enter your OpenAI API key to use the application"
        )
        
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        
        # Model selection
        model_choice = st.selectbox(
            "Select Model",
            ["gpt-4", "gpt-3.5-turbo"],
            help="Choose the language model for analysis"
        )
        
        # Load models button
        if st.button("🚀 Load Models", type="primary"):
            if not api_key:
                st.error("Please enter your OpenAI API key first!")
            else:
                load_models()
        
        st.divider()
        
        # Sample cases
        st.header("📚 Sample Cases")
        
        # Load JSON sample cases
        sample_cases = load_sample_cases()
        if sample_cases:
            st.subheader("JSON Cases")
            for i, case in enumerate(sample_cases):
                if st.button(f"Load: {case['title'][:50]}...", key=f"json_sample_{i}"):
                    st.session_state.case_text = case['content']
                    st.rerun()
        
        # Load PDF sample cases
        pdf_cases = load_pdf_cases()
        if pdf_cases:
            st.subheader("PDF Cases")
            for i, case in enumerate(pdf_cases):
                if st.button(f"Load PDF: {case['title'][:50]}...", key=f"pdf_sample_{i}"):
                    st.session_state.case_text = case['content']
                    st.rerun()
        
        # Convert PDFs to JSON button
        if st.button("🔄 Convert PDFs to JSON", help="Convert all PDF cases to JSON format for better processing"):
            with st.spinner("Converting PDFs to JSON..."):
                converted_count = batch_convert_pdfs_to_json()
                if converted_count > 0:
                    st.success(f"✅ Converted {converted_count} PDF cases to JSON format!")
                    st.rerun()
                else:
                    st.warning("No PDFs were converted. Check if PDFs exist in the sample_cases_pdf folder.")
    
    # Main content area
    if not st.session_state.rag_pipeline:
        st.info("👈 Please load the AI models from the sidebar to get started!")
        return
    
    # Input section
    st.header("📝 Input Case Text")
    
    # Text input options
    input_method = st.radio(
        "Choose input method:",
        ["Paste text directly", "Upload PDF file", "Enter Kanoon URL"],
        horizontal=True
    )
    
    if input_method == "Paste text directly":
        case_text = st.text_area(
            "Paste your case text here:",
            height=200,
            placeholder="Paste the full text of the legal case judgment here...",
            value=st.session_state.case_text
        )
    elif input_method == "Upload PDF file":
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
        if uploaded_file:
            # Save uploaded file temporarily
            temp_file_path = f"./temp_{uploaded_file.name}"
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            try:
                # Process the PDF
                with st.spinner("Processing PDF..."):
                    pdf_data = process_pdf_case(temp_file_path)
                    case_text = pdf_data['content']
                    st.success(f"✅ PDF processed successfully! ({pdf_data['metadata'].get('file_size_mb', 0):.2f} MB)")
                    
                    # Show PDF metadata
                    with st.expander("📄 PDF Information"):
                        st.write(f"**File:** {pdf_data['metadata'].get('file_name', 'Unknown')}")
                        st.write(f"**Size:** {pdf_data['metadata'].get('file_size_mb', 0):.2f} MB")
                        st.write(f"**Pages:** {pdf_data['metadata'].get('page_count', 'Unknown')}")
                        st.write(f"**Complexity:** {pdf_data.get('complexity', {}).get('overall_complexity', 0):.2f}")
                        
                        if pdf_data['metadata'].get('court'):
                            st.write(f"**Court:** {pdf_data['metadata']['court']}")
                        if pdf_data['metadata'].get('case_number'):
                            st.write(f"**Case Number:** {pdf_data['metadata']['case_number']}")
                        if pdf_data['metadata'].get('date'):
                            st.write(f"**Date:** {pdf_data['metadata']['date']}")
                
            except Exception as e:
                st.error(f"❌ Error processing PDF: {str(e)}")
                case_text = ""
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
        else:
            case_text = ""
    else:  # Kanoon URL
        kanoon_url = st.text_input("Enter Kanoon case URL:")
        if kanoon_url:
            # TODO: Implement Kanoon scraping
            st.info("Kanoon URL parsing will be implemented in the next version!")
            case_text = ""
        else:
            case_text = ""
    
    # Process button
    if st.button("🔍 Analyze Case", type="primary", disabled=not case_text.strip()):
        if not validate_case_text(case_text):
            st.error("Please enter valid case text (minimum 100 characters)")
        else:
            st.session_state.case_text = case_text
            process_case(case_text)
    
    # Display results
    if st.session_state.summary:
        display_results()

def process_case(case_text):
    """Process the case text and generate summary and precedents"""
    with st.spinner("Analyzing case..."):
        try:
            # Generate summary
            summary = st.session_state.summarizer.summarize_case(case_text)
            st.session_state.summary = summary
            
            # Find precedents
            precedents = st.session_state.precedent_finder.find_precedents(case_text)
            st.session_state.precedents = precedents
            
            st.success("✅ Case analysis completed!")
            
        except Exception as e:
            st.error(f"❌ Error processing case: {str(e)}")

def display_results():
    """Display the analysis results"""
    st.header("📊 Analysis Results")
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📋 Summary", "⚖️ Precedents", "👥 Plain English"])
    
    with tab1:
        display_summary()
    
    with tab2:
        display_precedents()
    
    with tab3:
        display_plain_english()

def display_summary():
    """Display the case summary"""
    if st.session_state.summary:
        st.markdown('<div class="summary-section">', unsafe_allow_html=True)
        st.subheader("📋 Case Summary")
        
        # Facts
        if 'facts' in st.session_state.summary:
            st.markdown("**🔍 Facts:**")
            st.write(st.session_state.summary['facts'])
        
        # Issues
        if 'issues' in st.session_state.summary:
            st.markdown("**❓ Legal Issues:**")
            st.write(st.session_state.summary['issues'])
        
        # Verdict
        if 'verdict' in st.session_state.summary:
            st.markdown("**⚖️ Verdict:**")
            st.write(st.session_state.summary['verdict'])
        
        # Key Statutes
        if 'statutes' in st.session_state.summary:
            st.markdown("**📜 Key Statutes:**")
            for statute in st.session_state.summary['statutes']:
                st.write(f"• {statute}")
        
        st.markdown('</div>', unsafe_allow_html=True)

def display_precedents():
    """Display the precedents found"""
    if st.session_state.precedents:
        st.subheader("⚖️ Related Precedents")
        
        for i, precedent in enumerate(st.session_state.precedents, 1):
            with st.expander(f"Precedent {i}: {precedent.get('title', 'Unknown Case')}"):
                st.write(f"**Court:** {precedent.get('court', 'N/A')}")
                st.write(f"**Year:** {precedent.get('year', 'N/A')}")
                st.write(f"**Relevance:** {precedent.get('relevance', 'N/A')}")
                st.write(f"**Summary:** {precedent.get('summary', 'N/A')}")
    else:
        st.info("No precedents found for this case.")

def display_plain_english():
    """Display plain English explanation"""
    if st.session_state.summary and 'plain_english' in st.session_state.summary:
        st.subheader("👥 Plain English Explanation")
        st.markdown('<div class="summary-section">', unsafe_allow_html=True)
        st.write(st.session_state.summary['plain_english'])
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Plain English explanation not available.")

if __name__ == "__main__":
    main()
