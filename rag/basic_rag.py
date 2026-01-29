"""
Basic RAG Pattern

Demonstrates core RAG: chunking, embedding, retrieval, and generation.

Key Production Concerns:
1. Chunk size/overlap: Balance context vs relevance
2. Index freshness: Incremental updates, not full reindex
3. No results handling: Never hallucinate, admit uncertainty
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import hashlib


@dataclass
class Document:
    """A document to be indexed."""
    id: str
    content: str
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Chunk:
    """A chunk of a document with context."""
    id: str
    content: str
    doc_id: str
    start_pos: int
    metadata: Dict


class DocumentChunker:
    """Chunk documents for RAG.
    
    Production Pattern:
    - Fixed token size with overlap to prevent context loss
    - Preserve sentence boundaries when possible
    - Include metadata for filtering and attribution
    """
    
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk(self, doc: Document) -> List[Chunk]:
        """Chunk a document into overlapping segments.
        
        Args:
            doc: Document to chunk
            
        Returns:
            List of chunks with overlap
            
        Production Notes:
        - Use tiktoken for accurate token counting (rough approximation here)
        - Consider semantic chunking (by paragraph/section) for some domains
        - Include source attribution in metadata for citations
        """
        # Simple word-based chunking (production: use tiktoken)
        words = doc.content.split()
        chunks = []
        
        for i in range(0, len(words), self.chunk_size - self.overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_content = " ".join(chunk_words)
            
            chunk_id = f"{doc.id}_chunk_{len(chunks)}"
            chunk = Chunk(
                id=chunk_id,
                content=chunk_content,
                doc_id=doc.id,
                start_pos=i,
                metadata={
                    **doc.metadata,
                    "chunk_index": len(chunks),
                    "total_chunks": -1  # Set after all chunks created
                }
            )
            chunks.append(chunk)
        
        # Update total chunks
        for chunk in chunks:
            chunk.metadata["total_chunks"] = len(chunks)
        
        return chunks


class VectorStore:
    """Simple in-memory vector store.
    
    In production: Use Pinecone, Weaviate, Qdrant, or similar.
    """
    
    def __init__(self):
        self._vectors: List[Tuple[str, List[float], Dict]] = []
    
    def add(self, chunk_id: str, embedding: List[float], metadata: Dict):
        """Add a chunk embedding to the store."""
        self._vectors.append((chunk_id, embedding, metadata))
    
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """Search for similar chunks.
        
        In production: Use proper vector similarity (cosine, dot product).
        This is a mock implementation.
        """
        # Mock: Return first top_k items
        results = []
        for chunk_id, embedding, metadata in self._vectors[:top_k]:
            results.append({
                "chunk_id": chunk_id,
                "score": 0.95,  # Mock score
                "metadata": metadata
            })
        return results


class BasicRAG:
    """Basic RAG system with chunking, embedding, and retrieval.
    
    Production Pattern:
    - Chunk documents with overlap
    - Embed and store in vector DB
    - Retrieve relevant chunks on query
    - Generate response with LLM
    """
    
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunker = DocumentChunker(chunk_size, overlap)
        self.vector_store = VectorStore()
        self._indexed_docs = set()
    
    def index_documents(self, documents: List[Document]):
        """Index documents for retrieval.
        
        Production Notes:
        - Batch embeddings for efficiency
        - Handle updates incrementally, not full reindex
        - Monitor indexing latency and cost
        """
        print(f"Indexing {len(documents)} documents...")
        
        for doc in documents:
            if doc.id in self._indexed_docs:
                print(f"  Skipping already indexed: {doc.id}")
                continue
            
            # Chunk document
            chunks = self.chunker.chunk(doc)
            print(f"  {doc.id}: {len(chunks)} chunks")
            
            # Embed and store chunks
            for chunk in chunks:
                # Mock embedding (production: use real embedding model)
                embedding = self._mock_embed(chunk.content)
                self.vector_store.add(chunk.id, embedding, {
                    "content": chunk.content,
                    "doc_id": chunk.doc_id,
                    **chunk.metadata
                })
            
            self._indexed_docs.add(doc.id)
        
        print(f"Indexed {len(self._indexed_docs)} documents total")
    
    def query(self, query: str, top_k: int = 5) -> Dict:
        """Query the RAG system.
        
        Args:
            query: User query
            top_k: Number of chunks to retrieve
            
        Returns:
            Dict with retrieved chunks and generated response
            
        Production Notes:
        - Handle "no relevant results" gracefully
        - Log query patterns for optimization
        - Monitor latency and cost per query
        """
        print(f"\nQuery: {query}")
        
        # Embed query
        query_embedding = self._mock_embed(query)
        
        # Retrieve relevant chunks
        results = self.vector_store.search(query_embedding, top_k)
        
        if not results:
            return {
                "response": "I don't have enough information to answer that question.",
                "chunks": [],
                "sources": []
            }
        
        # Build context from retrieved chunks
        context = "\n\n".join([
            f"[{i+1}] {r['metadata']['content']}"
            for i, r in enumerate(results)
        ])
        
        # Generate response (production: use real LLM)
        response = self._generate_response(query, context)
        
        # Extract sources for attribution
        sources = list(set([r['metadata']['doc_id'] for r in results]))
        
        return {
            "response": response,
            "chunks": results,
            "sources": sources,
            "num_chunks_used": len(results)
        }
    
    def _mock_embed(self, text: str) -> List[float]:
        """Mock embedding function.
        
        In production: Use OpenAI, Cohere, or local embedding model.
        """
        # Return mock 1536-dim embedding (OpenAI ada-002 dimension)
        return [0.1] * 1536
    
    def _generate_response(self, query: str, context: str) -> str:
        """Generate response from query and context.
        
        In production: Call LLM with proper prompt engineering.
        """
        # Mock response
        return f"Based on the provided context, here's the answer to '{query}'..."


def main():
    """Demonstrate basic RAG pattern."""
    print("=== Basic RAG Pattern ===\n")
    
    # Sample documents
    documents = [
        Document(
            id="doc1",
            content="Our product offers a 30-day money-back guarantee. "
                   "If you're not satisfied, you can request a full refund within 30 days of purchase. "
                   "To initiate a refund, contact our support team at support@example.com.",
            metadata={"source": "refund_policy.txt", "version": "2024-01"}
        ),
        Document(
            id="doc2",
            content="We offer 24/7 customer support through multiple channels. "
                   "You can reach us via email at support@example.com, phone at 1-800-SUPPORT, "
                   "or live chat on our website. Average response time is under 2 hours.",
            metadata={"source": "support_info.txt", "version": "2024-01"}
        ),
    ]
    
    # Initialize RAG system
    rag = BasicRAG(chunk_size=50, overlap=10)  # Small for demo
    
    # Index documents
    rag.index_documents(documents)
    
    # Query examples
    queries = [
        "What is your refund policy?",
        "How can I contact support?",
        "Do you offer international shipping?"  # Not in docs
    ]
    
    for query in queries:
        result = rag.query(query, top_k=3)
        print(f"Response: {result['response']}")
        print(f"Sources: {result['sources']}")
        print(f"Chunks used: {result['num_chunks_used']}")
        print("-" * 50)
    
    print("\n" + "="*50)
    print("\nKey Takeaways:")
    print("1. Chunk size affects retrieval quality - tune for your use case")
    print("2. Overlap prevents context loss at chunk boundaries")
    print("3. Handle 'no results' gracefully - never hallucinate")
    print("4. Always provide source attribution for transparency")
    print("5. Monitor: retrieval quality, latency, and cost per query")


if __name__ == "__main__":
    main()
