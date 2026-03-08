# 8-Week Sprint Plan (Phase 1)

## Week 1-2: Foundation
- Setup FastAPI, Next.js, Postgres, Redis, CI
- Implement Google OAuth + JWT + user isolation middleware
- Build DB schema + migrations

### Acceptance Criteria
- User can sign in with Google and fetch `/auth/me`
- User cannot read/write another user's data
- CI runs lint + tests on PRs

## Week 3-4: Resume Ingestion + Tailoring Core
- Upload flow and extraction job
- Canonical resume JSON + LaTeX generation
- JD ingestion + tailor worker with Gemini

### Acceptance Criteria
- Upload PDF/DOCX and create base resume version
- Tailor run returns status lifecycle and artifact records
- Gemini output passes strict schema validation

## Week 5-6: ATS + Dashboard + Tracker
- ATS scoring and explanation
- Skills gap extraction
- Dashboard list/search/filter
- Application tracker CRUD

### Acceptance Criteria
- ATS endpoint returns score and category breakdown
- Skills gap splits critical vs nice-to-have
- Dashboard supports filter by status/date/company

## Week 7: Drive Export + Hardening
- One-way Drive export integration
- Error handling, retries, dead-letter queue
- Audit logs + version history UX

### Acceptance Criteria
- Exported PDF returns valid Drive share URL
- Failed jobs are visible and retryable
- Resume version history is immutable and queryable

## Week 8: Beta + Launch Readiness
- Beta testing with 10-20 users
- Fix top issues, performance tuning
- Documentation and launch checklist

### Acceptance Criteria
- 90% beta task completion without support
- P95 non-AI endpoint latency < 800ms
- No P0/P1 open issues at release cut
