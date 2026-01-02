# Setup Guide

## Quick Start

### 1. Prerequisites Installation

#### macOS

```bash
# Install Python 3.11+
brew install python@3.11

# Install PostgreSQL
brew install postgresql@14
brew services start postgresql@14

# Install Git
brew install git
```

#### Linux (Ubuntu/Debian)

```bash
# Install Python 3.11+
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql

# Install Git
sudo apt install git
```

#### Windows

1. Install Python 3.11+ from [python.org](https://www.python.org/downloads/)
2. Install PostgreSQL from [postgresql.org](https://www.postgresql.org/download/windows/)
3. Install Git from [git-scm.com](https://git-scm.com/download/win)

### 2. Project Setup

```bash
# Clone repository
git clone <your-repo-url>
cd ai_backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Database Setup

```bash
# Create database
createdb ai_backend

# Or using PostgreSQL CLI
psql -U postgres
CREATE DATABASE ai_backend;
\q

# Initialize database schema
python init_db.py
```

### 4. Environment Configuration

Create `.env` file:

```bash
cp .env.example .env
# Edit .env with your configuration
```

Minimum required variables:

```bash
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/ai_backend
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key
```

### 5. Run Application

```bash
# Development mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Or using Make
make dev
```

### 6. Verify Installation

```bash
# Health check
curl http://localhost:8000/health

# API docs
open http://localhost:8000/docs
```

## Provider-Specific Setup

### OpenAI Setup

1. Get API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Add to `.env`:
   ```bash
   LLM_PROVIDER=openai
   OPENAI_API_KEY=sk-...
   OPENAI_MODEL=gpt-4o
   ```

### Vertex AI Setup

1. Install Google Cloud SDK:
   ```bash
   # macOS
   brew install google-cloud-sdk
   
   # Linux
   curl https://sdk.cloud.google.com | bash
   ```

2. Authenticate:
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

3. Set project:
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

4. Enable Vertex AI API:
   ```bash
   gcloud services enable aiplatform.googleapis.com
   ```

5. Add to `.env`:
   ```bash
   LLM_PROVIDER=vertex_ai
   GOOGLE_CLOUD_PROJECT=your-project-id
   GOOGLE_CLOUD_LOCATION=us-central1
   ```

### AWS Bedrock Setup

1. Install AWS CLI:
   ```bash
   # macOS
   brew install awscli
   
   # Linux
   pip install awscli
   ```

2. Configure credentials:
   ```bash
   aws configure
   ```

3. Enable Bedrock in your region:
   - Go to AWS Console → Bedrock
   - Enable model access

4. Add to `.env`:
   ```bash
   LLM_PROVIDER=aws_bedrock
   AWS_REGION=us-east-1
   AWS_ACCESS_KEY_ID=your-key
   AWS_SECRET_ACCESS_KEY=your-secret
   BEDROCK_MODEL=anthropic.claude-3-5-sonnet-20241022-v2:0
   ```

### LangSmith Setup

1. Get API key from [LangSmith](https://smith.langchain.com/)
2. Add to `.env`:
   ```bash
   LANGSMITH_API_KEY=your-key
   LANGSMITH_PROJECT=ai-backend
   LANGSMITH_TRACING=true
   ```

## Docker Setup

### Build and Run

```bash
# Build image
docker build -t ai-backend .

# Run container
docker run -p 8000:8000 --env-file .env ai-backend

# Or using docker-compose
docker-compose up --build
```

### Docker Compose

The `docker-compose.yml` includes:
- Application container
- PostgreSQL database
- Volume mounts for persistence

## Kubernetes Setup

### Prerequisites

- Kubernetes cluster (GKE, EKS, or local)
- kubectl configured
- Helm (optional)

### Deploy

```bash
# Apply manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Or using Helm (if charts available)
helm install ai-backend ./helm/ai-backend
```

## Development Setup

### IDE Configuration

#### VS Code

1. Install Python extension
2. Select Python interpreter: `venv/bin/python`
3. Install recommended extensions:
   - Python
   - Pylance
   - Black Formatter
   - pytest

#### PyCharm

1. Open project
2. Configure interpreter: `venv/bin/python`
3. Enable pytest integration

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install
```

### Code Formatting

```bash
# Format code
black app/ tests/

# Check formatting
black --check app/ tests/
```

### Linting

```bash
# Run linter
flake8 app/ tests/

# Type checking
mypy app/
```

## Testing Setup

### Run Tests

```bash
# All tests
pytest

# Specific test
pytest tests/test_agent_service.py

# With coverage
pytest --cov=app --cov-report=html

# Watch mode
pytest-watch
```

### Test Database

Tests use a separate test database or in-memory SQLite:

```bash
# Set test database URL
export TEST_DATABASE_URL=sqlite:///./test.db
```

## Troubleshooting

### Common Issues

#### Database Connection Error

```bash
# Check PostgreSQL is running
pg_isready

# Check connection
psql -U postgres -d ai_backend
```

#### Import Errors

```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

#### Port Already in Use

```bash
# Find process
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8001
```

#### Vector Store Errors

```bash
# Clear vector store
rm -rf vector_store/

# Recreate
mkdir -p vector_store/faiss_index
```

### Getting Help

1. Check logs: `tail -f logs/app.log`
2. Check API docs: `http://localhost:8000/docs`
3. Review error messages
4. Check GitHub issues

## Production Checklist

- [ ] Set strong `SECRET_KEY`
- [ ] Configure production database
- [ ] Set up proper CORS origins
- [ ] Enable HTTPS
- [ ] Set up monitoring
- [ ] Configure backup strategy
- [ ] Set resource limits
- [ ] Enable rate limiting
- [ ] Set up logging aggregation
- [ ] Configure alerting

## Next Steps

1. Read [Architecture Documentation](./ARCHITECTURE.md)
2. Review [API Documentation](./API.md)
3. Explore example code
4. Set up CI/CD pipeline
5. Deploy to staging environment

