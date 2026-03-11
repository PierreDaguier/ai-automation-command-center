"use client";

import { useEffect, useState } from "react";

import { EmptyState } from "@/components/empty-state";
import { useAuth } from "@/components/auth-provider";
import { fetchSettings } from "@/lib/api";
import { SettingsOverview } from "@/lib/types";

export default function SettingsPage() {
  const { token } = useAuth();
  const [settings, setSettings] = useState<SettingsOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;

    fetchSettings(token)
      .then(setSettings)
      .catch(() => setError("Unable to load settings from backend"))
      .finally(() => setLoading(false));
  }, [token]);

  if (loading) {
    return <p className="text-sm text-slate-400">Loading settings and environment status...</p>;
  }

  if (error || !settings) {
    return <EmptyState title="Settings unavailable" description={error ?? "Backend settings endpoint is unavailable."} />;
  }

  return (
    <div className="grid gap-4 lg:grid-cols-3">
      <section className="rounded-2xl border border-edge bg-panel/70 p-5">
        <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Secrets Placeholders</p>
        <div className="mt-3 space-y-2 text-sm text-slate-300">
          <p>OpenAI API key: {settings.secrets.openai_api_key_set ? "configured" : "missing"}</p>
          <p>n8n API key: {settings.secrets.n8n_api_key_set ? "configured" : "missing"}</p>
        </div>
      </section>

      <section className="rounded-2xl border border-edge bg-panel/70 p-5">
        <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Environment Status</p>
        <div className="mt-3 space-y-2 text-sm text-slate-300">
          <p>Database: {settings.environment.database}</p>
          <p>Redis: {settings.environment.redis}</p>
          <p>n8n: {settings.environment.n8n}</p>
        </div>
      </section>

      <section className="rounded-2xl border border-edge bg-panel/70 p-5">
        <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Safety Controls</p>
        <div className="mt-3 space-y-2 text-sm text-slate-300">
          <p>Max retries: {settings.safety_controls.max_retries}</p>
          <p>Timeout: {settings.safety_controls.timeout_seconds}s</p>
          <p>Budget guardrail: ${settings.safety_controls.max_budget_per_run_usd.toFixed(2)}</p>
        </div>
      </section>
    </div>
  );
}
