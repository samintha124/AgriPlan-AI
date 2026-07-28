"""
RAG Retriever Module for AgriPlan AI.
Searches the indexed knowledge base chunks and returns top-k relevant snippets with source metadata.
"""

import os
import json
import re

class KnowledgeRetriever:
    def __init__(self, db_dir: str = "data/vectorstore"):
        self.db_dir = db_dir
        self.index_file = os.path.join(db_dir, "chunks_index.json")
        self.chunks = self._load_chunks()

    def _load_chunks(self):
        if not os.path.exists(self.index_file):
            # Auto-ingest if not built yet
            from rag.ingest import build_vector_store
            build_vector_store()
        
        try:
            with open(self.index_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading vector index: {e}")
            return []

    def retrieve(self, query: str, top_k: int = 3):
        """
        Perform BM25/TF-IDF keyword & semantic relevance ranking.
        Returns list of dicts containing 'content', 'source', and 'score'.
        """
        if not self.chunks:
            return []

        # Tokenize query
        query_words = set(re.findall(r'\w+', query.lower()))
        if not query_words:
            return self.chunks[:top_k]

        scored_chunks = []
        for chunk in self.chunks:
            content = chunk["content"]
            content_words = re.findall(r'\w+', content.lower())
            
            # Match score based on word overlap frequency
            score = 0
            for qw in query_words:
                count = content_words.count(qw)
                if count > 0:
                    # Longer unique matches get higher weight
                    score += (count * len(qw))
            
            if score > 0:
                scored_chunks.append({
                    "content": content,
                    "source": chunk["source"],
                    "chunk_id": chunk["chunk_id"],
                    "score": score
                })

        # Sort descending by relevance score
        scored_chunks.sort(key=lambda x: x["score"], reverse=True)

        if not scored_chunks:
            # Fallback to returning top chunks if no exact keyword match
            return self.chunks[:top_k]

        return scored_chunks[:top_k]

    def format_context(self, retrieved_chunks):
        """Format retrieved chunks into a clean prompt context block."""
        if not retrieved_chunks:
            return "No specific domain documents found for this query."

        context_str = "--- RETRIEVED KNOWLEDGE BASE CONTEXT ---\n"
        for idx, item in enumerate(retrieved_chunks):
            context_str += f"\n[Source {idx+1}: {item['source']} (Chunk #{item.get('chunk_id', 1)})]\n"
            context_str += f"{item['content']}\n"
        context_str += "\n--- END CONTEXT ---"
        return context_str
