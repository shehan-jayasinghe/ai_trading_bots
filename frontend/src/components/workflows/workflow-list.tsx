"use client";

import { Button } from "@/components/ui/button";
import { EditWorkflowSheet } from "@/components/workflows/edit-workflow-sheet";
import { WorkflowStatusBadge } from "@/components/workflows/workflow-status-badge";
import { ApiError } from "@/services/api-client";
import { useAuthStore } from "@/stores/auth-store";
import { useWorkflowStore } from "@/stores/workflow-store";
import type { Workflow } from "@/types/workflow";
import { useEffect, useState } from "react";

export function WorkflowList() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const workflows = useWorkflowStore((s) => s.workflows);
  const isLoading = useWorkflowStore((s) => s.isLoading);
  const error = useWorkflowStore((s) => s.error);
  const fetchWorkflows = useWorkflowStore((s) => s.fetchWorkflows);
  const runWorkflow = useWorkflowStore((s) => s.runWorkflow);
  const deleteWorkflow = useWorkflowStore((s) => s.deleteWorkflow);
  const [editing, setEditing] = useState<Workflow | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  useEffect(() => {
    if (accessToken) void fetchWorkflows();
  }, [accessToken, fetchWorkflows]);

  async function handleRun(id: string) {
    setActionError(null);
    try {
      await runWorkflow(id);
    } catch (err) {
      setActionError(
        err instanceof ApiError ? err.message : "Failed to start workflow",
      );
    }
  }

  if (!accessToken) {
    return <p className="text-sm text-slate-500">Connecting to API…</p>;
  }

  if (isLoading && workflows.length === 0) {
    return <p className="text-sm text-slate-500">Loading workflows…</p>;
  }

  return (
    <div className="mt-8">
      <EditWorkflowSheet
        workflow={editing}
        open={editing !== null}
        onOpenChange={(open) => {
          if (!open) setEditing(null);
        }}
      />
      {(error || actionError) && (
        <p className="mb-4 text-sm text-red-600" role="alert">
          {error ?? actionError}
        </p>
      )}
      {workflows.length === 0 ? (
        <p className="text-sm text-slate-500">
          No workflows yet. Create one to get started.
        </p>
      ) : (
        <ul className="divide-y divide-slate-200 rounded-xl border border-slate-200 bg-white">
          {workflows.map((w) => (
            <li
              key={w.id}
              className="flex flex-wrap items-center justify-between gap-4 px-4 py-4"
            >
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <p className="font-medium text-slate-900">{w.name}</p>
                  <WorkflowStatusBadge status={w.status} />
                </div>
                <p className="text-sm text-slate-500">
                  {w.trading_pair} · {w.trading_type}
                </p>
              </div>
              <div className="flex flex-wrap gap-2">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  disabled={w.status === "run"}
                  onClick={() => setEditing(w)}
                >
                  Edit
                </Button>
                <Button
                  type="button"
                  size="sm"
                  disabled={w.status === "run"}
                  onClick={() => void handleRun(w.id)}
                >
                  Run
                </Button>
                <Button
                  type="button"
                  variant="destructive"
                  size="sm"
                  onClick={() => void deleteWorkflow(w.id)}
                >
                  Delete
                </Button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
