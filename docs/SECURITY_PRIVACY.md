# Security and Privacy - Phase 1

## Data Protection
- Encrypt data in transit (TLS) and at rest (DB + object storage)
- Store OAuth tokens encrypted with KMS-backed keys
- Strip PII from logs; never log resume raw content by default

## Access Control
- Mandatory user_id filters on every query
- DB row-level security recommended where feasible
- Signed URLs short-lived and single-purpose

## Secrets
- Secrets in secure manager only; no plaintext in repo
- Rotate Gemini, OAuth, Drive credentials quarterly

## AI Safety Controls
- Prompt templates include non-fabrication constraints
- JSON-schema validation on model output
- Reject outputs with unverifiable claims or missing traceability

## Compliance Readiness
- Data export + delete endpoints
- Consent for Gmail/Drive scopes with clear purpose text
- Audit events for login, export, and data mutation
