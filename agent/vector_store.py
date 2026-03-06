"""
🗄️ Vector Store Module
Stores and retrieves article chunks using ChromaDB for RAG.
"""

import os
import uuid
import hashlib
from typing import List, Dict, Optional
import chromadb
from chromadb.utils import embedding_functions


class VectorStore:
    """
    ChromaDB-based vector store for research documents.
    Supports:
    - Adding documents with automatic chunking
    - Semantic similarity search
    - Persistent storage between sessions
    """

    def __init__(self, persist_dir: str = "./chroma_db"):
        self.persist_dir = persist_dir
        os.makedirs(persist_dir, exist_ok=True)

        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(path=persist_dir)

        # Use sentence transformers for embeddings (free, runs locally)
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="research_documents",
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"}
        )

        self.chunk_size = 800   # chars per chunk
        self.chunk_overlap = 100

    def add_documents(self, articles: List[Dict]) -> int:
        """
        Add articles to the vector store with chunking.

        Args:
            articles: List of article dicts with content, title, url

        Returns:
            Number of chunks added
        """
        all_chunks = []
        all_ids = []
        all_metadata = []

        for article in articles:
            content = article.get("content", "")
            if not content:
                continue

            chunks = self._chunk_text(content)

            for i, chunk in enumerate(chunks):
                # Create deterministic ID based on URL + chunk index
                chunk_id = hashlib.md5(
                    f"{article.get('url', '')}_chunk_{i}".encode()
                ).hexdigest()

                all_chunks.append(chunk)
                all_ids.append(chunk_id)
                all_metadata.append({
                    "url": article.get("url", ""),
                    "title": article.get("title", "Unknown"),
                    "domain": article.get("domain", ""),
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                })

        if not all_chunks:
            return 0

        # Add to ChromaDB (in batches to avoid memory issues)
        batch_size = 50
        total_added = 0

        for i in range(0, len(all_chunks), batch_size):
            batch_chunks = all_chunks[i:i + batch_size]
            batch_ids = all_ids[i:i + batch_size]
            batch_meta = all_metadata[i:i + batch_size]

            try:
                # Upsert to handle duplicates
                self.collection.upsert(
                    documents=batch_chunks,
                    ids=batch_ids,
                    metadatas=batch_meta
                )
                total_added += len(batch_chunks)
            except Exception as e:
                print(f"   VectorStore upsert error: {e}")

        return total_added

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search for relevant document chunks using semantic similarity.

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of dicts with content, metadata, and similarity score
        """
        if self.collection.count() == 0:
            return []

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=min(top_k, self.collection.count()),
                include=["documents", "metadatas", "distances"]
            )

            chunks = []
            for i, doc in enumerate(results["documents"][0]):
                meta = results["metadatas"][0][i]
                distance = results["distances"][0][i]
                similarity = 1 - distance  # Convert cosine distance to similarity

                chunks.append({
                    "content": doc,
                    "title": meta.get("title", "Unknown"),
                    "url": meta.get("url", ""),
                    "similarity": round(similarity, 3),
                    "chunk_index": meta.get("chunk_index", 0),
                })

            # Sort by similarity (highest first)
            chunks.sort(key=lambda x: x["similarity"], reverse=True)
            return chunks

        except Exception as e:
            print(f"   VectorStore search error: {e}")
            return []

    def has_documents(self) -> bool:
        """Check if the vector store has any documents."""
        try:
            return self.collection.count() > 0
        except Exception:
            return False

    def clear(self):
        """Clear all documents from the vector store."""
        try:
            self.client.delete_collection("research_documents")
            self.collection = self.client.get_or_create_collection(
                name="research_documents",
                embedding_function=self.embedding_fn,
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            print(f"   VectorStore clear error: {e}")

    def _chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks for better retrieval.

        Args:
            text: Text to chunk

        Returns:
            List of text chunks
        """
        if len(text) <= self.chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size

            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence end near the chunk boundary
                for punct in [". ", "! ", "? ", "\n\n"]:
                    boundary = text.rfind(punct, start + self.chunk_size // 2, end)
                    if boundary != -1:
                        end = boundary + len(punct)
                        break

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end - self.chunk_overlap

        return chunks
