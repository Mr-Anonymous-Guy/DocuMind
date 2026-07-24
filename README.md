# DocuMind

**DocuMind** is a professional AI-powered document intelligence platform built with Python, Streamlit, LangChain, FAISS, and Ollama. 

It allows users to create searchable knowledge bases from documents and interact with them using local Retrieval-Augmented Generation (RAG).

## Features
- **Workspace System**: Organize documents into Collections.
- **Multi-document RAG**: Upload PDF, DOCX, TXT, and Markdown files.
- **Privacy First**: Uses local Ollama LLMs and Embeddings (no data leaves your machine).
- **Citation-based Answers**: Responses include exact citations mapping back to your documents.
- **AI Productivity Tools**: Generate executive summaries, flashcards, and quizzes.

## Tech Stack
- **Frontend**: Streamlit
- **Backend Core**: Python, SQLAlchemy, LangChain
- **Vector Storage**: FAISS
- **Metadata Storage**: SQLite
- **LLM Engine**: Ollama (`llama3`, `nomic-embed-text`)
- **Document Parsers**: PyMuPDF, python-docx, pdfplumber

## Setup

1. **Install Ollama**: Download from [ollama.ai](https://ollama.ai/)
2. **Pull Required Models**:
   ```bash
   ollama run llama3
   ollama pull nomic-embed-text
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run Application**:
   - Windows: `run.bat`
   - Linux/Mac: `./run.sh` or `make run`
   
## Architecture
The application follows a clean architectural pattern:
- `src/ai/`: Wrappers for LangChain Ollama inference.
- `src/document/`: Loaders and chunkers for handling raw files.
- `src/retrieval/`: RAG engine orchestrating FAISS semantic search and LLM context building.
- `src/services/`: High-level business logic orchestrators.
- `src/storage/`: SQLite and FAISS database managers.
- `app/`: Streamlit UI layer.
