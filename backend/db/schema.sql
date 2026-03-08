CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  google_sub TEXT UNIQUE NOT NULL,
  email TEXT UNIQUE NOT NULL,
  full_name TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE resume_documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  source_file_url TEXT,
  source_file_type TEXT NOT NULL CHECK (source_file_type IN ('pdf','docx')),
  canonical_json JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_resume_documents_user_id ON resume_documents(user_id);

CREATE TABLE job_descriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  company_name TEXT,
  position_title TEXT,
  source_url TEXT,
  raw_text TEXT NOT NULL,
  extracted_requirements JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_job_descriptions_user_id ON job_descriptions(user_id);

CREATE TABLE resume_versions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  resume_document_id UUID NOT NULL REFERENCES resume_documents(id) ON DELETE CASCADE,
  version_no INT NOT NULL,
  based_on_version_id UUID REFERENCES resume_versions(id),
  job_description_id UUID REFERENCES job_descriptions(id),
  latex_source TEXT NOT NULL,
  pdf_file_url TEXT,
  compile_status TEXT NOT NULL DEFAULT 'PENDING' CHECK (compile_status IN ('PENDING','RUNNING','SUCCEEDED','FAILED')),
  created_by TEXT NOT NULL CHECK (created_by IN ('SYSTEM','USER')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (resume_document_id, version_no)
);
CREATE INDEX idx_resume_versions_resume_document_id ON resume_versions(resume_document_id);

CREATE TABLE tailor_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  resume_document_id UUID NOT NULL REFERENCES resume_documents(id) ON DELETE CASCADE,
  job_description_id UUID NOT NULL REFERENCES job_descriptions(id) ON DELETE CASCADE,
  output_resume_version_id UUID REFERENCES resume_versions(id),
  status TEXT NOT NULL CHECK (status IN ('PENDING','RUNNING','SUCCEEDED','FAILED')),
  idempotency_key TEXT NOT NULL,
  model_name TEXT,
  prompt_version TEXT,
  failure_stage TEXT,
  failure_reason TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (user_id, idempotency_key)
);

CREATE TABLE ats_scores (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  resume_version_id UUID NOT NULL UNIQUE REFERENCES resume_versions(id) ON DELETE CASCADE,
  score INT NOT NULL CHECK (score >= 0 AND score <= 100),
  breakdown JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE skills_gap_reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  resume_version_id UUID NOT NULL UNIQUE REFERENCES resume_versions(id) ON DELETE CASCADE,
  critical_missing JSONB NOT NULL,
  nice_to_have_missing JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE applications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  company_name TEXT NOT NULL,
  position_title TEXT NOT NULL,
  applied_date DATE,
  status TEXT NOT NULL CHECK (status IN ('NOT_APPLIED','APPLIED','SCREENING','INTERVIEW','OFFER','REJECTED')),
  resume_version_id UUID REFERENCES resume_versions(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_applications_user_id ON applications(user_id);
CREATE INDEX idx_applications_status ON applications(status);

CREATE TABLE application_notes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
  note TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE drive_exports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  resume_version_id UUID NOT NULL REFERENCES resume_versions(id) ON DELETE CASCADE,
  drive_file_id TEXT,
  drive_share_url TEXT,
  status TEXT NOT NULL CHECK (status IN ('PENDING','RUNNING','SUCCEEDED','FAILED')),
  failure_reason TEXT,
  exported_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE audit_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  event_type TEXT NOT NULL,
  resource_type TEXT,
  resource_id UUID,
  metadata JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
