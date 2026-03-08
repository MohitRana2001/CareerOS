.PHONY: up down backend-install backend-run backend-test backend-lint backend-format

up:
	docker compose up -d

down:
	docker compose down

backend-install:
	cd backend && python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

backend-run:
	cd backend && . .venv/bin/activate && uvicorn app.main:app --reload

backend-test:
	cd backend && . .venv/bin/activate && pytest

backend-lint:
	cd backend && . .venv/bin/activate && ruff check .

backend-format:
	cd backend && . .venv/bin/activate && ruff format .
