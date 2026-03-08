# Backend (FastAPI) - Starter

## Run Locally
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Tooling
```bash
ruff check .
ruff format .
pytest
```

## Database
Apply `db/schema.sql` to a PostgreSQL instance named `resume_tailor`.

## Environment
Copy `.env.example` to `.env` and update values as needed.

## Next Implementation Targets
1. Auth middleware + user context
2. SQLAlchemy models + Alembic migrations
3. End-to-end flow: upload -> extract -> tailor -> ATS -> dashboard
