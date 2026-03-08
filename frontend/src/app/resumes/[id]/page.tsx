"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";

import { Shell } from "@/components/shell";
import { api } from "@/lib/api";
import type { AtsScore, ResumeVersion, SkillsGap } from "@/lib/types";

export default function ResumeDetailPage() {
  const params = useParams<{ id: string }>();
  const resumeId = useMemo(() => params.id, [params.id]);
  const [versions, setVersions] = useState<ResumeVersion[]>([]);
  const [selectedVersionId, setSelectedVersionId] = useState<string | null>(null);
  const [ats, setAts] = useState<AtsScore | null>(null);
  const [skills, setSkills] = useState<SkillsGap | null>(null);
  const [latex, setLatex] = useState("\\\\item Added impactful bullet point aligned to role");
  const [error, setError] = useState<string | null>(null);
  const [polling, setPolling] = useState(false);

  const loadVersions = async () => {
    const rows = await api.listResumeVersions(resumeId);
    setVersions(rows);
    if (!selectedVersionId && rows[0]) {
      setSelectedVersionId(rows[0].id);
    }
    return rows;
  };

  useEffect(() => {
    loadVersions().catch((err: Error) => setError(err.message));
  }, [resumeId]);

  useEffect(() => {
    if (!selectedVersionId) return;
    Promise.all([api.getAts(resumeId, selectedVersionId), api.getSkillsGap(resumeId, selectedVersionId)])
      .then(([atsRow, skillsRow]) => {
        setAts(atsRow);
        setSkills(skillsRow);
      })
      .catch((err: Error) => setError(err.message));
  }, [resumeId, selectedVersionId]);

  useEffect(() => {
    if (!polling) return;
    const interval = setInterval(async () => {
      try {
        const rows = await loadVersions();
        const stillRunning = rows.some((row) => row.compile_status === "RUNNING");
        if (!stillRunning) {
          setPolling(false);
        }
      } catch (err) {
        setError((err as Error).message);
        setPolling(false);
      }
    }, 3000);
    return () => clearInterval(interval);
  }, [polling]);

  const onCreateVersion = async () => {
    try {
      await api.createResumeVersion(resumeId, {
        based_on_version_id: versions[0]?.id,
        latex_source: latex,
        created_by: "USER",
      });
      await loadVersions();
    } catch (err) {
      setError((err as Error).message);
    }
  };

  const onCompile = async (versionId: string) => {
    try {
      await api.compileResumeVersion(resumeId, versionId);
      setPolling(true);
      await loadVersions();
    } catch (err) {
      setError((err as Error).message);
    }
  };

  return (
    <Shell>
      <div className="grid gap-4 md:grid-cols-3">
        <div className="card p-4">
          <p className="text-xs text-black/60">ATS Score</p>
          <p className="text-2xl font-semibold">{ats?.score ?? 0}</p>
        </div>
        <div className="card p-4">
          <p className="text-xs text-black/60">Critical Missing Skills</p>
          <p className="text-2xl font-semibold">{skills?.critical_missing.length ?? 0}</p>
        </div>
        <div className="card p-4">
          <p className="text-xs text-black/60">Compile Polling</p>
          <p className="text-lg font-semibold">{polling ? "Running" : "Idle"}</p>
        </div>
      </div>

      <div className="card mt-4 p-5">
        <h1 className="text-xl font-semibold">Resume {resumeId}</h1>
        {error ? <p className="mt-2 text-sm text-red-700">{error}</p> : null}

        <div className="mt-4 grid gap-2 md:grid-cols-4">
          <input
            value={latex}
            onChange={(e) => setLatex(e.target.value)}
            className="rounded border px-3 py-2 md:col-span-3"
            placeholder="New LaTeX bullet content"
          />
          <button onClick={onCreateVersion} className="rounded bg-moss px-3 py-2 text-white">
            Create Version
          </button>
        </div>

        <div className="mt-4 space-y-3">
          {versions.map((version) => (
            <div key={version.id} className="rounded-lg border border-black/10 p-3">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium">Version #{version.version_no}</p>
                <button
                  onClick={() => setSelectedVersionId(version.id)}
                  className="rounded border border-black/20 px-2 py-1 text-xs"
                >
                  View metrics
                </button>
              </div>
              <p className="mt-1 text-xs text-black/60">Compile status: {version.compile_status}</p>
              <button onClick={() => onCompile(version.id)} className="mt-2 rounded bg-sky px-3 py-1 text-sm text-white">
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
