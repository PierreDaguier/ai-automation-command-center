"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Activity, ClipboardCheck, Gauge, Logs, Route, Settings, Shield, Sparkles } from "lucide-react";

import { useAuth } from "@/components/auth-provider";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: Gauge },
  { href: "/workflows", label: "Workflows", icon: Route },
  { href: "/approvals", label: "Approvals", icon: ClipboardCheck },
  { href: "/logs", label: "Action Logs", icon: Logs },
  { href: "/audit", label: "Audit", icon: Shield },
  { href: "/settings", label: "Settings", icon: Settings },
] as const;

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, signOut } = useAuth();

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#070b12] via-[#0c1422] to-[#08101c] text-slate-100">
      <div className="mx-auto flex min-h-screen w-full max-w-[1440px] flex-col lg:flex-row">
        <aside className="border-b border-edge bg-panel/85 px-4 py-4 backdrop-blur lg:min-h-screen lg:w-72 lg:border-b-0 lg:border-r">
          <div className="flex items-center gap-3 px-2 py-2">
            <div className="rounded-xl bg-accent/15 p-2 text-accent">
              <Sparkles size={20} />
            </div>
            <div>
              <p className="font-semibold tracking-wide">AI Automation</p>
              <p className="text-xs text-slate-400">Command Center</p>
            </div>
          </div>

          <nav className="mt-6 grid grid-cols-2 gap-2 lg:grid-cols-1">
            {NAV_ITEMS.map((item) => {
              const ActiveIcon = item.icon;
              const active = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-2 rounded-xl border px-3 py-2 text-sm transition ${
                    active
                      ? "border-accent/60 bg-accent/10 text-accent"
                      : "border-edge bg-slate-900/30 text-slate-300 hover:border-slate-500"
                  }`}
                >
                  <ActiveIcon size={16} />
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </aside>

        <main className="flex-1 px-4 py-4 sm:px-6 lg:px-8">
          <header className="mb-6 flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-edge bg-panel/70 p-4 shadow-glow">
            <div>
              <p className="text-sm text-slate-400">Operator Console</p>
              <p className="font-semibold tracking-wide">Trusted automation with human control</p>
            </div>
            <div className="flex items-center gap-3 text-xs">
              <span className="inline-flex items-center gap-1 rounded-full border border-signal/30 bg-signal/10 px-2 py-1 text-signal">
                <Activity size={12} /> Live
              </span>
              <span className="rounded-full border border-edge bg-slate-900/40 px-2 py-1 text-slate-300">
                {user?.email ?? "unknown"}
              </span>
              <button
                type="button"
                onClick={() => {
                  signOut();
                  router.push("/login");
                }}
                className="rounded-full border border-edge px-3 py-1 text-slate-200 hover:border-slate-300"
              >
                Sign out
              </button>
            </div>
          </header>

          {children}
        </main>
      </div>
    </div>
  );
}
