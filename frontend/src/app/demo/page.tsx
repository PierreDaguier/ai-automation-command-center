import { MetricCard } from "@/components/metric-card";
import { currency, ms, percent } from "@/lib/format";

const sample = {
  success_rate: 98.6,
  p95_latency_ms: 1120,
  cost_per_run_usd: 0.0118,
  failed_runs: 3,
};

export default function DemoPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#070b12] via-[#0c1422] to-[#08101c] px-4 py-10 text-slate-100">
      <div className="mx-auto max-w-6xl space-y-6">
        <header className="rounded-2xl border border-edge bg-panel/70 p-6 shadow-glow">
          <p className="text-xs uppercase tracking-[0.22em] text-accent">Production Demo Snapshot</p>
          <h1 className="mt-2 text-4xl font-semibold">AI Automation Command Center</h1>
          <p className="mt-3 max-w-3xl text-sm text-slate-300">
            Workflow orchestration + AI agent execution + human approvals + full audit telemetry.
          </p>
        </header>

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <MetricCard title="Success Rate" value={percent(sample.success_rate)} accent="#78ffd6" />
          <MetricCard title="P95 Latency" value={ms(sample.p95_latency_ms)} accent="#6ca8ff" />
          <MetricCard title="Cost Per Run" value={currency(sample.cost_per_run_usd)} accent="#ffcc66" />
          <MetricCard title="Failed Runs" value={`${sample.failed_runs}`} accent="#ff6f6f" />
        </section>
      </div>
    </div>
  );
}
