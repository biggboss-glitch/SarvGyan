# 🛠️ SarvGyan Internal Backend Testing

This repository includes a developer-only Jupyter Notebook (`notebooks/backend_test.ipynb`). You can use this to execute raw backend code for LLM generation, vector embedding, and ChromaDB search without ever running the Streamlit frontend UI.

> **Note:** The `notebooks/` directory and `.ipynb` files are deliberately ignored by `.gitignore` so they remain isolated on your local machine and are not pushed to public repositories.

---

## 🚀 How to Start the Developer Notebook

### 1. Install Developer Dependencies
The project uses `[dev]` optional dependencies for Jupyter components to keep the production app lightweight. 

Run this command in the root project folder:
```bash
uv pip install -e ".[dev]"
```

### 2. Launch Jupyter Server
Start the Jupyter Notebook server using UV:
```bash
uv run jupyter notebook
```

### 3. Open the Notebook
1. A Jupyter interface will automatically open in your web browser.
2. Navigate to the `notebooks` directory.
3. Open `backend_test.ipynb`.
4. Run the cells sequentially (`Shift + Enter`).

---

## 🔍 What this Notebook Does

- **Test LLM (Groq API):** Perform raw `llama-3.3-70b-versatile` generations to ensure your `.env` connection is authenticating successfully.
- **Test Embeddings Engine:** Generate a raw 1024-dimensional embedding vector locally using the `BAAI/bge-large-en-v1.5` HuggingFace model.
- **Inspect Vector Database:** Check how many documents and chunks are permanently stored in your local ChromaDB.
- **Run Raw Semantic Search:** Send text queries and see exactly what context chunks the database returns without the LLM masking them.
- **Wipe Database:** A code block you can manually uncomment to completely factory reset your ChromaDB collections.
