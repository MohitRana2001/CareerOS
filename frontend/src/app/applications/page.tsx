"use client";

import { useEffect, useMemo, useState } from "react";

import { Shell } from "@/components/shell";
import { api } from "@/lib/api";
import type { Application, ApplicationStatus } from "@/lib/types";

const STATUSES: ApplicationStatus[] = ["NOT_APPLIED", "APPLIED", "SCREENING", "INTERVIEW", "OFFER", "REJECTED"];

export default function ApplicationsPage() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [company, setCompany] = useState("Acme");
  const [position, setPosition] = useState("Backend Engineer");
  const [statusFilter, setStatusFilter] = useState<"ALL" | ApplicationStatus>("ALL");
  const [query, setQuery] = useState("");
  const [error, setError] = useState<string | null>(null);

  const refresh = async () => {
    try {
      const rows = await api.listApplications();
      setApplications(rows);
    } catch (err) {
      setError((err as Error).message);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  const onAdd = async () => {
    try {
      await api.createApplication({ company_name: company, position_title: position, status: "APPLIED" });
      await refresh();
    } catch (err) {
      setError((err as Error).message);
    }
  };

  const onUpdateStatus = async (applicationId: string, nextStatus: ApplicationStatus) => {
    try {
      await api.updateApplication(applicationId, { status: nextStatus });
      await refresh();
    } catch (err) {
      setError((err as Error).message);
    }
  };

  const filtered = useMemo(() => {
    return applications.filter((app) => {
      const matchStatus = statusFilter === "ALL" || app.status === statusFilter;
      const q = query.trim().toLowerCase();
      const matchQuery =
        q.length === 0 || app.company_name.toLowerCase().includes(q) || app.position_title.toLowerCase().includes(q);
      return matchStatus && matchQuery;
    });
  }, [applications, query, statusFilter]);

  return (
    <Shell>
      <div className="card p-5">
        <h1 className="text-xl font-semibold">Applications</h1>
        {error ? <p className="mt-2 text-sm text-red-700">{error}</p> : null}

        <div className="mt-4 grid gap-2 md:grid-cols-3">
          <input value={company} onChange={(e) => setCompany(e.target.value)} className="rounded border px-3 py-2" />
          <input value={position} onChange={(e) => setPosition(e.target.value)} className="rounded border px-3 py-2" />
          <button onClick={onAdd} className="rounded bg-moss px-3 py-2 font-medium text-white">
            Add
          </button>
        </div>

        <div className="mt-4 grid gap-2 md:grid-cols-3">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search company or position"
            className="rounded border px-3 py-2"
          />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as "ALL" | ApplicationStatus)}
            className="rounded border px-3 py-2"
          >
            <option value="ALL">All statuses</option>
            {STATUSES.map((status) => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
          <p className="self-center text-sm text-black/60">{filtered.length} results</p>
        </div>

        <ul className="mt-4 space-y-2 text-sm">
          {filtered.map((app) => (
            <li key={app.id} className="rounded border border-black/10 px-3 py-2">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <span>
                  {app.company_name} • {app.position_title}
                </span>
                <select
                  value={app.status}
                  onChange={(e) => onUpdateStatus(app.id, e.target.value as ApplicationStatus)}
                  className="rounded border px-2 py-1 text-xs"
                >
                  {STATUSES.map((status) => (
                    <option key={status} value={status}>
                      {status}
                    </option>
                  ))}
                </select>
              </div>
            </li>
          ))}
          {filtered.length === 0 ? <li className="text-black/60">No matching applications.</li> : null}
        </ul>
      </div>
    </Shell>
  );
}
