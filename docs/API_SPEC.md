# API Spec - Phase 1 (v1)

Base path: `/api/v1`
Auth: Bearer JWT (Google OAuth session -> internal JWT)

## Auth
- `POST /auth/google/callback` -> exchange code, create user session
- `GET /auth/me` -> current user profile

## Resume
- `POST /resumes/upload-url` -> signed URL for source file upload
- `POST /resumes` -> create resume record after upload
- `GET /resumes` -> list resumes (filter by company/position/status/date)
- `GET /resumes/{resume_id}` -> detail with versions
- `PATCH /resumes/{resume_id}` -> metadata update
- `POST /resumes/{resume_id}/versions/{version_id}/compile` -> queue PDF compile
- Compile response shape: `{ id, status, failure_reason, created_at, updated_at }`

## Job Description + Tailoring
- `POST /job-descriptions` -> create JD from text/url
- `POST /tailor-runs` -> start tailoring run
- `GET /tailor-runs/{run_id}` -> status/result
- `GET /tailor-runs/{run_id}/analytics` -> frontend metrics (`alignment_score`, `missing_keywords_count`, `attempts`, `latency_ms`)

## ATS + Skills Gap
- `GET /resumes/{resume_id}/versions/{version_id}/ats` -> score + breakdown
- `GET /resumes/{resume_id}/versions/{version_id}/skills-gap` -> missing critical/nice-to-have

## Applications
- `POST /applications`
- `GET /applications`
- `PATCH /applications/{application_id}`
- `POST /applications/{application_id}/notes`

## Drive Export
- `POST /drive/exports` -> queue export of specific PDF
- `GET /drive/exports/{export_id}` -> status + share URL
- Export response shape: `{ id, resume_version_id, status, failure_reason, drive_file_id, drive_share_url, exported_at, created_at }`

## Status Values
- Application status: `NOT_APPLIED | APPLIED | SCREENING | INTERVIEW | OFFER | REJECTED`
- Tailor run status: `PENDING | RUNNING | SUCCEEDED | FAILED`

## Error Shape
```
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "...",
    "request_id": "..."
  }
}
```
