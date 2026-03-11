import {
  ActionLogItem,
  ApprovalItem,
  AuditItem,
  AuthUser,
  KpiData,
  SettingsOverview,
  WorkflowItem,
} from "@/lib/types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

const FALLBACK_KPI: KpiData = {
  success_rate: 98.2,
  p95_latency_ms: 1240,
  cost_per_run_usd: 0.0124,
  failed_runs: 2,
  total_runs: 113,
};

async function request<T>(path: string, token?: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers);
  headers.set("Content-Type", "application/json");
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers,
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return (await response.json()) as T;
}

export async function login(email: string, password: string): Promise<string> {
  const data = await request<{ access_token: string }>("/auth/login", undefined, {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  return data.access_token;
}

export async function me(token: string): Promise<AuthUser> {
  const data = await request<{ email: string; role: AuthUser["role"] }>("/auth/me", token);
  return { email: data.email, role: data.role };
}

export async function fetchKpis(token: string): Promise<KpiData> {
  try {
    return await request<KpiData>("/dashboard/kpis", token);
  } catch {
    return FALLBACK_KPI;
  }
}

export async function fetchWorkflows(token: string): Promise<WorkflowItem[]> {
  try {
    const data = await request<{ items: WorkflowItem[] }>("/workflows/catalog", token);
    return data.items;
  } catch {
    return [];
  }
}

export async function fetchApprovals(token: string): Promise<ApprovalItem[]> {
  try {
    const data = await request<{ items: ApprovalItem[] }>("/approvals/queue", token);
    return data.items;
  } catch {
    return [];
  }
}

export async function decisionApproval(
  token: string,
  approvalId: string,
  decision: "approve" | "reject",
  reason: string,
): Promise<void> {
  await request(`/approvals/${approvalId}/decision`, token, {
    method: "POST",
    body: JSON.stringify({ decision, reason }),
  });
}

export async function fetchActionLogs(token: string): Promise<ActionLogItem[]> {
  try {
    const data = await request<{ items: ActionLogItem[] }>("/logs/actions", token);
    return data.items;
  } catch {
    return [];
  }
}

export async function fetchAudit(token: string): Promise<AuditItem[]> {
  try {
    const data = await request<{ items: AuditItem[] }>("/audit/timeline", token);
    return data.items;
  } catch {
    return [];
  }
}

export async function fetchSettings(token: string): Promise<SettingsOverview> {
  return request<SettingsOverview>("/settings", token);
}
