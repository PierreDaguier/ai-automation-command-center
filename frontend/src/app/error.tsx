"use client";

export default function Error({ reset }: { error: Error; reset: () => void }) {
  return (
    <div className="grid min-h-screen place-items-center bg-ink px-6">
      <div className="max-w-md rounded-2xl border border-dashed border-danger/50 bg-panel/70 p-6 text-center">
        <h2 className="text-xl font-semibold text-danger">Unable to render command center</h2>
        <p className="mt-2 text-sm text-slate-300">
          An unexpected UI error occurred. Retry after backend connectivity is restored.
        </p>
        <button
          type="button"
          onClick={reset}
          className="mt-4 rounded-lg border border-edge bg-slate-800 px-4 py-2 text-sm"
        >
          Retry
        </button>
      </div>
    </div>
  );
}
