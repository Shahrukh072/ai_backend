# Quick Start Guide

## 5-Minute Setup

### Step 1: Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### Step 2: Configure Environment

Create `.env` file:

```bash
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/ai_backend
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key
LLM_PROVIDER=openai
```

### Step 3: Setup Database

```bash
# Create database
createdb ai_backend

# Initialize schema
python init_db.py
```

### Step 4: Run Application

```bash
uvicorn app.main:app --reload
```

### Step 5: Test API

```bash
# Health check
curl http://localhost:8000/health

# View API docs
open http://localhost:8000/docs
```

## First Chat Request

### Register User

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword",
    "full_name": "Test User"
  }'
```

### Login

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=testpassword"
```

### Create Chat

```bash
curl -X POST "http://localhost:8000/api/chat/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Hello, how are you?",
    "document_id": null
  }'
```

## Key Features to Try

### 1. Agentic Workflow

```bash
curl -X POST "http://localhost:8000/api/chat/agent" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Calculate 10 * 5 and search for information about Python",
    "document_id": null
  }'
```

### 2. WebSocket Chat

```javascript
const ws = new WebSocket('ws://localhost:8000/api/chat/ws/1');
ws.onmessage = (e) => console.log(JSON.parse(e.data));
ws.send(JSON.stringify({message: "Hello!"}));
```

### 3. Document Upload & RAG

```bash
# Upload document
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf"

# Chat with document context
curl -X POST "http://localhost:8000/api/chat/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is in my document?",
    "document_id": 1
  }'
```

## Common Commands

```bash
# Run tests
pytest

# Format code
black app/

# Check types
mypy app/

# Run with Docker
docker-compose up
```

## Next Steps

1. Read [Full Setup Guide](./SETUP.md)
2. Explore [Architecture](./ARCHITECTURE.md)
3. Review [API Documentation](./API.md)
4. Check example code in `app/services/`

