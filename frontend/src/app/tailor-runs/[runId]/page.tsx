"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";

import { Shell } from "@/components/shell";
import { api } from "@/lib/api";
import type { TailorRun, TailorRunAnalytics } from "@/lib/types";

export default function TailorRunPage() {
  const params = useParams<{ runId: string }>();
  const runId = useMemo(() => params.runId, [params.runId]);
  const [run, setRun] = useState<TailorRun | null>(null);
  const [analytics, setAnalytics] = useState<TailorRunAnalytics | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const [runRow, analyticsRow] = await Promise.all([api.getTailorRun(runId), api.getTailorRunAnalytics(runId)]);
        setRun(runRow);
        setAnalytics(analyticsRow);
      } catch (err) {
        setError((err as Error).message);
      }
    };

    load();
    const interval = setInterval(load, 5000);
    return () => clearInterval(interval);
  }, [runId]);

  return (
    <Shell>
      <div className="grid gap-4 md:grid-cols-4">
        <div className="card p-4">
          <p className="text-xs text-black/60">Status</p>
          <p className="text-xl font-semibold">{analytics?.status ?? run?.status ?? "-"}</p>
        </div>
        <div className="card p-4">
          <p className="text-xs text-black/60">Alignment</p>
          <p className="text-xl font-semibold">{analytics?.alignment_score ?? 0}</p>
        </div>
        <div className="card p-4">
          <p className="text-xs text-black/60">Missing Keywords</p>
          <p className="text-xl font-semibold">{analytics?.missing_keywords_count ?? 0}</p>
        </div>
        <div className="card p-4">
          <p className="text-xs text-black/60">Latency (ms)</p>
          <p className="text-xl font-semibold">{analytics?.latency_ms ?? 0}</p>
        </div>
      </div>
      {error ? <p className="mt-3 text-sm text-red-700">{error}</p> : null}
    </Shell>
  );
}
