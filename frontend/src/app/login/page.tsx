"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { useAuth } from "@/components/auth-provider";

export default function LoginPage() {
  const router = useRouter();
  const { token, signIn } = useAuth();
  const [email, setEmail] = useState("operator@command-center.io");
  const [password, setPassword] = useState("ChangeMe!123");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (token) {
      router.replace("/dashboard");
    }
  }, [token, router]);

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await signIn(email, password);
      router.replace("/dashboard");
    } catch {
      setError("Authentication failed. Verify credentials or backend API availability.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid min-h-screen place-items-center px-4">
      <form onSubmit={onSubmit} className="w-full max-w-md rounded-3xl border border-edge bg-panel/80 p-8 shadow-glow">
        <p className="text-xs uppercase tracking-[0.25em] text-accent">AI Automation Command Center</p>
        <h1 className="mt-3 text-3xl font-semibold">Operator Sign-In</h1>
        <p className="mt-2 text-sm text-slate-400">
          Access workflow control, approvals, and audit telemetry.
        </p>

        <div className="mt-6 grid gap-4">
          <label className="text-sm text-slate-300">
            Email
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className="mt-1 w-full rounded-xl border border-edge bg-slate-950/70 px-3 py-2 text-sm outline-none focus:border-accent"
              required
            />
          </label>

          <label className="text-sm text-slate-300">
            Password
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="mt-1 w-full rounded-xl border border-edge bg-slate-950/70 px-3 py-2 text-sm outline-none focus:border-accent"
              required
            />
          </label>
        </div>

        {error ? <p className="mt-4 text-sm text-danger">{error}</p> : null}

        <button
          type="submit"
          disabled={loading}
          className="mt-6 w-full rounded-xl bg-accent px-4 py-2 font-medium text-ink transition hover:brightness-95 disabled:opacity-60"
        >
          {loading ? "Signing in..." : "Enter Command Center"}
        </button>
      </form>
    </div>
  );
}
