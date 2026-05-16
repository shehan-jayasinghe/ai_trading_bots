"use client";

import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/stores/auth-store";
import { useWorkflowStore } from "@/stores/workflow-store";
import { useEffect } from "react";

export function WorkflowList() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const workflows = useWorkflowStore((s) => s.workflows);
  const isLoading = useWorkflowStore((s) => s.isLoading);
  const error = useWorkflowStore((s) => s.error);
  const fetchWorkflows = useWorkflowStore((s) => s.fetchWorkflows);
  const deleteWorkflow = useWorkflowStore((s) => s.deleteWorkflow);

  useEffect(() => {
    if (accessToken) void fetchWorkflows();
  }, [accessToken, fetchWorkflows]);

  if (!accessToken) {
    return <p className="text-sm text-slate-500">Connecting to API…</p>;
  }

  if (isLoading && workflows.length === 0) {
    return <p className="text-sm text-slate-500">Loading workflows…</p>;
  }

  return (
    <div className="mt-8">
      {error && (
        <p className="mb-4 text-sm text-red-600" role="alert">
          {error}
        </p>
      )}
      {workflows.length === 0 ? (
        <p className="text-sm text-slate-500">No workflows yet. Create one to get started.</p>
      ) : (
        <ul className="divide-y divide-slate-200 rounded-xl border border-slate-200 bg-white">
          {workflows.map((w) => (
            <li
              key={w.id}
              className="flex items-center justify-between gap-4 px-4 py-4"
            >
              <div>
                <p className="font-medium text-slate-900">{w.name}</p>
                <p className="text-sm text-slate-500">
                  {w.trading_pair} · {w.trading_type} · {w.status}
                </p>
              </div>
              <Button
                type="button"
                variant="destructive"
                size="sm"
                onClick={() => void deleteWorkflow(w.id)}
              >
                Delete
              </Button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
