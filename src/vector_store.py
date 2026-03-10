"""
Vector Store Module

Manages ChromaDB for storing and retrieving document embeddings.
Handles collection management, document indexing, and similarity search.
"""

import os
import shutil
from typing import List, Dict, Optional

import chromadb
from chromadb.config import Settings

from src.embeddings import generate_embeddings, generate_single_embedding


# Default path for the persistent ChromaDB database
DEFAULT_DB_PATH = os.path.join("data", "chroma_db")
DEFAULT_COLLECTION_NAME = "knowledge_base"


class VectorStore:
    """Manages ChromaDB vector store for document retrieval."""

    def __init__(
        self,
        db_path: Optional[str] = None,
        collection_name: Optional[str] = None,
    ):
        """Initialize the vector store.

        Args:
            db_path: Path to the ChromaDB persistent directory.
            collection_name: Name of the ChromaDB collection.
        """
        self.db_path = db_path or os.getenv("CHROMA_DB_PATH", DEFAULT_DB_PATH)
        self.collection_name = collection_name or DEFAULT_COLLECTION_NAME

        try:
            self.client = chromadb.PersistentClient(path=self.db_path)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        except Exception:
            # If DB is corrupted or incompatible, wipe and retry
            if os.path.exists(self.db_path):
                shutil.rmtree(self.db_path, ignore_errors=True)
                os.makedirs(self.db_path, exist_ok=True)
            self.client = chromadb.PersistentClient(path=self.db_path)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )

    def add_documents(
        self,
        chunks: List[str],
        doc_id: str,
        metadata: Optional[Dict] = None,
    ) -> int:
        """Add document chunks to the vector store.

        Args:
            chunks: List of text chunks from the document.
            doc_id: Unique identifier for the document.
            metadata: Optional metadata dict for the document.

        Returns:
            Number of chunks added.
        """
        if not chunks:
            return 0

        embeddings = generate_embeddings(chunks)

        ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [
            {
                "source": doc_id,
                "chunk_index": i,
                **(metadata or {}),
            }
            for i in range(len(chunks))
        ]

        self._add_with_retry(ids, embeddings, chunks, metadatas)

        return len(chunks)

    def _add_with_retry(self, ids, embeddings, chunks, metadatas):
        """Add to collection, auto-resetting on dimension mismatch."""
        try:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas,
            )
        except Exception as e:
            if "dimension" in str(e).lower():
                # Embedding model changed — reset collection and retry
                self.reset()
                self.collection.add(
                    ids=ids,
                    embeddings=embeddings,
                    documents=chunks,
                    metadatas=metadatas,
                )
            else:
                raise

    def search(
        self,
        query: str,
        n_results: int = 5,
        filter_doc_id: Optional[str] = None,
    ) -> List[Dict]:
        """Search the vector store for relevant document chunks.

        Args:
            query: The search query text.
            n_results: Number of results to return.
            filter_doc_id: Optional document ID to filter results.

        Returns:
            List of result dicts with 'text', 'metadata', and 'distance'.
        """
        query_embedding = generate_single_embedding(query)

        where_filter = {"source": filter_doc_id} if filter_doc_id else None

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_filter,
        )

        formatted_results = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                formatted_results.append({
                    "text": doc,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else None,
                })

        return formatted_results

    def delete_document(self, doc_id: str) -> None:
        """Delete all chunks belonging to a specific document.

        Args:
            doc_id: The document ID whose chunks should be removed.
        """
        self.collection.delete(where={"source": doc_id})

    def get_document_count(self) -> int:
        """Get the total number of chunks in the collection."""
        return self.collection.count()

    def list_documents(self) -> List[str]:
        """List all unique document IDs in the collection."""
        all_metadata = self.collection.get()["metadatas"]
        sources = set()
        for meta in all_metadata:
            if "source" in meta:
                sources.add(meta["source"])
        return sorted(list(sources))

    def reset(self) -> None:
        """Delete the entire collection and recreate it."""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
