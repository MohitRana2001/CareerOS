# Phase 1 Implementation Checklist

## Foundation
- [ ] Setup backend service, env config, CI
- [ ] Setup frontend app and shared API client
- [ ] Provision Postgres + Redis + object storage

## Core Features
- [ ] Google OAuth + JWT session
- [ ] Resume upload + extraction pipeline
- [ ] Base LaTeX editor + version history
- [ ] JD ingestion + tailor run orchestration
- [ ] ATS score calculator + explainability
- [ ] Skills gap analysis endpoint/UI
- [ ] Dashboard table with search/filter
- [ ] Application tracker CRUD + notes
- [ ] Drive one-way export

## Hardening
- [ ] Job retries + dead-letter strategy
- [ ] Audit logs + request tracing
- [ ] Security controls from SECURITY_PRIVACY.md
- [ ] Integration tests for critical flows
- [ ] Beta checklist and launch criteria
