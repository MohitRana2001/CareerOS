# PRD - Phase 1 MVP

## Problem
Job seekers spend 1-2 hours tailoring a resume per role with inconsistent quality and weak ATS alignment.

## Goal
Reduce tailoring time to <5 minutes per application and improve ATS alignment quality.

## Personas
- Active software job seekers
- Career switchers
- Fresh graduates
- International applicants

## Core User Journey
1. User signs in with Google.
2. Uploads base resume (PDF/DOCX).
3. System extracts content into canonical resume JSON and LaTeX source.
4. User pastes JD (text/URL).
5. System generates tailored resume + ATS score + skills gap.
6. User exports PDF to local/Drive and tracks application status.

## In-Scope Features (MVP)
1. Resume upload + base template management + version history
2. JD-based resume tailoring via Gemini
3. ATS score calculator with breakdown
4. Resume dashboard (search/filter/status)
5. Google Drive one-way export
6. Skills gap analysis (critical vs nice-to-have)
7. Basic application tracker
8. Auth + encrypted data + strict user isolation

## Out of Scope (Phase 2+)
- Gmail auto-tracking
- Cover letter generator
- Batch processing
- Chrome extension
- Notion sync

## Non-Functional Requirements
- P95 API latency: <800ms for non-AI endpoints
- Async AI generation reliability: >99%
- Data isolation: user-scoped access everywhere
- Auditability: full version history of tailored resumes

## Success Metrics (First 90 Days)
- Median tailoring time <= 5 min
- Average ATS delta >= +20 points
- WAU retention >= 25%
- Pro conversion >= 10%
