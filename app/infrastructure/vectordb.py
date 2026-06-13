import os
import uuid
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.config import settings

# ChromaDB optional import fallback
try:
    import chromadb
    from chromadb.utils import embedding_functions
    chroma_available = True
except ImportError:
    chroma_available = False

class BaseVectorDB(ABC):
    @abstractmethod
    async def add_document(self, doc_id: str, text: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        pass

    @abstractmethod
    async def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        pass


class ChromaVectorDB(BaseVectorDB):
    def __init__(self, persist_dir: str, collection_name: str):
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        self._init_client()

    def _init_client(self):
        if not chroma_available:
            return
        
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        # Using default ChromaDB embedding function (downloads a lightweight model)
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function
        )

    async def add_document(self, doc_id: str, text: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        if not chroma_available:
            # InMemory fallback log
            print(f"[Mock VectorDB Add] ID: {doc_id} | Text: {text[:50]}...")
            return

        self.collection.add(
            documents=[text],
            metadatas=[metadata or {}],
            ids=[doc_id]
        )

    async def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        if not chroma_available:
            print(f"[Mock VectorDB Query] '{query}'")
            return []

        results = self.collection.query(
            query_texts=[query],
            n_results=limit
        )

        formatted_results = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if "metadatas" in results and results["metadatas"] else [{}] * len(docs)
            ids = results["ids"][0] if "ids" in results and results["ids"] else [""] * len(docs)
            distances = results["distances"][0] if "distances" in results and results["distances"] else [0.0] * len(docs)
            
            for i in range(len(docs)):
                formatted_results.append({
                    "id": ids[i],
                    "document": docs[i],
                    "metadata": metas[i],
                    "score": float(distances[i])
                })
        return formatted_results


# Simple SQLite fallback or Mock when ChromaDB is not installed
class SimpleVectorDB(BaseVectorDB):
    """Fallback database for environments without ChromaDB binary capability."""
    def __init__(self):
        self.storage: Dict[str, Dict[str, Any]] = {}

    async def add_document(self, doc_id: str, text: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        self.storage[doc_id] = {
            "id": doc_id,
            "document": text,
            "metadata": metadata or {}
        }

    async def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        # Simple substring match ranking for testing
        results = []
        query_words = query.lower().split()
        for doc_id, item in self.storage.items():
            matches = 0
            doc_content = item["document"].lower()
            for word in query_words:
                if word in doc_content:
                    matches += 1
            if matches > 0:
                results.append({
                    "id": doc_id,
                    "document": item["document"],
                    "metadata": item["metadata"],
                    "score": float(matches)
                })
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]


_vector_db_instance: Optional[BaseVectorDB] = None

def get_vector_db() -> BaseVectorDB:
    global _vector_db_instance
    if _vector_db_instance is None:
        if chroma_available:
            _vector_db_instance = ChromaVectorDB(
                persist_dir=settings.CHROMA_PERSIST_DIR,
                collection_name=settings.VECTOR_DB_COLLECTION
            )
        else:
            print("[Warning] ChromaDB is not available. Using local in-memory substring-search fallback.")
            _vector_db_instance = SimpleVectorDB()
    return _vector_db_instance
