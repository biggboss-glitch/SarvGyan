# 🧠 SarvGyan — Setup Guide

Follow these steps to get the project running on your machine.

---

## Prerequisites

- **Python 3.12+** → [Download](https://www.python.org/downloads/)
- **UV package manager** → [Install](https://github.com/astral-sh/uv)
- **Groq API Key** (free) → [Get one here](https://console.groq.com/keys)
- **4 GB RAM minimum** (8 GB recommended for embedding model)

---

## Step 1 — Install UV

```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Verify:
```bash
uv --version
```

---

## Step 2 — Clone the Repository

```bash
git clone https://github.com/yourusername/SarvGyan.git
cd SarvGyan
```

---

## Step 3 — Create Virtual Environment

```bash
uv venv
```

Activate it:
```bash
.venv\Scripts\activate
```

---

## Step 4 — Install Dependencies

```bash
uv pip install -e .
```

This installs all required packages (Streamlit, Groq SDK, ChromaDB, sentence-transformers, etc.)

---

## Step 5 — Configure Environment

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
HF_TOKEN=your_hftoken_here
LLM_MODEL=llama-3.3-70b-versatile
EMBEDDING_MODEL=BAAI/bge-large-en-v1.5
CHROMA_DB_PATH=data/chroma_db
```

Replace `your_groq_api_key_here` with your actual Groq API key, and `HF_TOKEN` with your HuggingFace token (for faster local embeddings download).

---

## Step 6 — Run the App

```bash
streamlit run app.py
```

The app will open at **http://localhost:8501**

---

## Usage

1. **Upload** a PDF or DOCX file using the sidebar
2. **Wait** for the document to be indexed (first run downloads the embedding model ~1.2 GB)
3. **Ask questions** in the chat box at the bottom
4. **Get answers** sourced from your uploaded documents

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `uv venv` | Create virtual environment |
| `.venv\Scripts\activate` | Activate venv |
| `uv pip install -e .` | Install dependencies |
| `streamlit run app.py` | Start the app |
| `uv run pytest` | Run tests |

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `GROQ_API_KEY not configured` | Set your key in `.env` |
| `Collection dimension mismatch` | Click "Reset All" in the sidebar |
| `Module not found` | Run `uv pip install -e .` again |
| Slow first upload | The embedding model (~1.2 GB) downloads on first use — subsequent runs are instant |
