"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";

import { Shell } from "@/components/shell";
import { api } from "@/lib/api";
import type { ResumeVersion } from "@/lib/types";

export default function ResumeDetailPage() {
  const params = useParams<{ id: string }>();
  const resumeId = useMemo(() => params.id, [params.id]);
  const [versions, setVersions] = useState<ResumeVersion[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .listResumeVersions(resumeId)
      .then(setVersions)
      .catch((err: Error) => setError(err.message));
  }, [resumeId]);

  const onCompile = async (versionId: string) => {
    try {
      setLoading(true);
      await api.compileResumeVersion(resumeId, versionId);
      const rows = await api.listResumeVersions(resumeId);
      setVersions(rows);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Shell>
      <div className="card p-5">
        <h1 className="text-xl font-semibold">Resume {resumeId}</h1>
        {error ? <p className="mt-2 text-sm text-red-700">{error}</p> : null}
        <div className="mt-4 space-y-3">
          {versions.map((version) => (
            <div key={version.id} className="rounded-lg border border-black/10 p-3">
              <p className="text-sm">Version #{version.version_no}</p>
              <p className="text-xs text-black/60">Compile status: {version.compile_status}</p>
              <button
                onClick={() => onCompile(version.id)}
                disabled={loading}
                className="mt-2 rounded bg-sky px-3 py-1 text-sm text-white"
              >
                Queue compile
              </button>
            </div>
          ))}
          {versions.length === 0 ? <p className="text-sm text-black/60">No versions yet.</p> : null}
        </div>
      </div>
    </Shell>
  );
}
