"""
QA Chain Module

Orchestrates the full RAG pipeline: document processing → embedding →
vector search → LLM response generation.
"""

import os
import logging
from typing import Dict, List, Optional, Generator
from pathlib import Path

from src.document_processor import process_document
from src.vector_store import VectorStore
from src.llm_handler import generate_response, generate_response_stream

logger = logging.getLogger(__name__)


# Load prompt templates
PROMPTS_DIR = Path("prompts")


def _load_prompt(filename: str) -> str:
    """Load a prompt template from the prompts/ directory."""
    path = PROMPTS_DIR / filename
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


QA_PROMPT_TEMPLATE = _load_prompt("qa_prompt.txt")
SUMMARY_PROMPT_TEMPLATE = _load_prompt("summary_prompt.txt")


class QAChain:
    """Orchestrates the RAG question-answering pipeline."""

    def __init__(self, vector_store: Optional[VectorStore] = None):
        """Initialize the QA chain.

        Args:
            vector_store: Optional VectorStore instance. Creates default if None.
        """
        self.vector_store = vector_store or VectorStore()
        self.chat_history: List[Dict[str, str]] = []

    def index_document(
        self,
        file_path: str,
        file_type: str,
        doc_id: Optional[str] = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ) -> Dict:
        """Process and index a document into the vector store.

        Args:
            file_path: Path to the document file.
            file_type: Type of file ("pdf" or "docx").
            doc_id: Optional custom document ID. Defaults to filename.
            chunk_size: Characters per chunk.
            chunk_overlap: Overlap between chunks.

        Returns:
            Dict with processing results and metadata.
        """
        doc_id = doc_id or os.path.basename(file_path)

        logger.info(f"\n📄 [Embedding]  Extracting text & chunks from '{doc_id}'")
        result = process_document(file_path, file_type, chunk_size, chunk_overlap)
        
        logger.info(f"💾 [Storing]    Saving {len(result['chunks'])} chunks to Vector Database")
        num_chunks = self.vector_store.add_documents(
            chunks=result["chunks"],
            doc_id=doc_id,
            metadata=result["metadata"],
        )

        return {
            "doc_id": doc_id,
            "chunks_indexed": num_chunks,
            "total_characters": result["metadata"]["total_characters"],
            "status": "success",
        }

    def ask_question(
        self,
        question: str,
        n_results: int = 5,
        filter_doc_id: Optional[str] = None,
    ) -> Dict:
        """Ask a question and get an answer from the indexed documents.

        Args:
            question: The user's question.
            n_results: Number of context chunks to retrieve.
            filter_doc_id: Optional document ID to restrict search.

        Returns:
            Dict with 'answer', 'sources', and 'context'.
        """
        # Retrieve relevant context
        logger.info(f"\n🔍 [Searching]  Retrieving chunks matching: \"{question}\"")
        search_results = self.vector_store.search(
            query=question,
            n_results=n_results,
            filter_doc_id=filter_doc_id,
        )
        logger.info(f"   [Found]      {len(search_results)} relevant chunks in vector store")

        context = "\n\n---\n\n".join([r["text"] for r in search_results])

        # Format chat history
        history_str = ""
        for entry in self.chat_history[-5:]:  # Last 5 exchanges
            history_str += f"Human: {entry['question']}\nAI: {entry['answer']}\n\n"

        # Build prompt
        prompt = QA_PROMPT_TEMPLATE.format(
            context=context,
            chat_history=history_str,
            question=question,
        ) if QA_PROMPT_TEMPLATE else (
            f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
        )

        # Generate response
        logger.info("🤖 [Generating] Asking LLM (llama-3.3-70b/Groq) to craft response...")
        answer = generate_response(prompt)

        # Store in history
        self.chat_history.append({
            "question": question,
            "answer": answer,
        })

        # Extract unique sources
        sources = list(set(
            r["metadata"].get("source", "Unknown")
            for r in search_results
        ))

        return {
            "answer": answer,
            "sources": sources,
            "context": context,
            "num_chunks_used": len(search_results),
        }

    def ask_question_stream(
        self,
        question: str,
        n_results: int = 5,
        filter_doc_id: Optional[str] = None,
    ) -> Generator[str, None, None]:
        """Ask a question and stream the answer.

        Args:
            question: The user's question.
            n_results: Number of context chunks to retrieve.
            filter_doc_id: Optional document ID to restrict search.

        Yields:
            Text chunks of the answer as they are generated.
        """
        search_results = self.vector_store.search(
            query=question,
            n_results=n_results,
            filter_doc_id=filter_doc_id,
        )

        context = "\n\n---\n\n".join([r["text"] for r in search_results])

        history_str = ""
        for entry in self.chat_history[-5:]:
            history_str += f"Human: {entry['question']}\nAI: {entry['answer']}\n\n"

        prompt = QA_PROMPT_TEMPLATE.format(
            context=context,
            chat_history=history_str,
            question=question,
        ) if QA_PROMPT_TEMPLATE else (
            f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
        )

        full_answer = ""
        for chunk in generate_response_stream(prompt):
            full_answer += chunk
            yield chunk

        self.chat_history.append({
            "question": question,
            "answer": full_answer,
        })

    def generate_summary(
        self,
        doc_id: str,
        summary_type: str = "detailed",
    ) -> str:
        """Generate a summary of a specific document.

        Args:
            doc_id: Document ID to summarize.
            summary_type: "brief", "detailed", or "key_points".

        Returns:
            Generated summary text.
        """
        results = self.vector_store.search(
            query="summarize the main content",
            n_results=20,
            filter_doc_id=doc_id,
        )

        content = "\n\n".join([r["text"] for r in results])

        prompt = SUMMARY_PROMPT_TEMPLATE.format(
            summary_type=summary_type,
            content=content,
        ) if SUMMARY_PROMPT_TEMPLATE else (
            f"Summarize the following content ({summary_type}):\n\n{content}"
        )

        return generate_response(prompt)

    def clear_history(self) -> None:
        """Clear the conversation history."""
        logger.info("Clearing chat history in QAChain")
        self.chat_history.clear()

    def get_indexed_documents(self) -> List[str]:
        """Get list of all indexed document IDs."""
        return self.vector_store.list_documents()
