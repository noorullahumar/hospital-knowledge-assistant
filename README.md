# 🏥 Hospital Knowledge Assistant

An **AI-powered Retrieval-Augmented Generation (RAG) web application** that allows patients and hospital staff to ask questions and receive accurate answers **strictly based on hospital documents**.

This project demonstrates **secure, production-aware AI engineering** with a focus on healthcare use cases, ensuring that AI responses are grounded in fact and access is controlled by user roles.

---

## 🚀 Live Demo

👉 **[Access the Live Application](https://hospital-knowledge-assistant-1.streamlit.app/)**

---

## 📌 Key Features

* 🧠 **RAG Architecture** – Answers generated using context retrieved from official hospital PDFs.
* 🔐 **Secure Authentication** – User login and registration powered by **bcrypt** password hashing.
* 👤 **Role-Based Access Control** – Tailored AI behavior for **Patients**, **Staff**, and **Admins**.
* 🛠️ **Secret Admin Tool** – Hidden setup route via URL parameters to provision the first system admin.
* 📚 **Source Citations** – Every answer includes references to the specific document and page used.
* 💬 **Chat-Based UI** – Clean, modern Streamlit interface with persistent session history.
* ⚡ **Fast & Cached** – Optimized performance using Streamlit resource caching.
* 🏥 **Healthcare-Oriented UX** – Custom professional CSS designed for medical environments.

---

## 🛠️ Tech Stack

* **Frontend**: [Streamlit](https://streamlit.io/)
* **Backend / RAG**: [LangChain](https://www.langchain.com/)
* **Vector Store**: [FAISS](https://github.com/facebookresearch/faiss) (In-memory, safe rebuild from JSON)
* **LLM**: OpenAI (**GPT-4o-mini**)
* **Embeddings**: OpenAI Embeddings (**text-embedding-3-small/large**)
* **Database**: SQLite (User Auth & Chat History)
* **Document Loader**: PyPDFLoader
* **Language**: Python 3.9+

---

## 🧩 Project Architecture



1.  **PDF Documents** → Loaded via `PyPDFLoader`.
2.  **Text Splitter** → Chunks documents into manageable pieces for the AI.
3.  **Embeddings** → OpenAI converts text chunks into vector representations.
4.  **FAISS Vector Store** → Stores embeddings in-memory for lightning-fast similarity search.
5.  **Role-Based Prompt Guard** → Injects user role constraints before querying the LLM.
6.  **GPT-4o-mini** → Generates the final answer based only on retrieved context.

---

## 🔐 Secure Password Recovery (OTP)

The portal includes a multi-step password reset flow to ensure account security:

1. **Email Verification:** Users enter their registered email address.
2. **OTP Generation:** The system generates a cryptographically secure 6-digit One-Time Password.
3. **SMTP Integration:** The OTP is sent via Gmail's SMTP server using SSL encryption (Port 465).
4. **Rate Limiting:** A **60-second cooldown timer** is enforced to prevent SMTP spamming and brute-force attempts.
5. **Session Locking:** The reset process is locked to the verified email to prevent cross-account hijacking.

### 📧 Setting up the OTP Mailer
To enable the "Reset Password" button, ensure your `.env` is configured:
- `EMAIL_USER`: Your Gmail address.
- `EMAIL_PASS`: A 16-character **Google App Password**.

### 🎨 Visualizing the flow
User → Requests Reset → System → Sends Email → User → Enters OTP → System → Updates Hashed Password.

---
## 📂 Project Structure

```text
hospital-knowledge-assistant/
│
├── app.py              # Main Application (UI, Routing, Admin Tool)
├── ingest.py           # Document ingestion & chunking pipeline
├── rag_pipeline.py     # RAG logic, FAISS indexing & role-based querying
├── database.py         # SQLite logic for auth and chat history
├── style.py            # Custom CSS for healthcare branding
├── requirements.txt    # Project dependencies
├── data/               # Source PDF documents (Gitignored)
├── documents.json      # Processed document chunks (Gitignored)
├── hospital_users.db   # SQLite database file (Gitignored)
└── .env                # API keys and secrets (Gitignored)

---
⚙️ Setup & Installation
1️⃣ Clone the Repository

---Bash---
git clone [https://github.com/noorullahumar/hospital-knowledge-assistant.git](https://github.com/noorullahumar/hospital-knowledge-assistant.git)
cd hospital-knowledge-assistant

2️⃣ Create Virtual Environment

---Bash---
# Create the environment
python -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
# venv\Scripts\activate

3️⃣ Install Dependencies

---Bash---
pip install -r requirements.txt
4️⃣ Environment Variables
Create a .env file in the root directory:

Paste this inside the .env file
OPENAI_API_KEY=your_actual_openai_api_key

---
📥 Ingestion & Admin Setup
1. Initial Admin Creation:
Run the app and navigate to the setup URL using the secret key defined in your .env file: http://localhost:8501/?setup=YOUR_SECRET_ADMIN_KEY


2. Ingesting Documents
Log in as an Admin.

Use the sidebar to upload PDFs and click "Index Knowledge".

Alternatively, run the ingestion script via CLI:

---Bash---
python ingest.py

▶️ Run the Application

---Bash---
streamlit run app.py
Open your browser at: http://localhost:8501


---


🔐 Security Considerations
✅ No Pickle Loading: FAISS is rebuilt from safe JSON chunks to prevent remote code execution.

✅ Password Hashing: User credentials are encrypted using bcrypt.

✅ Identity Guarding: Role-based instructions are hard-coded into the AI prompt to prevent data leakage.


---
⚠️ Medical Disclaimer
This application provides informational responses based on hospital documents only. It is not a substitute for professional medical advice, diagnosis, or treatment.


---

👤 Author
Noor Ullah Umar IT / Cybersecurity / AI Enthusiast

GitHub: github.com/noorullahumar

Portfolio: your-portfolio-site.com

⭐ Support the Project
If you found this project useful, please give it a ⭐ on GitHub — it helps others find the work!