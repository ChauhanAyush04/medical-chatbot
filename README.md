# Medical ChatBot

Professional medical information chatbot backend + ingestion pipeline with a TypeScript frontend. It provides PDF ingestion → FAISS vector store, a FastAPI backend exposing chat and medical endpoints, and a simple chat session model for storing conversations.

## Stack
- **Language(s):** Python (backend, ML), TypeScript (frontend), CSS, HTML  
- **Framework / runtime:** FastAPI (backend)  
- **Notable libraries:** LangChain, HuggingFace sentence-transformers, FAISS (vector DB), SQLAlchemy, Uvicorn

## What this repo contains
Top-level layout (important entries only):

```
.
├─ app/                      # FastAPI backend
│  ├─ api/                   # HTTP routes and dependency helpers
│  │  └─ routes/             # chat.py, medical.py (API endpoints)
│  ├─ models/                # ORM models (ChatSession, ChatMessage, ...)
│  ├─ schemas/               # Pydantic response/request schemas
│  ├─ services/              # business logic / ML & vectorstore helpers
│  ├─ utils/                 # logging, helpers
│  ├─ database.py            # SQLAlchemy engine, SessionLocal, Base
│  ├─ config.py              # configuration (dotenv)
│  └─ main.py                # application factory & startup (uvicorn entry)
├─ data/                     # PDF documents to ingest (source documents)
├─ ingest.py                 # script to create FAISS vector DB from PDFs
├─ vectorstores/             # saved vector databases (e.g. vectorstores/db_faiss)
├─ frontend/                 # TypeScript frontend (client) — start/build files here
├─ requirements.txt          # Python dependencies for backend + ingestion
└─ .python-version           # (optional) recommended Python version (pyenv)
```

How it fits together:
- ingest.py reads PDFs from data/, splits text into chunks, computes embeddings via HuggingFaceEmbeddings (sentence-transformers/all-MiniLM-L6-v2) and saves a FAISS vectorstore under vectorstores/db_faiss.  
- The FastAPI app (app/main.py) creates DB tables at startup and exposes two main route groups: /api/v1/chat (chat session creation, retrieval, list, delete) and /api/v1/medical (medical-related endpoints). The chat routes persist sessions/messages with SQLAlchemy. The backend connects to the saved vectorstore for retrieval-augmented responses in service logic (services/).

## Quick start — development

Prerequisites:
- Python (use the version in .python-version if you use pyenv)
- Git
- (Optional) GPU-compatible PyTorch if you plan to run large models locally

1. Clone and create venv
```bash
git clone https://github.com/ChauhanAyush04/medical-chatbot.git
cd medical-chatbot
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. Prepare environment
- Create a `.env` file in the project root if needed. The application loads config from `app/config.py` (python-dotenv is installed). Check `app/config.py` for required environment variables (database URL, API keys, etc).

3. Ingest documents to build vector DB (stores to vectorstores/db_faiss)
```bash
python ingest.py
# This will:
#  - load PDFs from data/
#  - split them into chunks
#  - compute embeddings with sentence-transformers/all-MiniLM-L6-v2
#  - save FAISS DB to vectorstores/db_faiss
```

4. Run the API server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- Health check: GET http://localhost:8000/health
- Interactive API docs: http://localhost:8000/docs

## Important backend endpoints (examples)
- Create chat session
  - POST /api/v1/chat/sessions
  - Response: ChatSession object with `session_id`
- Get session with messages
  - GET /api/v1/chat/sessions/{session_id}
- List sessions
  - GET /api/v1/chat/sessions
- Delete session
  - DELETE /api/v1/chat/sessions/{session_id}

Example: create a session with curl
```bash
curl -X POST http://localhost:8000/api/v1/chat/sessions
```

## Notes on persistence & vector store
- SQLAlchemy is used for persistence; tables are created automatically at app startup via `Base.metadata.create_all(bind=engine)` in `app/main.py`.
- The FAISS vectorstore produced by `ingest.py` is saved under `vectorstores/db_faiss` and can be loaded by the service code to perform similarity search / retrieval for medical responses.

## Development tips
- CORS: allowed origins configured in `app/main.py` include the deployed frontend URL and localhost:5173. Adjust as needed for development.
- If you change models/schemas, migrations are not configured in this repo; recreate or manage schema changes manually or add Alembic if needed.
- For faster embeddings, consider running with GPU-enabled PyTorch and changing the embedding model/device in `ingest.py`.

## Troubleshooting
- If ingest fails due to missing PDFs, add PDFs to `data/` and re-run `python ingest.py`.
- Large dependency installs (PyTorch, transformers) may require extra system dependencies. Use the versions pinned in `requirements.txt` or adapt to newer ones carefully.

## Contributing
- Open issues for feature requests or bugs.
- For code changes, follow the repo layout: backend code under app/, ingestion in ingest.py, frontend in frontend/.

## License
- Add a LICENSE file to this repository and state license here (e.g., MIT). If no license is present, default to “All rights reserved.”

## Try asking
- What environment variables does `app/config.py` expect (database URL, API keys)? Where should I set them?
- How does `app/api/routes/medical.py` use the FAISS vectorstore — is retrieval integrated in services/ or inside the route handler?
- What framework and start/build commands are in frontend/ (open `frontend/package.json` to confirm how to run the client)?
