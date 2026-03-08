# Job Workers - Phase 1

## Queues
- `extract_resume`
- `tailor_resume`
- `compile_pdf`
- `export_drive`

## Task Contracts
### `extract_resume`
Input: `resume_document_id`
Output: canonical JSON, base LaTeX, version row

### `tailor_resume`
Input: `tailor_run_id`
Output: tailored JSON delta, LaTeX, ATS score, skills gap, compiled PDF

### `compile_pdf`
Input: `resume_version_id`
Output: PDF file object and compile logs

### `export_drive`
Input: `resume_version_id`, `user_drive_folder_id`
Output: drive file id, link, exported_at

## Retry Policy
- Max retries: 3
- Backoff: 5s, 20s, 60s
- Retry on: 429, 5xx, transient timeout
- No retry on: schema-validation failure, auth invalid

## Idempotency
- Unique idempotency key for each logical request
- Persist key + final artifact IDs
- Return existing result when duplicate request is detected

## Failure Handling
- Persist `failure_reason` and `failure_stage`
- Mark run `FAILED`
- Expose retry endpoint to user
