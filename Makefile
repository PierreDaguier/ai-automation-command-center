.PHONY: help
help:
	@echo "Available targets: backend-dev, backend-test, frontend-dev, frontend-build, up, down"

.PHONY: backend-dev
backend-dev:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

.PHONY: backend-test
backend-test:
	cd backend && pytest -q

.PHONY: frontend-dev
frontend-dev:
	cd frontend && npm run dev

.PHONY: frontend-build
frontend-build:
	cd frontend && npm run build

.PHONY: up
up:
	docker compose up -d --build

.PHONY: down
down:
	docker compose down --remove-orphans
