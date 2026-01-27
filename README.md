# 🏥 Hospital Knowledge Assistant

An **AI-powered Retrieval-Augmented Generation (RAG) web application** that allows patients and hospital staff to ask questions and receive accurate answers **strictly based on hospital documents**.

This project demonstrates **secure, production-aware AI engineering** with a focus on healthcare use cases.

---

## 🚀 Live Demo

👉 **[Live Application](https://your-app-link-here.streamlit.app)**
*(Replace with your deployed URL)*

---

## 📌 Key Features

* 🧠 **RAG Architecture** – Answers are generated using retrieved hospital documents
* 🔐 **Secure by Design** – No unsafe pickle deserialization
* 👤 **Role-Based Querying** – Different behavior for Patients vs Hospital Staff
* 📚 **Source Citations** – Every answer includes document references
* 💬 **Chat-Based UI** – Clean, modern Streamlit chat interface
* ⚡ **Fast & Cached** – Optimized with Streamlit caching
* 🏥 **Healthcare-Oriented UX** – Professional and easy to use

---

## 🛠️ Tech Stack

* **Frontend**: Streamlit
* **Backend / RAG**: LangChain
* **Vector Store**: FAISS (in-memory, safe rebuild)
* **LLM**: OpenAI (GPT-4o-mini)
* **Embeddings**: OpenAI Embeddings (`text-embedding-3-large`)
* **Document Loader**: PyPDFLoader
* **Language**: Python

---

## 🧩 Project Architecture

```
PDF Documents
      ↓
Document Loader (PyPDFLoader)
      ↓
Text Splitter
      ↓
Embeddings (OpenAI)
      ↓
FAISS Vector Store (in memory)
      ↓
Retriever
      ↓
LLM (GPT-4o-mini)
      ↓
Streamlit Chat UI
```

---

## 📂 Project Structure

```
hospital-knowledge-assistant/
│
├── app.py              # Streamlit UI
├── ingest.py           # Document ingestion pipeline
├── rag_pipeline.py     # RAG + FAISS logic
├── requirements.txt
├── README.md
├── data/               # PDF documents (ignored in git)
├── documents.json      # Processed chunks (ignored in git)
└── .env                # API keys (ignored in git)
```

---

## ⚙️ Setup & Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/hospital-knowledge-assistant.git
cd hospital-knowledge-assistant
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Environment Variables

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key
```

---

## 📥 Ingest Documents

Place your hospital PDFs inside the `data/` folder and run:

```bash
python ingest.py
```

This will:

* Load PDFs
* Split them into chunks
* Save them safely to `documents.json`

---

## ▶️ Run the Application

```bash
streamlit run app.py
```

Open your browser at:

```
http://localhost:8501
```

---

## 🧪 Example Questions

* "What are the hospital visiting hours?"
* "What documents are required for patient admission?"
* "Explain the emergency room procedure"

---

## 🔐 Security Considerations

* ❌ No pickle-based FAISS loading
* ✅ Safe JSON-based document storage
* ✅ In-memory FAISS rebuild
* 🚫 `.env`, PDFs, and documents.json are excluded from GitHub

---

## ⚠️ Medical Disclaimer

> This application provides informational responses based on hospital documents only.
> It is **not a substitute for professional medical advice, diagnosis, or treatment**.

---

## 🌱 Future Enhancements

* 🔐 User authentication (Doctor / Nurse / Admin)
* 🏥 Department-based retrieval (OPD, ICU, Pharmacy)
* 📊 Answer confidence scoring
* 🧾 Downloadable reports
* 🐳 Docker & cloud deployment

---

## 👤 Author

**Your Name**
IT / Cybersecurity / AI Enthusiast

* GitHub: [https://github.com/your-username](https://github.com/your-username)
* Portfolio: [https://your-portfolio-site.com](https://your-portfolio-site.com)

---

## ⭐ If You Like This Project

Give it a ⭐ on GitHub — it really helps!

---

## 🏁 Final Note

This project showcases **real-world RAG implementation**, secure AI practices, and healthcare-focused design — making it ideal for portfolios, demos, and academic or professional review.
