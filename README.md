🏥 Hospital Knowledge Assistant

A secure AI-powered Hospital Knowledge Assistant built using Retrieval-Augmented Generation (RAG).
It allows patients, hospital staff, and admins to ask questions and receive accurate answers strictly based on hospital documents.

This project focuses on real-world AI systems, security, and healthcare-safe design.

🚀 Live Demo

👉 Live Application

(Replace with your deployed Streamlit URL)

📌 Key Features

🧠 RAG Architecture – Answers generated only from hospital PDFs

🔐 Authentication System – Secure login with bcrypt password hashing

👥 Role-Based Access Control

Patient – General information

Staff – Professional hospital data

Admin – Full access + document ingestion

💬 Chat-Based Interface – Modern Streamlit chat UI

🗂️ Multi-Session Chat History – Persistent conversations per user

📚 Source-Grounded Answers – No hallucinated responses

⚡ Fast & Cached – Optimized using Streamlit caching

🎨 Healthcare UI – Custom CSS with hospital-themed design

🛠️ Tech Stack

Frontend: Streamlit

Backend / RAG: LangChain

Vector Store: FAISS (in-memory, safe rebuild)

LLM: OpenAI (GPT-4o-mini)

Embeddings: OpenAI Embeddings

Database: SQLite

Authentication: bcrypt

Document Loader: PyPDFLoader

Language: Python

🧩 Project Architecture
Hospital PDFs
      ↓
PyPDFLoader
      ↓
Text Splitter
      ↓
JSON Storage (documents.json)
      ↓
Embeddings (OpenAI)
      ↓
FAISS Vector Store (In-Memory)
      ↓
Retriever (k=3)
      ↓
GPT-4o-mini
      ↓
Role-Based Prompt Guard
      ↓
Streamlit Chat UI

📂 Project Structure
hospital-knowledge-assistant/
│
├── app.py              # Streamlit UI + routing + auth
├── ingest.py           # PDF ingestion & chunking
├── rag_pipeline.py     # RAG + FAISS logic
├── database.py         # SQLite auth & chat history
├── style.py            # Custom Streamlit CSS
├── requirements.txt
├── README.md
│
├── data/               # Hospital PDFs (gitignored)
├── documents.json      # Processed chunks (gitignored)
├── hospital_users.db   # SQLite DB (gitignored)
└── .env                # API keys (gitignored)

⚙️ Setup & Installation
1️⃣ Clone Repository
git clone https://github.com/your-username/hospital-knowledge-assistant.git
cd hospital-knowledge-assistant

2️⃣ Create Virtual Environment
python -m venv venv
source venv/bin/activate     # Windows: venv\Scripts\activate

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Environment Variables

Create a .env file:

OPENAI_API_KEY=your_openai_api_key

📥 Ingest Hospital Documents (Admin)
Option 1: Upload via Admin Dashboard

Login as Admin

Upload PDF from sidebar

Click Index Knowledge

Option 2: CLI Ingestion
python ingest.py


This will:

Load hospital PDFs

Split them into chunks

Store them safely in documents.json

▶️ Run the Application
streamlit run app.py


Open in browser:

http://localhost:8501

🧪 Example Questions

“What are the hospital visiting hours?”

“What documents are required for patient admission?”

“Explain emergency room procedures”

“What is the OPD workflow?”

🐳 Docker Support
Build Image
docker build -t hospital-ai .

Run Container
docker run -p 8501:8501 --env-file .env hospital-ai

🔐 Security Considerations

❌ No pickle-based FAISS loading

✅ bcrypt password hashing

✅ Role-based prompt protection

✅ JSON-based document storage

✅ In-memory FAISS rebuild only

🚫 .env, PDFs, DB, and documents.json excluded from GitHub

⚠️ Medical Disclaimer

This application provides informational responses based only on hospital documents.
It is not a substitute for professional medical advice, diagnosis, or treatment.

🌱 Future Enhancements

🔐 JWT / OAuth authentication

🏥 Department-based retrieval (OPD, ICU, Pharmacy)

📊 Answer confidence scoring

🧾 Export chat reports (PDF)

☁️ Cloud vector databases

🐳 Full Docker Compose deployment

👤 Author

Your Name
IT | Cybersecurity | AI Enthusiast

GitHub: https://github.com/your-username

Portfolio: https://your-portfolio-site.com

⭐ Support the Project

If you like this project, give it a ⭐ — it really helps!