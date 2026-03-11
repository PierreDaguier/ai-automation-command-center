"use client";

import { motion } from "framer-motion";

export function MetricCard({
  title,
  value,
  accent,
}: {
  title: string;
  value: string;
  accent: string;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="rounded-2xl border border-edge bg-panel/70 p-4 shadow-glow"
    >
      <p className="text-xs uppercase tracking-[0.2em] text-slate-400">{title}</p>
      <p className="mt-2 text-3xl font-semibold" style={{ color: accent }}>
        {value}
      </p>
    </motion.div>
  );
}
