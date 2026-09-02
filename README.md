# 🤖 Smart AI Assistant

A RAG-based AI assistant that allows users to upload PDF documents and ask questions about their content. The application retrieves relevant information from the uploaded document and uses an LLM to generate context-aware answers.

## 🚀 Features

- 📄 Upload and process PDF documents
- ✂️ Split PDF text into smaller chunks
- 🧠 Generate semantic embeddings using Hugging Face
- 🔎 Retrieve relevant document content using FAISS
- 🤖 Generate answers using Groq LLM
- 💬 Interactive chat interface using Streamlit
- 🗂️ Multiple chat conversations
- 💾 Persistent chat history
- ⚡ Document processing optimization
- 🛡️ Error handling and input validation

## 🛠️ Technologies Used

- Python
- Streamlit
- LangChain
- Groq API
- Hugging Face Embeddings
- FAISS
- PyPDF
- JSON
- Git & GitHub

## 🧩 RAG Architecture

The application follows a Retrieval-Augmented Generation (RAG) pipeline:

PDF Upload
   ↓
PDF Text Extraction
   ↓
Text Chunking
   ↓
Hugging Face Embeddings
   ↓
FAISS Vector Database
   ↓
Similarity Search
   ↓
Relevant Context
   ↓
Groq LLM
   ↓
AI Generated Answer

## 📂 Project Structure

```text
Smart-Ai-Assitant/
│
├── app.py
├── chat_manager.py
├── chat_storage.py
├── utils.py
├── requirements.txt
├── README.md
├── .gitignore
│
└── rag/
    ├── __init__.py
    ├── pdf_processor.py
    ├── embeddings.py
    └── retriever.py
