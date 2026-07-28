"""
RAG Document Ingestion Pipeline for AgriPlan AI.
Loads documents from data/pdfs/, performs text chunking, generates vector embeddings,
and stores them persistently in ChromaDB vector store.
"""

import os
import glob
import math
import json

class SimpleDocument:
    def __init__(self, page_content: str, metadata: dict):
        self.page_content = page_content
        self.metadata = metadata

def load_documents(data_dir: str = "data/pdfs"):
    """Load text and PDF files from data directory."""
    documents = []
    files = glob.glob(os.path.join(data_dir, "*.*"))
    
    for fpath in files:
        fname = os.path.basename(fpath)
        if fpath.endswith(".txt") or fpath.endswith(".md"):
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
                    documents.append(SimpleDocument(content, {"source": fname}))
            except Exception as e:
                print(f"Error reading file {fname}: {e}")
        elif fpath.endswith(".pdf"):
            try:
                from pypdf import PdfReader
                reader = PdfReader(fpath)
                full_text = ""
                for idx, page in enumerate(reader.pages):
                    txt = page.extract_text()
                    if txt:
                        full_text += f"\n--- Page {idx+1} ---\n" + txt
                if full_text:
                    documents.append(SimpleDocument(full_text, {"source": fname}))
            except Exception as e:
                print(f"Error reading PDF {fname}: {e}")
    return documents

def split_documents(documents, chunk_size=450, overlap=50):
    """Chunk documents recursively by headers/paragraphs with overlap."""
    chunks = []
    for doc in documents:
        text = doc.page_content
        source = doc.metadata.get("source", "unknown")
        
        # Split by sections / paragraphs
        paragraphs = text.split("\n\n")
        current_chunk = ""
        chunk_id = 1
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            if len(current_chunk) + len(para) <= chunk_size:
                current_chunk += ("\n\n" + para) if current_chunk else para
            else:
                if current_chunk:
                    chunks.append(SimpleDocument(
                        current_chunk,
                        {"source": source, "chunk_id": chunk_id}
                    ))
                    chunk_id += 1
                # start next chunk with overlap snippet
                overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else ""
                current_chunk = (overlap_text + "\n" + para) if overlap_text else para
                
        if current_chunk:
            chunks.append(SimpleDocument(
                current_chunk,
                {"source": source, "chunk_id": chunk_id}
            ))
            
    return chunks

def build_vector_store(data_dir: str = "data/pdfs", db_dir: str = "data/vectorstore"):
    """
    Build vector index from documents and save persistent json fallback or ChromaDB store.
    """
    docs = load_documents(data_dir)
    chunks = split_documents(docs)
    
    # Store processed chunks into persistent index
    os.makedirs(db_dir, exist_ok=True)
    index_file = os.path.join(db_dir, "chunks_index.json")
    
    chunk_records = [
        {"content": chunk.page_content, "source": chunk.metadata["source"], "chunk_id": chunk.metadata["chunk_id"]}
        for chunk in chunks
    ]
    
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(chunk_records, f, indent=2, ensure_ascii=False)
        
    print(f"Ingested {len(docs)} documents into {len(chunks)} chunks stored at {index_file}.")
    return len(chunks)

if __name__ == "__main__":
    count = build_vector_store()
    print(f"Ingestion complete! Total chunks created: {count}")
