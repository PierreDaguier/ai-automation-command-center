export type UserRole = "admin" | "operator";

export type AuthUser = {
  email: string;
  role: UserRole;
};

export type KpiData = {
  success_rate: number;
  p95_latency_ms: number;
  cost_per_run_usd: number;
  failed_runs: number;
  total_runs: number;
};

export type WorkflowItem = {
  id: string;
  slug: string;
  name: string;
  description: string;
  category: string;
  risk_level: string;
  enabled: boolean;
  requires_approval: boolean;
};

export type ApprovalItem = {
  approval_id: string;
  run_id: string;
  workflow_slug: string;
  action_label: string;
  requested_by: string;
  status: string;
  created_at: string;
};

export type ActionLogItem = {
  id: string;
  run_id: string;
  action_type: string;
  target: string;
  status: string;
  details_json: Record<string, unknown>;
  created_at: string;
};

export type AuditItem = {
  id: string;
  actor: string;
  actor_role: string;
  action: string;
  entity_type: string;
  entity_id: string;
  metadata_json: Record<string, unknown>;
  created_at: string;
};

export type SettingsOverview = {
  secrets: {
    openai_api_key_set: boolean;
    n8n_api_key_set: boolean;
  };
  environment: {
    database: string;
    redis: string;
    n8n: string;
  };
  safety_controls: {
    max_retries: number;
    timeout_seconds: number;
    max_budget_per_run_usd: number;
  };
};
