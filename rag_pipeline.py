# Standard library import for working with JSON files
import json

# LangChain Document schema to wrap text + metadata
from langchain_classic.schema import Document

# FAISS vector store for fast similarity search
from langchain_community.vectorstores import FAISS

# OpenAI embeddings for converting text into vectors
from langchain_community.embeddings.openai import OpenAIEmbeddings

# RetrievalQA chain for RAG (Retrieval-Augmented Generation)
from langchain_classic.chains import RetrievalQA

# Chat-based OpenAI LLM
from langchain_community.chat_models import ChatOpenAI

# Loads environment variables from a .env file (e.g., OPENAI_API_KEY)
from dotenv import load_dotenv

# Load environment variables at startup
load_dotenv()

# Path to the JSON file containing documents
DOC_FILE = "documents.json"


def load_documents():
    """
    Loads documents from a JSON file and converts them
    into LangChain Document objects.
    """
    # Open and read the JSON document file
    with open(DOC_FILE, "r", encoding="utf-8") as f:
        raw_docs = json.load(f)

    # Convert each JSON object into a Document
    documents = [
        Document(
            page_content=d["page_content"],  # Main text content
            metadata=d["metadata"]            # Extra information (source, type, etc.)
        )
        for d in raw_docs
    ]

    return documents


def build_qa_chain():
    """
    Builds and returns a RetrievalQA chain using:
    - FAISS vector store
    - OpenAI embeddings
    - Chat-based LLM
    """
    # Load documents from JSON
    documents = load_documents()

    # Initialize OpenAI embeddings
    embeddings = OpenAIEmbeddings()

    # Create a FAISS vector store from documents
    vectorstore = FAISS.from_documents(documents, embeddings)

    # Initialize the chat-based LLM
    llm = ChatOpenAI(
        temperature=0,             # Deterministic output
        model="gpt-4o-mini"        # Fast and cost-effective model
    )

    # Create a RetrievalQA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),  # Top 3 matches
        return_source_documents=True  # Return documents used in the answer
    )

    return qa_chain


# ---------- Role-based query wrapper for RAG ----------

def role_based_query(qa_chain, query, role="Patient"):
    """
    Executes a role-aware RAG query.

    Roles:
    - Patient: Cannot access other patients' medical records
    - Staff: Full access to medical records
    """
    # Inject role-based rules directly into the prompt
    query_with_role = f"""
    You are a hospital assistant.
    User role: {role}

    Rules:
    - If Patient: do NOT reveal private medical records of others
    - If Staff: you may answer using medical records
    - Be accurate and concise

    Question: {query}
    """

    # Run the query through the RetrievalQA chain
    return qa_chain(query_with_role)
