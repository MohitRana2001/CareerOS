# Architecture - Phase 1

## Stack
- Frontend: Next.js (App Router), TypeScript, Tailwind, Monaco Editor
- Backend: FastAPI, Pydantic, SQLAlchemy, Alembic
- DB: PostgreSQL
- Cache/Queue: Redis + Celery (or RQ)
- AI: Gemini API (JSON schema constrained outputs)
- File storage: S3-compatible bucket
- PDF compile: containerized LaTeX worker

## Services
- `api`: auth, CRUD, orchestration, signed URLs
- `worker`: extraction, tailoring, ATS scoring, PDF compile, Drive export
- `db`: canonical source of truth
- `redis`: job broker + transient caches

## Data Model Strategy
- Canonical resume format in JSON (`resume_documents.canonical_json`)
- Generated LaTeX stored per version
- Output PDFs tracked by file object and checksum
- Every tailored output linked to JD snapshot and model metadata

## Core Flows
### Upload + Extraction
1. Client uploads source file via signed URL.
2. API creates `resume_documents` row.
3. Worker extracts structured data and initializes base LaTeX.
4. Version `v1` written to `resume_versions`.

### Tailoring
1. User submits JD.
2. API creates `job_descriptions` + `tailor_runs` (PENDING).
3. Worker calls Gemini with strict JSON schema and guardrails.
4. Worker writes new resume version, ATS score, skills gap, and compiled PDF.

### Drive Export
1. User clicks export.
2. Worker uploads PDF to Drive folder.
3. API stores Drive file id and share URL.

## Reliability and Idempotency
- Every async run has `idempotency_key`.
- Retry AI calls with exponential backoff (max 3).
- Dead-letter queue for failed runs.
- Resume compilation errors surfaced with actionable reasons.

## Observability
- Structured logs by `request_id`, `user_id`, `run_id`
- Metrics: run success rate, generation time, ATS delta
- Traces on AI + PDF compile path
