import type {
  Application,
  ApplicationStatus,
  AtsScore,
  JobDescription,
  JobStatus,
  Resume,
  ResumeVersion,
  SkillsGap,
  TailorRun,
  TailorRunAnalytics,
  UploadUrlResponse,
} from "@/lib/types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

function authHeaders() {
  const token = typeof window !== "undefined" ? localStorage.getItem("careeros_token") : null;
  const devEmail = typeof window !== "undefined" ? localStorage.getItem("careeros_dev_email") : null;

  return {
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(devEmail ? { "X-Dev-User-Email": devEmail } : {}),
    "Content-Type": "application/json",
  };
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      ...authHeaders(),
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`API ${response.status}: ${text}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  me: () => request<{ id: string; email: string; full_name: string | null }>("/auth/me"),

  createUploadUrl: () => request<UploadUrlResponse>("/resumes/upload-url", { method: "POST" }),
  listResumes: () => request<Resume[]>("/resumes"),
  createResume: (payload: { source_file_url?: string; source_file_type: "pdf" | "docx" }) =>
    request<Resume>("/resumes", { method: "POST", body: JSON.stringify(payload) }),
  getResume: (resumeId: string) => request<Resume>(`/resumes/${resumeId}`),
  listResumeVersions: (resumeId: string) => request<ResumeVersion[]>(`/resumes/${resumeId}/versions`),
  createResumeVersion: (
    resumeId: string,
    payload: {
      based_on_version_id?: string;
      job_description_id?: string;
      latex_source: string;
      created_by?: "SYSTEM" | "USER";
    }
  ) => request<ResumeVersion>(`/resumes/${resumeId}/versions`, { method: "POST", body: JSON.stringify(payload) }),
  compileResumeVersion: (resumeId: string, versionId: string) =>
    request<JobStatus>(`/resumes/${resumeId}/versions/${versionId}/compile`, { method: "POST" }),
  getAts: (resumeId: string, versionId: string) => request<AtsScore>(`/resumes/${resumeId}/versions/${versionId}/ats`),
  getSkillsGap: (resumeId: string, versionId: string) =>
    request<SkillsGap>(`/resumes/${resumeId}/versions/${versionId}/skills-gap`),

  createJobDescription: (payload: {
    company_name?: string;
    position_title?: string;
    source_url?: string;
    raw_text: string;
  }) => request<JobDescription>("/job-descriptions", { method: "POST", body: JSON.stringify(payload) }),

  createTailorRun: (payload: {
    resume_document_id: string;
    job_description_id: string;
    idempotency_key: string;
    model_name?: string;
    prompt_version?: string;
  }) => request<TailorRun>("/tailor-runs", { method: "POST", body: JSON.stringify(payload) }),

  getTailorRun: (runId: string) => request<TailorRun>(`/tailor-runs/${runId}`),
  getTailorRunAnalytics: (runId: string) => request<TailorRunAnalytics>(`/tailor-runs/${runId}/analytics`),

  listApplications: () => request<Application[]>("/applications"),
  createApplication: (payload: {
    company_name: string;
    position_title: string;
    status?: ApplicationStatus;
    applied_date?: string;
  }) => request<Application>("/applications", { method: "POST", body: JSON.stringify(payload) }),
  updateApplication: (
    applicationId: string,
    payload: {
      company_name?: string;
      position_title?: string;
      status?: ApplicationStatus;
      applied_date?: string;
    }
  ) => request<Application>(`/applications/${applicationId}`, { method: "PATCH", body: JSON.stringify(payload) }),
};
