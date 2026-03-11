"use client";

import { useEffect, useState } from "react";

import { EmptyState } from "@/components/empty-state";
import { useAuth } from "@/components/auth-provider";
import { fetchActionLogs } from "@/lib/api";
import { stamp } from "@/lib/format";
import { ActionLogItem } from "@/lib/types";

export default function LogsPage() {
  const { token } = useAuth();
  const [items, setItems] = useState<ActionLogItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;

    fetchActionLogs(token)
      .then(setItems)
      .finally(() => setLoading(false));
  }, [token]);

  if (loading) {
    return <p className="text-sm text-slate-400">Loading action logs...</p>;
  }

  if (!items.length) {
    return <EmptyState title="No action logs" description="Runs have not emitted action records yet." />;
  }

  return (
    <div className="overflow-x-auto rounded-2xl border border-edge bg-panel/70">
      <table className="w-full min-w-[900px] text-left text-sm">
        <thead className="border-b border-edge text-xs uppercase tracking-[0.2em] text-slate-400">
          <tr>
            <th className="px-4 py-3">Time</th>
            <th className="px-4 py-3">Run</th>
            <th className="px-4 py-3">Action</th>
            <th className="px-4 py-3">Target</th>
            <th className="px-4 py-3">Status</th>
            <th className="px-4 py-3">Details</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.id} className="border-b border-edge/60">
              <td className="px-4 py-3 text-slate-300">{stamp(item.created_at)}</td>
              <td className="px-4 py-3 font-[var(--font-mono)] text-xs text-slate-300">{item.run_id.slice(0, 8)}...</td>
              <td className="px-4 py-3">{item.action_type}</td>
              <td className="px-4 py-3">{item.target}</td>
              <td className="px-4 py-3">
                <span className="rounded-full border border-edge px-2 py-1 text-xs">{item.status}</span>
              </td>
              <td className="px-4 py-3 text-xs text-slate-400">
                <pre className="max-h-28 overflow-auto rounded-md bg-slate-950/70 p-2">{JSON.stringify(item.details_json, null, 2)}</pre>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
