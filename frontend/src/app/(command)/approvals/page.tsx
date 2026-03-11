"use client";

import { useEffect, useState } from "react";

import { EmptyState } from "@/components/empty-state";
import { useAuth } from "@/components/auth-provider";
import { decisionApproval, fetchApprovals } from "@/lib/api";
import { stamp } from "@/lib/format";
import { ApprovalItem } from "@/lib/types";

export default function ApprovalsPage() {
  const { token } = useAuth();
  const [items, setItems] = useState<ApprovalItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState<string | null>(null);

  const load = () => {
    if (!token) return;
    setLoading(true);
    fetchApprovals(token)
      .then(setItems)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  const decide = async (approvalId: string, decision: "approve" | "reject") => {
    if (!token) return;
    const reason = window.prompt(`Reason for ${decision}:`, decision === "approve" ? "Validated by operator" : "Policy blocked") ?? "";
    if (reason.trim().length < 3) return;

    setBusy(approvalId);
    try {
      await decisionApproval(token, approvalId, decision, reason);
      await load();
    } finally {
      setBusy(null);
    }
  };

  if (loading) {
    return <p className="text-sm text-slate-400">Loading approval queue...</p>;
  }

  if (!items.length) {
    return <EmptyState title="Approval queue is empty" description="No sensitive actions are waiting for operator decision." />;
  }

  return (
    <div className="space-y-3">
      {items.map((item) => (
        <article key={item.approval_id} className="rounded-2xl border border-edge bg-panel/70 p-4">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <p className="text-lg font-semibold">{item.workflow_slug}</p>
              <p className="text-sm text-slate-300">{item.action_label}</p>
              <p className="mt-1 text-xs text-slate-500">
                requested by {item.requested_by} | {stamp(item.created_at)}
              </p>
            </div>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => decide(item.approval_id, "approve")}
                disabled={busy === item.approval_id}
                className="rounded-lg bg-accent px-3 py-1 text-sm font-medium text-ink disabled:opacity-60"
              >
                Approve
              </button>
              <button
                type="button"
                onClick={() => decide(item.approval_id, "reject")}
                disabled={busy === item.approval_id}
                className="rounded-lg border border-danger px-3 py-1 text-sm text-danger disabled:opacity-60"
              >
                Reject
              </button>
            </div>
          </div>
        </article>
      ))}
    </div>
  );
}
