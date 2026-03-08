"use client";

import { useEffect, useState } from "react";

import { Shell } from "@/components/shell";
import { api } from "@/lib/api";
import type { Application, Resume } from "@/lib/types";

export default function DashboardPage() {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [applications, setApplications] = useState<Application[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([api.listResumes(), api.listApplications()])
      .then(([resumeRows, applicationRows]) => {
        setResumes(resumeRows);
        setApplications(applicationRows);
      })
      .catch((err: Error) => setError(err.message));
  }, []);

  return (
    <Shell>
      <section className="grid gap-4 md:grid-cols-3">
        <div className="card p-5">
          <p className="text-sm text-black/60">Resumes</p>
          <p className="text-3xl font-semibold">{resumes.length}</p>
        </div>
        <div className="card p-5">
          <p className="text-sm text-black/60">Applications</p>
          <p className="text-3xl font-semibold">{applications.length}</p>
        </div>
        <div className="card p-5">
          <p className="text-sm text-black/60">Flow</p>
          <p className="text-lg font-semibold">Upload → Tailor → Apply</p>
        </div>
      </section>

      <section className="card mt-6 p-5">
        <h2 className="text-lg font-semibold">Recent Resumes</h2>
        {error ? <p className="mt-2 text-sm text-red-700">{error}</p> : null}
        <ul className="mt-3 space-y-2">
          {resumes.map((resume) => (
            <li key={resume.id} className="rounded-lg border border-black/10 px-3 py-2 text-sm">
              {resume.source_file_type.toUpperCase()} • {resume.id}
            </li>
          ))}
          {resumes.length === 0 ? <li className="text-sm text-black/60">No resumes yet.</li> : null}
        </ul>
      </section>
    </Shell>
  );
}
