# AI Document SaaS Backend

A FastAPI-based backend service for AI-powered document processing and chat functionality using RAG (Retrieval-Augmented Generation).

## Features

- User authentication and authorization
- Document upload and processing (PDF, TXT, DOCX, MD)
- Text extraction and chunking
- Vector embeddings using OpenAI
- FAISS vector store for similarity search
- RAG-based chat with document context
- RESTful API with FastAPI

## Quick Start

### Using Make (Recommended)

**Local Development:**
```bash
make dev
```

**Docker:**
```bash
make up    # Start containers
make down  # Stop containers
```

**Other Commands:**
```bash
make help      # Show all available commands
make install   # Install dependencies only
make init-db   # Initialize database tables
make clean     # Clean up generated files
```

### Manual Setup

1. **Create virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Initialize database:**
```bash
make init-db
# or
python init_db.py
```

5. **Run the application:**
```bash
make dev
# or
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Docker Setup

```bash
# Start all services
make up

# Stop all services
make down

# Or manually
docker-compose up --build
docker-compose down
```

The API will be available at `http://localhost:8000`

## Project Structure

```
ai_backend/
│
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection and session
│   ├── dependencies.py      # FastAPI dependencies
│   │
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── routers/             # API route handlers
│   ├── services/            # Business logic services
│   ├── utils/               # Utility functions
│   └── vector_store/        # FAISS index storage
│
├── migrations/              # Database migrations
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose setup
├── Makefile                 # Make commands
├── .env                     # Environment variables
└── README.md                # This file
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and get access token
- `GET /api/auth/me` - Get current user info

### Documents
- `POST /api/documents/upload` - Upload a document
- `GET /api/documents/` - Get all user documents
- `GET /api/documents/{id}` - Get a specific document
- `DELETE /api/documents/{id}` - Delete a document

### Chat
- `POST /api/chat/` - Create a chat interaction
- `GET /api/chat/` - Get all chats
- `GET /api/chat/{id}` - Get a specific chat

## Environment Variables

See `.env` file for all configurable environment variables.

## Prerequisites

- Python 3.11+ (Python 3.14 recommended)
- PostgreSQL
- OpenAI API key

## License

MIT
