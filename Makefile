.PHONY: help dev up down install clean init-db test

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

dev: ## Run development server locally
	@echo "🚀 Starting development server..."
	@if [ ! -d "venv" ]; then \
		echo "📦 Creating virtual environment..."; \
		python3 -m venv venv; \
	fi
	@echo "🔌 Activating virtual environment..."
	@bash -c '. venv/bin/activate && \
		pip install --upgrade pip --quiet && \
		if ! python -c "import fastapi, uvicorn" 2>/dev/null; then \
			echo "📥 Installing dependencies (this may take a while)..."; \
			pip install "shapely>=2.0.0,<3.0.0" 2>/dev/null || true; \
			pip install --upgrade -r requirements.txt || echo "⚠️  Some dependencies may have failed to install, but continuing..."; \
		else \
			echo "✅ Dependencies already installed, skipping installation..."; \
		fi && \
		mkdir -p uploads vector_store/faiss_index && \
		python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload'

install: ## Install dependencies
	@echo "📥 Installing dependencies..."
	@if [ ! -d "venv" ]; then \
		echo "📦 Creating virtual environment..."; \
		python3 -m venv venv; \
	fi
	@. venv/bin/activate && \
		pip install --upgrade pip && \
		pip install --upgrade -r requirements.txt

init-db: ## Initialize database tables
	@echo "🗄️  Initializing database..."
	@. venv/bin/activate && python init_db.py

up: ## Start Docker containers
	@echo "🐳 Starting Docker containers..."
	docker-compose up --build

down: ## Stop Docker containers
	@echo "🛑 Stopping Docker containers..."
	docker-compose down

clean: ## Clean up generated files
	@echo "🧹 Cleaning up..."
	rm -rf venv
	rm -rf __pycache__
	rm -rf */__pycache__
	rm -rf */*/__pycache__
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

test: ## Run tests
	@echo "🧪 Running tests..."
	@if [ ! -d "venv" ]; then \
		echo "❌ Virtual environment not found. Run 'make install' first."; \
		exit 1; \
	fi
	@. venv/bin/activate && \
		if ! python -c "import pytest" 2>/dev/null; then \
			echo "📥 Installing test dependencies..."; \
			pip install pytest pytest-asyncio pytest-cov pytest-mock; \
		fi && \
		pytest

