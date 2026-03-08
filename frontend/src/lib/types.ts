export type RunStatus = "PENDING" | "RUNNING" | "SUCCEEDED" | "FAILED";

export type Resume = {
  id: string;
  source_file_url: string | null;
  source_file_type: "pdf" | "docx";
  canonical_json: Record<string, unknown> | null;
  created_at: string;
};

export type ResumeVersion = {
  id: string;
  resume_document_id: string;
  version_no: number;
  based_on_version_id: string | null;
  job_description_id: string | null;
  latex_source: string;
  compile_status: RunStatus;
  created_by: "SYSTEM" | "USER";
  created_at: string;
};

export type JobDescription = {
  id: string;
  company_name: string | null;
  position_title: string | null;
  source_url: string | null;
  raw_text: string;
  extracted_requirements: { keywords?: string[] } | null;
  created_at: string;
};

export type TailorRun = {
  id: string;
  resume_document_id: string;
  job_description_id: string;
  status: RunStatus;
  idempotency_key: string;
  model_name: string | null;
  prompt_version: string | null;
  run_attempt_count: number;
  ats_keyword_alignment: Record<string, unknown> | null;
  model_trace_metadata: Record<string, unknown> | null;
  failure_stage: string | null;
  failure_reason: string | null;
  created_at: string;
  updated_at: string;
};

export type TailorRunAnalytics = {
  run_id: string;
  status: RunStatus;
  alignment_score: number;
  missing_keywords_count: number;
  attempts: number;
  latency_ms: number | null;
};

export type Application = {
  id: string;
  company_name: string;
  position_title: string;
  applied_date: string | null;
  status: "NOT_APPLIED" | "APPLIED" | "SCREENING" | "INTERVIEW" | "OFFER" | "REJECTED";
  created_at: string;
};
