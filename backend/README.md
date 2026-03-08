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
Or run Alembic for Week 1 core tables:
```bash
alembic -c alembic.ini upgrade head
```

## Environment
Copy `.env.example` to `.env` and update values as needed.
- `GOOGLE_CLIENT_ID` is required for secure Google token verification.
- `GEMINI_API_KEY` is required for tailoring worker execution.
- `ALLOW_DEV_AUTH_HEADER` should be `false` outside local development.

## Next Implementation Targets
1. Auth middleware + user context
2. SQLAlchemy models + Alembic migrations
3. End-to-end flow: upload -> extract -> tailor -> ATS -> dashboard
