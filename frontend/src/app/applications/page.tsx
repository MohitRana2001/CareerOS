"use client";

import { useEffect, useState } from "react";

import { Shell } from "@/components/shell";
import { api } from "@/lib/api";
import type { Application } from "@/lib/types";

export default function ApplicationsPage() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [company, setCompany] = useState("Acme");
  const [position, setPosition] = useState("Backend Engineer");

  const refresh = () => api.listApplications().then(setApplications);

  useEffect(() => {
    refresh();
  }, []);

  const onAdd = async () => {
    await api.createApplication({ company_name: company, position_title: position, status: "APPLIED" });
    await refresh();
  };

  return (
    <Shell>
      <div className="card p-5">
        <h1 className="text-xl font-semibold">Applications</h1>
        <div className="mt-3 grid gap-2 md:grid-cols-3">
          <input value={company} onChange={(e) => setCompany(e.target.value)} className="rounded border px-3 py-2" />
          <input value={position} onChange={(e) => setPosition(e.target.value)} className="rounded border px-3 py-2" />
          <button onClick={onAdd} className="rounded bg-moss px-3 py-2 font-medium text-white">
            Add
          </button>
        </div>

        <ul className="mt-4 space-y-2 text-sm">
          {applications.map((app) => (
            <li key={app.id} className="rounded border border-black/10 px-3 py-2">
              {app.company_name} • {app.position_title} • {app.status}
            </li>
          ))}
        </ul>
      </div>
    </Shell>
  );
}
