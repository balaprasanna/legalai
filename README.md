# LawMate – AI Legal Case Summarizer & Precedent Finder

## 📖 Overview
LawMate is an AI-powered legal assistant that transforms lengthy Indian judgments into concise, structured summaries and highlights key precedents/statutes. It saves time for lawyers, law students, and citizens by making law more accessible.

## ⚡ Features
- **Case Summarizer**: Convert 50+ page judgments into 1-2 page structured summaries (facts, issues, verdict)
- **Precedent Finder**: Identify and list top cited cases/statutes with short explanations
- **Plain-Language Mode**: Explain case outcomes in simple English for non-lawyers
- **Case Comparison Tool**: Compare two cases side by side to show similarities/differences in reasoning

## 🛠️ Tech Stack
- **Backend**: Python 3.10+
- **UI**: Streamlit
- **RAG**: ChromaDB + OpenAI embeddings
- **LLM**: OpenAI GPT-4/Groq
- **Deployment**: Hugging Face Spaces / Streamlit Cloud

## 📂 Project Structure
```
lawmate-ai/
├── README.md                # Project overview & setup
├── requirements.txt         # Python dependencies
├── .env.example             # Example environment variables (API keys)
├── app/                     # Core app code
│   ├── main.py              # Streamlit entry point
│   ├── rag_pipeline.py      # RAG pipeline (chunking, embedding, retrieval)
│   ├── summarizer.py        # Case summarizer logic
│   ├── precedent_finder.py  # Precedent extraction logic
│   ├── prompts/             # System & user prompt templates
│   └── utils.py             # Helpers (PDF parsing, cleaning, etc.)
├── data/                    
│   ├── sample_cases/        # 2-3 sample Kanoon cases (cached text)
│   └── embeddings/          # VectorDB index storage
├── tests/                   # Unit tests
│   ├── test_rag.py
│   └── test_summarizer.py
└── docs/                    
    ├── architecture.png     # High-level architecture diagram
    └── evaluation.md        # Brief eval report (metrics, gold Qs)
```

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or higher
- OpenAI API key (or Groq API key)

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/lawmate-ai.git
cd lawmate-ai

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your API keys

# Run the application
streamlit run app/main.py
```

### Environment Variables
Create a `.env` file with the following variables:
```
OPENAI_API_KEY=your_openai_api_key_here
GROQ_API_KEY=your_groq_api_key_here  # Optional alternative
```

## 📊 Evaluation

### Metrics
- **Recall@k**: How many relevant precedents are found in top-k results
- **Hallucination Rate**: Percentage of false information generated
- **Latency**: Time to process a case and generate summary
- **Accuracy**: Manual review of summary quality

### Gold Dataset
Mini gold set of 10 case questions with manually prepared summaries for evaluation.

See `docs/evaluation.md` for detailed evaluation methodology.

## 📅 Challenge Timeline

- **Day 3**: Brain (summarizer + precedent pipeline)
- **Day 4**: Optimize RAG + evaluation
- **Day 5**: Integrate UI
- **Day 6-8**: Deployment + review

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Indian Kanoon for providing access to legal case data
- OpenAI for GPT models
- Streamlit for the web interface framework