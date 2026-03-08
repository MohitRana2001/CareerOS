"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { Shell } from "@/components/shell";
import { api } from "@/lib/api";
import type { Resume } from "@/lib/types";

export default function ResumesPage() {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [fileType, setFileType] = useState<"pdf" | "docx">("pdf");
  const [sourceUrl, setSourceUrl] = useState("https://storage.example.com/careeros/uploads/base-resume.pdf");
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  const refresh = () => api.listResumes().then(setResumes).catch((err: Error) => setError(err.message));

  useEffect(() => {
    refresh();
  }, []);

  const onCreateResume = async () => {
    try {
      setIsSaving(true);
      const upload = await api.createUploadUrl();
      await api.createResume({ source_file_url: sourceUrl || upload.file_url, source_file_type: fileType });
      await refresh();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Shell>
      <div className="card p-5">
        <h1 className="text-xl font-semibold">Resumes</h1>
        <p className="mt-1 text-sm text-black/70">Upload (URL stub) and manage resume versions.</p>
        {error ? <p className="mt-2 text-sm text-red-700">{error}</p> : null}

        <div className="mt-4 grid gap-2 md:grid-cols-4">
          <select
            value={fileType}
            onChange={(e) => setFileType(e.target.value as "pdf" | "docx")}
            className="rounded border px-3 py-2"
          >
            <option value="pdf">PDF</option>
            <option value="docx">DOCX</option>
          </select>
          <input
            value={sourceUrl}
            onChange={(e) => setSourceUrl(e.target.value)}
            className="rounded border px-3 py-2 md:col-span-2"
            placeholder="Source URL"
          />
          <button onClick={onCreateResume} disabled={isSaving} className="rounded bg-ember px-3 py-2 font-medium text-white">
            {isSaving ? "Saving..." : "Create Resume"}
          </button>
        </div>

        <ul className="mt-5 space-y-2 text-sm">
          {resumes.map((resume) => (
            <li key={resume.id} className="flex items-center justify-between rounded border border-black/10 px-3 py-2">
              <span>
                {resume.source_file_type.toUpperCase()} • {resume.id}
              </span>
              <Link href={`/resumes/${resume.id}`} className="rounded bg-sky px-3 py-1 text-white">
                Open
              </Link>
            </li>
          ))}
          {resumes.length === 0 ? <li className="text-black/60">No resumes created yet.</li> : null}
        </ul>
      </div>
    </Shell>
  );
}
