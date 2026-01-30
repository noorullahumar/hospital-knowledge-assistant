import os
import json
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Configuration: Where PDFs are stored and where the processed JSON is saved
DATA_FOLDER = "data"
OUTPUT_FILE = "documents.json"

# Ensure the data directory exists before processing
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

def process_pdf(pdf_path):
    """
    Processes a single PDF by loading text, splitting it into manageable chunks, 
    and appending it to a central documents.json file.
    """
    
    # 1. Load the PDF file using LangChain's PyPDFLoader
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()

    # 2. Define the text splitting logic. 
    # chunk_size: Max characters per chunk.
    # chunk_overlap: Overlap between chunks to maintain context across splits.
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    
    # Apply the split to the loaded document objects
    split_docs = splitter.split_documents(docs)

    # 3. Format the split chunks into a dictionary format for JSON storage
    new_entries = [
        {
            "page_content": doc.page_content,
            "metadata": {
                # Save only the filename (not the full path) for cleaner citations
                "source": os.path.basename(doc.metadata.get("source", "")),
                "page": doc.metadata.get("page", None)
            }
        }
        for doc in split_docs
    ]

    # 4. Handle Persistent Storage: Load existing JSON data if it exists
    existing_docs = []
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            try:
                existing_docs = json.load(f)
            except json.JSONDecodeError:
                # If the file is corrupted or empty, start with an empty list
                existing_docs = []

    # 5. Append new processed chunks to the existing collection
    existing_docs.extend(new_entries)

    # 6. Save the updated list back to the JSON file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        # indent=2 makes the file human-readable
        json.dump(existing_docs, f, ensure_ascii=False, indent=2)

    # Return the count of new chunks added for UI feedback
    return len(split_docs)