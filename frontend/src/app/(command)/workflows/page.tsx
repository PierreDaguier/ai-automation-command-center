"use client";

import { useEffect, useState } from "react";

import { EmptyState } from "@/components/empty-state";
import { useAuth } from "@/components/auth-provider";
import { fetchWorkflows } from "@/lib/api";
import { WorkflowItem } from "@/lib/types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export default function WorkflowsPage() {
  const { token } = useAuth();
  const [items, setItems] = useState<WorkflowItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;

    fetchWorkflows(token)
      .then(setItems)
      .finally(() => setLoading(false));
  }, [token]);

  if (loading) {
    return <p className="text-sm text-slate-400">Loading workflow catalog...</p>;
  }

  if (!items.length) {
    return <EmptyState title="No workflows configured" description="Seed data or connect backend catalog." />;
  }

  return (
    <div className="space-y-5">
      <section className="rounded-2xl border border-edge bg-panel/70 p-5">
        <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Trigger Ingestion</p>
        <p className="mt-2 text-sm text-slate-300">
          Inbound events can arrive through signed webhooks and scheduler triggers.
        </p>
        <div className="mt-3 grid gap-2 text-xs text-slate-300">
          <p className="rounded-lg border border-edge bg-slate-900/50 px-3 py-2">
            Webhook: <code className="font-[var(--font-mono)]">{API_BASE}/triggers/webhook/{'{workflow_slug}'}</code>
          </p>
          <p className="rounded-lg border border-edge bg-slate-900/50 px-3 py-2">
            Scheduler: <code className="font-[var(--font-mono)]">{API_BASE}/triggers/scheduler/run</code>
          </p>
        </div>
      </section>

      <section className="grid gap-3 lg:grid-cols-2">
        {items.map((workflow) => (
          <article key={workflow.id} className="rounded-2xl border border-edge bg-panel/70 p-5">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h2 className="text-lg font-semibold">{workflow.name}</h2>
              <span
                className={`rounded-full px-2 py-1 text-xs ${
                  workflow.enabled ? "bg-accent/15 text-accent" : "bg-slate-700/40 text-slate-300"
                }`}
              >
                {workflow.enabled ? "enabled" : "disabled"}
              </span>
            </div>
            <p className="mt-2 text-sm text-slate-300">{workflow.description}</p>
            <div className="mt-3 flex flex-wrap gap-2 text-xs">
              <span className="rounded-full border border-edge px-2 py-1">{workflow.category}</span>
              <span className="rounded-full border border-edge px-2 py-1">risk: {workflow.risk_level}</span>
              <span className="rounded-full border border-edge px-2 py-1">
                approval: {workflow.requires_approval ? "required" : "not required"}
              </span>
            </div>
          </article>
        ))}
      </section>
    </div>
  );
}
