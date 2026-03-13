"use client";

import { useEffect, useState } from "react";

import { EmptyState } from "@/components/empty-state";
import { MetricCard } from "@/components/metric-card";
import { useAuth } from "@/components/auth-provider";
import { fetchKpis, fetchWorkflows } from "@/lib/api";
import { currency, ms, percent } from "@/lib/format";
import { KpiData, WorkflowItem } from "@/lib/types";

export default function DashboardPage() {
  const { token } = useAuth();
  const [kpis, setKpis] = useState<KpiData | null>(null);
  const [workflows, setWorkflows] = useState<WorkflowItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;

    Promise.all([fetchKpis(token), fetchWorkflows(token)])
      .then(([kpiData, workflowData]) => {
        setKpis(kpiData);
        setWorkflows(workflowData);
      })
      .finally(() => setLoading(false));
  }, [token]);

  if (loading) {
    return <p className="text-sm text-slate-400">Loading KPI telemetry...</p>;
  }

  if (!kpis) {
    return <EmptyState title="No KPI signal" description="Connect API gateway to read live run metrics." />;
  }

  return (
    <div className="space-y-6">
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard title="Success Rate" value={percent(kpis.success_rate)} accent="#62ff9b" />
        <MetricCard title="P95 Latency" value={ms(kpis.p95_latency_ms)} accent="#ffd47a" />
        <MetricCard title="Cost Per Run" value={currency(kpis.cost_per_run_usd)} accent="#ffbf66" />
        <MetricCard title="Failed Runs" value={`${kpis.failed_runs}`} accent="#ff7a88" />
      </section>

      <section className="grid gap-4 lg:grid-cols-3">
        <article className="rounded-2xl border border-edge bg-panel/70 p-5 lg:col-span-2">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Value Narrative</p>
          <h2 className="mt-2 text-2xl font-semibold">Execution confidence in under 30 seconds</h2>
          <p className="mt-3 text-sm text-slate-300">
            This command center demonstrates operational workflows with agent reasoning, explicit tool contracts,
            approval gates, and immutable audit trails. Buyers can evaluate reliability and governance without reading code.
          </p>
          <div className="mt-4 grid gap-3 sm:grid-cols-3">
            <div className="rounded-xl border border-edge bg-slate-900/50 p-3 text-sm text-slate-300">
              <p className="text-xs text-slate-500">Workflow Runs</p>
              <p className="mt-1 text-lg font-semibold">{kpis.total_runs}</p>
            </div>
            <div className="rounded-xl border border-edge bg-slate-900/50 p-3 text-sm text-slate-300">
              <p className="text-xs text-slate-500">Agent + n8n</p>
              <p className="mt-1 text-lg font-semibold">Active</p>
            </div>
            <div className="rounded-xl border border-edge bg-slate-900/50 p-3 text-sm text-slate-300">
              <p className="text-xs text-slate-500">HITL Queue</p>
              <p className="mt-1 text-lg font-semibold">Governed</p>
            </div>
          </div>
        </article>

        <article className="rounded-2xl border border-edge bg-panel/70 p-5">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Catalog Snapshot</p>
          <ul className="mt-3 space-y-2 text-sm text-slate-200">
            {workflows.slice(0, 4).map((workflow) => (
              <li key={workflow.id} className="rounded-lg border border-edge bg-slate-900/40 p-3">
                <p className="font-medium">{workflow.name}</p>
                <p className="mt-1 text-xs text-slate-400">{workflow.category} | risk: {workflow.risk_level}</p>
              </li>
            ))}
          </ul>
        </article>
      </section>
    </div>
  );
}
