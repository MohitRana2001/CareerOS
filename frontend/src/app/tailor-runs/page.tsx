"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { Shell } from "@/components/shell";
import { api } from "@/lib/api";
import type { Resume, TailorRun, TailorRunAnalytics } from "@/lib/types";

function makeIdempotencyKey(resumeId: string, company: string) {
  const stamp = new Date().toISOString().slice(0, 19).replace(/[-:T]/g, "");
  return `${company.toLowerCase().replace(/\s+/g, "-")}-${resumeId.slice(0, 8)}-${stamp}`;
}

export default function TailorRunsPage() {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [resumeId, setResumeId] = useState("");
  const [company, setCompany] = useState("Acme Inc");
  const [position, setPosition] = useState("Backend Engineer");
  const [jdText, setJdText] = useState("Looking for Python, FastAPI, PostgreSQL, Redis, Docker, and AWS experience.");
  const [run, setRun] = useState<TailorRun | null>(null);
  const [analytics, setAnalytics] = useState<TailorRunAnalytics | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .listResumes()
      .then((rows) => {
        setResumes(rows);
        if (rows[0]) setResumeId(rows[0].id);
      })
      .catch((err: Error) => setError(err.message));
  }, []);

  useEffect(() => {
    if (!run) return;
    const load = async () => {
      try {
        const [runRow, analyticsRow] = await Promise.all([api.getTailorRun(run.id), api.getTailorRunAnalytics(run.id)]);
        setRun(runRow);
        setAnalytics(analyticsRow);
      } catch (err) {
        setError((err as Error).message);
      }
    };

    load();
    const interval = setInterval(load, 5000);
    return () => clearInterval(interval);
  }, [run?.id]);

  const canStart = useMemo(() => Boolean(resumeId && jdText.trim().length > 30), [resumeId, jdText]);

  const onStart = async () => {
    try {
      const jd = await api.createJobDescription({
        company_name: company,
        position_title: position,
        raw_text: jdText,
      });
      const createdRun = await api.createTailorRun({
        resume_document_id: resumeId,
        job_description_id: jd.id,
        idempotency_key: makeIdempotencyKey(resumeId, company),
        model_name: "gemini-2.5-pro",
        prompt_version: "v1",
      });
      setRun(createdRun);
      const analyticsRow = await api.getTailorRunAnalytics(createdRun.id);
      setAnalytics(analyticsRow);
    } catch (err) {
      setError((err as Error).message);
    }
  };

  return (
    <Shell>
      <div className="card p-5">
        <h1 className="text-xl font-semibold">Tailoring Workflow</h1>
        <p className="mt-1 text-sm text-black/70">Create JD, start run, and poll analytics.</p>
        {error ? <p className="mt-2 text-sm text-red-700">{error}</p> : null}

        <div className="mt-4 grid gap-2 md:grid-cols-2">
          <select value={resumeId} onChange={(e) => setResumeId(e.target.value)} className="rounded border px-3 py-2">
            {resumes.map((resume) => (
              <option key={resume.id} value={resume.id}>
                {resume.id}
              </option>
            ))}
          </select>
          <input value={company} onChange={(e) => setCompany(e.target.value)} className="rounded border px-3 py-2" />
          <input value={position} onChange={(e) => setPosition(e.target.value)} className="rounded border px-3 py-2" />
          <button
            onClick={onStart}
            disabled={!canStart}
            className="rounded bg-ember px-3 py-2 font-medium text-white disabled:opacity-50"
          >
            Start Tailor Run
          </button>
        </div>
        <textarea
          value={jdText}
          onChange={(e) => setJdText(e.target.value)}
          className="mt-2 h-32 w-full rounded border px-3 py-2"
          placeholder="Paste JD text"
        />
      </div>

      {run ? (
        <div className="mt-4 grid gap-4 md:grid-cols-5">
          <div className="card p-4">
            <p className="text-xs text-black/60">Status</p>
            <p className="text-xl font-semibold">{run.status}</p>
          </div>
          <div className="card p-4">
            <p className="text-xs text-black/60">Alignment</p>
            <p className="text-xl font-semibold">{analytics?.alignment_score ?? 0}</p>
          </div>
          <div className="card p-4">
            <p className="text-xs text-black/60">Missing</p>
            <p className="text-xl font-semibold">{analytics?.missing_keywords_count ?? 0}</p>
          </div>
          <div className="card p-4">
            <p className="text-xs text-black/60">Attempts</p>
            <p className="text-xl font-semibold">{analytics?.attempts ?? 0}</p>
          </div>
          <div className="card p-4">
            <p className="text-xs text-black/60">Latency</p>
            <p className="text-xl font-semibold">{analytics?.latency_ms ?? 0} ms</p>
          </div>
          <div className="md:col-span-5">
            <Link href={`/tailor-runs/${run.id}`} className="rounded bg-sky px-3 py-2 text-white">
              Open live run detail
            </Link>
          </div>
        </div>
      ) : null}
    </Shell>
  );
}
