#  SarvGyan

**AI-Powered Document Q&A Assistant**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![UV](https://img.shields.io/badge/uv-latest-00D9FF.svg)](https://github.com/astral-sh/uv)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🌟 Overview

SarvGyan transforms your documents into an intelligent assistant that can:

- 📚 Answer questions from your PDFs and Word documents
- 🔍 Perform semantic search across multiple documents
- 💬 Maintain conversation context and memory
- 📊 Generate summaries and extract key points

---

## ✨ Features

- ✅ **Document Processing** — PDF and DOCX support
- ✅ **Semantic Search** — Vector-based retrieval with ChromaDB
- ✅ **AI-Powered Q&A** — Context-aware answers with conversation history
- ✅ **Multi-Document** — Search across all uploaded files simultaneously
- ✅ **Custom Theme & Branding** — Built-in Light/Dark mode toggle and custom app icon
- ✅ **Clean Terminal Logging** — Structured, emoji-based CLI output for easy monitoring
- ✅ **Developer Testing** — Isolated Jupyter Notebook for backend debugging
- ✅ **Fast Setup** — Up and running in minutes with UV

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- [UV package manager](https://github.com/astral-sh/uv)
- [Groq API Key](https://console.groq.com/keys) (free)

### Setup

```bash
# Clone
git clone https://github.com/yourusername/SarvGyan.git
cd SarvGyan

# Create & activate virtual environment
uv venv
.venv\Scripts\activate

# Install dependencies
uv pip install -e .
```

### Configure

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
HF_TOKEN=your_huggingface_token_here
LLM_MODEL=llama-3.3-70b-versatile
EMBEDDING_MODEL=BAAI/bge-large-en-v1.5
CHROMA_DB_PATH=data/chroma_db
```

### Run

```bash
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

> 📖 See **[SETUP.md](SETUP.md)** for the full step-by-step guide.

---

## 📁 Project Structure

```
SarvGyan/
├── pyproject.toml          # Dependencies & project config
├── .env                    # API keys (not committed)
├── app.py                  # Main application
├── assets/                 # App icons and media
│   └── icon.png
├── notebooks/              # Developer testing environment
│   └── backend_test.ipynb
├── src/
│   ├── document_processor.py   # PDF/DOCX text extraction
│   ├── embeddings.py           # Vector embedding generation
│   ├── vector_store.py         # ChromaDB operations
│   ├── llm_handler.py          # LLM API integration
│   ├── qa_chain.py             # RAG pipeline orchestrator
│   └── utils.py                # Helper functions
├── data/
│   ├── uploads/            # User documents
│   ├── chroma_db/          # Vector database
│   └── temp/               # Temporary files
├── prompts/                # Prompt templates
└── .streamlit/             # UI configuration
```

---

## � Usage

1. **Upload** — Drag & drop PDFs or DOCX files in the sidebar
2. **Wait** — Documents are automatically chunked and indexed
3. **Ask** — Type questions in the chat box
4. **Read** — Get AI-generated answers with source citations

---

## 🧪 Testing

```bash
uv run pytest
uv run pytest --cov=src
```

---

## 📝 License

MIT License — see [LICENSE](LICENSE) for details.

---

**© 2025 SarvGyan. All rights reserved.**
