"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";

import { AppShell } from "@/components/app-shell";
import { useAuth } from "@/components/auth-provider";

export default function CommandLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { token, booting } = useAuth();

  useEffect(() => {
    if (!booting && !token && pathname !== "/login") {
      router.replace("/login");
    }
  }, [booting, token, pathname, router]);

  if (booting || !token) {
    return (
      <div className="grid min-h-screen place-items-center bg-ink text-slate-300">
        <p className="text-sm tracking-[0.2em]">SECURE SESSION CHECK</p>
      </div>
    );
  }

  return <AppShell>{children}</AppShell>;
}
