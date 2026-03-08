# AI Resume Tailoring Platform - Phase 1 Build Package

This package is the implementation-ready baseline for MVP (Phase 1).

## Scope (Phase 1)
- Resume upload + extraction to canonical JSON
- Base resume template + versioning
- JD-based tailoring (Gemini)
- ATS scoring (transparent breakdown)
- Resume dashboard + application tracker
- Google OAuth + user data isolation
- Google Drive one-way export (upload + share link)
- Skills gap analysis

## Package Contents
- `docs/PRD.md`: MVP product requirements
- `docs/ARCHITECTURE.md`: system design and boundaries
- `docs/API_SPEC.md`: REST endpoints and contracts
- `docs/JOB_WORKERS.md`: async jobs, retries, idempotency
- `docs/SPRINT_PLAN_8_WEEKS.md`: execution plan with acceptance criteria
- `docs/SECURITY_PRIVACY.md`: security and privacy controls
- `backend/db/schema.sql`: PostgreSQL schema for Phase 1
- `backend/app/*`: FastAPI starter skeleton
- `frontend/README.md`: Next.js app skeleton requirements

## MVP Decision
- Drive integration is **one-way export** in Phase 1.
- Two-way Drive sync and Gmail auto-tracking are deferred to Phase 2.

## Immediate Next Steps
1. Bootstrap backend virtualenv and install dependencies.
2. Run PostgreSQL and apply `backend/db/schema.sql`.
3. Implement endpoint logic in router stubs.
4. Stand up Next.js frontend with auth and dashboard flows.

## Local Dev Hygiene
- Start infra: `make up`
- Install backend deps: `make backend-install`
- Run migrations: `make backend-migrate`
- Run API: `make backend-run`
- Lint: `make backend-lint`
- Format: `make backend-format`
- Test: `make backend-test`
