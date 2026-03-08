.PHONY: up down backend-install backend-run backend-test backend-lint backend-format backend-migrate

up:
	docker compose up -d

down:
	docker compose down

backend-install:
	cd backend && python3.13 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

backend-run:
	cd backend && . .venv/bin/activate && uvicorn app.main:app --reload

backend-test:
	cd backend && . .venv/bin/activate && PYTHONPATH=. pytest

backend-lint:
	cd backend && . .venv/bin/activate && PYTHONPATH=. ruff check .

backend-format:
	cd backend && . .venv/bin/activate && PYTHONPATH=. ruff format .

backend-migrate:
	cd backend && . .venv/bin/activate && alembic -c alembic.ini upgrade head
