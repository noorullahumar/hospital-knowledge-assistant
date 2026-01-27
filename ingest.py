# Standard library imports
import os
import json

# Load environment variables from .env file
from dotenv import load_dotenv

# LangChain PDF loader for extracting text from PDFs
from langchain_community.document_loaders import PyPDFLoader

# Text splitter optimized for RAG pipelines
from langchain_text_splitters import RecursiveCharacterTextSplitter


# Load environment variables (e.g., API keys if needed later)
load_dotenv()


# ========= CONFIG =========
# Folder containing all source PDF files
DATA_FOLDER = "data"

# Output file where processed documents will be saved
OUTPUT_FILE = "documents.json"

# List of PDF files to ingest into the knowledge base
PDF_FILES = [
    "hospital_knowledge.pdf",
    "medical_records.pdf",
    # add more PDFs here
]
# ==========================


def ingest_documents():
    """
    Loads PDF files, extracts text, splits it into chunks,
    and saves the result as a safe JSON file for RAG usage.
    """
    all_docs = []

    # 1️⃣ Load all PDFs
    for pdf_name in PDF_FILES:
        # Build full file path
        pdf_path = os.path.join(DATA_FOLDER, pdf_name)

        # Ensure the PDF exists
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"❌ Missing file: {pdf_path}")

        # Load PDF using LangChain loader
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()

        # Validate extracted text
        if not docs:
            raise ValueError(f"❌ No text extracted from {pdf_name}")

        # Accumulate documents from all PDFs
        all_docs.extend(docs)

    print(f"📄 Loaded {len(all_docs)} pages from PDFs")

    # 🔍 DEBUG (IMPORTANT – remove later)
    # Shows sample extracted text to verify correctness
    print("\n--- SAMPLE TEXT ---")
    print(all_docs[0].page_content[:500])
    print("-------------------\n")

    # 2️⃣ Split into chunks (RAG-optimized)
    # Smaller overlapping chunks improve retrieval accuracy
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,            # Max characters per chunk
        chunk_overlap=150,         # Overlap to preserve context
        separators=["\n\n", "\n", ".", " ", ""]
    )

    # Split full documents into smaller chunks
    split_docs = splitter.split_documents(all_docs)

    if not split_docs:
        raise ValueError("❌ Text splitting failed")

    print(f"✂️ Split into {len(split_docs)} chunks")

    # 3️⃣ Save SAFE JSON (NO PICKLE)
    # JSON is portable, secure, and production-friendly
    safe_docs = [
        {
            "page_content": doc.page_content,  # Text chunk
            "metadata": {
                "source": os.path.basename(doc.metadata.get("source", "")),
                "page": doc.metadata.get("page", None)
            }
        }
        for doc in split_docs
    ]

    # Write processed documents to JSON file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(
            safe_docs,
            f,
            ensure_ascii=False,
            indent=2
        )

    print(f"✅ Ingestion complete")
    print(f"📦 Saved to {OUTPUT_FILE}")


# Entry point for running this file directly
if __name__ == "__main__":
    ingest_documents()
