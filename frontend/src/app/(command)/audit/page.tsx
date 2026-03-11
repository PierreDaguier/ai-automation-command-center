"use client";

import { useEffect, useState } from "react";

import { EmptyState } from "@/components/empty-state";
import { useAuth } from "@/components/auth-provider";
import { fetchAudit } from "@/lib/api";
import { stamp } from "@/lib/format";
import { AuditItem } from "@/lib/types";

export default function AuditPage() {
  const { token } = useAuth();
  const [items, setItems] = useState<AuditItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;

    fetchAudit(token)
      .then(setItems)
      .finally(() => setLoading(false));
  }, [token]);

  if (loading) {
    return <p className="text-sm text-slate-400">Loading audit timeline...</p>;
  }

  if (!items.length) {
    return <EmptyState title="No audit events" description="No governed actions have been recorded." />;
  }

  return (
    <div className="space-y-3">
      {items.map((item) => (
        <article key={item.id} className="rounded-2xl border border-edge bg-panel/70 p-4">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <p className="font-medium">{item.action}</p>
            <p className="text-xs text-slate-500">{stamp(item.created_at)}</p>
          </div>
          <p className="mt-1 text-sm text-slate-300">
            actor: {item.actor} ({item.actor_role}) | {item.entity_type} {item.entity_id}
          </p>
          <pre className="mt-2 overflow-auto rounded-lg bg-slate-950/70 p-2 text-xs text-slate-400">
            {JSON.stringify(item.metadata_json, null, 2)}
          </pre>
        </article>
      ))}
    </div>
  );
}
