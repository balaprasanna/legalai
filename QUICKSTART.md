# LawMate Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### 1. Prerequisites
- Python 3.8 or higher
- OpenAI API key (get one from [OpenAI](https://platform.openai.com/api-keys))

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/lawmate-ai.git
cd lawmate-ai

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env and add your OpenAI API key
```

### 3. Run the Application
```bash
# Option 1: Using Streamlit directly
streamlit run app/main.py

# Option 2: Using the runner script
python run.py
```

### 4. Using LawMate

1. **Load Models**: Enter your OpenAI API key in the sidebar and click "Load Models"
2. **Input Case**: Paste your legal case text in the main text area
3. **Analyze**: Click "Analyze Case" to generate summary and find precedents
4. **Review Results**: Check the Summary, Precedents, and Plain English tabs

## 📁 Project Structure

```
lawmate-ai/
├── app/                    # Main application code
│   ├── main.py            # Streamlit UI
│   ├── rag_pipeline.py    # RAG system for document retrieval
│   ├── summarizer.py      # AI case summarization
│   ├── precedent_finder.py # Legal precedent analysis
│   ├── utils.py           # Utility functions
│   └── prompts/           # AI prompt templates
├── data/                  # Data storage
│   ├── sample_cases/      # Sample legal cases
│   └── embeddings/        # Vector database storage
├── tests/                 # Unit tests
├── docs/                  # Documentation
└── requirements.txt       # Python dependencies
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file with:
```env
OPENAI_API_KEY=your_openai_api_key_here
GROQ_API_KEY=your_groq_api_key_here  # Optional
DEFAULT_MODEL=gpt-4
EMBEDDING_MODEL=text-embedding-3-small
```

### Model Options
- **GPT-4**: Best quality, slower, more expensive
- **GPT-3.5-turbo**: Good quality, faster, cheaper
- **Groq**: Alternative provider for faster inference

## 📊 Features

### ✅ Implemented
- **Case Summarization**: Extract facts, issues, verdict from legal cases
- **Precedent Finding**: Identify and analyze cited legal precedents
- **Plain English**: Convert legal jargon to everyday language
- **Sample Cases**: Pre-loaded cases for testing
- **RAG Pipeline**: Vector-based document retrieval system

### 🚧 Coming Soon
- **PDF Upload**: Direct PDF case document processing
- **Kanoon Integration**: Direct scraping from Indian Kanoon website
- **Case Comparison**: Side-by-side case analysis
- **Export Options**: Save summaries as PDF/Word documents

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_summarizer.py

# Run with coverage
pytest --cov=app
```

## 📈 Performance

- **Average Processing Time**: 10-15 seconds per case
- **Memory Usage**: ~2GB for full model loading
- **Accuracy**: 85-90% on legal fact extraction
- **Supported Languages**: English (Indian legal context)

## 🐛 Troubleshooting

### Common Issues

1. **"Error loading models"**
   - Check your OpenAI API key is correct
   - Ensure you have sufficient API credits
   - Try using GPT-3.5-turbo instead of GPT-4

2. **"No precedents found"**
   - The case might not cite other cases
   - Try with a longer, more detailed case text
   - Check if the case text contains legal citations

3. **"Invalid case text"**
   - Ensure the text is at least 100 characters
   - Make sure it contains legal content
   - Try with one of the sample cases first

### Getting Help

- Check the [README.md](README.md) for detailed documentation
- Review the [evaluation report](docs/evaluation.md) for performance metrics
- Open an issue on GitHub for bugs or feature requests

## 🎯 Next Steps

1. **Test with Sample Cases**: Try the pre-loaded sample cases
2. **Add Your Own Cases**: Paste real legal case text
3. **Customize Prompts**: Modify prompts in `app/prompts/` for your needs
4. **Deploy**: Use Streamlit Cloud or Hugging Face Spaces for deployment

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Happy Legal Research! ⚖️**

