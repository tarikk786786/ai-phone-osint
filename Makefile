.PHONY: help setup backend frontend docker test lint clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Full project setup (backend + frontend)
	@echo "Running full setup..."
	@bash setup.sh

backend: ## Start backend development server
	@echo "Starting FastAPI backend on port 8000..."
	@cd backend && uvicorn app.main:app --reload --port 8000

frontend: ## Start frontend development server
	@echo "Starting Next.js frontend on port 3000..."
	@cd frontend && npm run dev

docker: ## Start all services with Docker Compose
	@echo "Starting Docker Compose services..."
	@docker-compose up -d

docker-down: ## Stop all Docker Compose services
	@docker-compose down

test: ## Run all tests
	@echo "Running backend tests..."
	@cd backend && python -m pytest tests/ -v
	@echo ""
	@echo "Running frontend type check..."
	@cd frontend && npm run typecheck

backend-test: ## Run backend tests only
	@cd backend && python -m pytest tests/ -v

lint: ## Run linters
	@echo "Running backend lint..."
	@cd backend && pip install flake8 && flake8 app/ --max-line-length=100
	@echo ""
	@echo "Running frontend lint..."
	@cd frontend && npm run lint

clean: ## Clean temporary files
	@echo "Cleaning..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@rm -rf frontend/.next frontend/node_modules backend/venv
	@echo "Done."

migrate: ## Run database migrations
	@cd backend && alembic upgrade head

migration: ## Create a new database migration (usage: make migration msg="description")
	@cd backend && alembic revision --autogenerate -m "$(msg)"
