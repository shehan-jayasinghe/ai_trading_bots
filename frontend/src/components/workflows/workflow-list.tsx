"use client";

import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import { EditWorkflowSheet } from "@/components/workflows/edit-workflow-sheet";
import { WorkflowRowActions } from "@/components/workflows/workflow-row-actions";
import { WorkflowStatusBadge } from "@/components/workflows/workflow-status-badge";
import { formatDateTime } from "@/lib/format-datetime";
import { ApiError } from "@/services/api-client";
import { useAuthStore } from "@/stores/auth-store";
import { useWorkflowStore } from "@/stores/workflow-store";
import type { Workflow } from "@/types/workflow";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { toast } from "sonner";

export function WorkflowList() {
  const router = useRouter();
  const accessToken = useAuthStore((s) => s.accessToken);
  const workflows = useWorkflowStore((s) => s.workflows);
  const isLoading = useWorkflowStore((s) => s.isLoading);
  const error = useWorkflowStore((s) => s.error);
  const fetchWorkflows = useWorkflowStore((s) => s.fetchWorkflows);
  const completeWorkflow = useWorkflowStore((s) => s.completeWorkflow);
  const runWorkflow = useWorkflowStore((s) => s.runWorkflow);
  const deleteWorkflow = useWorkflowStore((s) => s.deleteWorkflow);
  const [editing, setEditing] = useState<Workflow | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Workflow | null>(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    if (accessToken) void fetchWorkflows();
  }, [accessToken, fetchWorkflows]);

  useEffect(() => {
    if (error) toast.error(error);
  }, [error]);

  async function handleComplete(id: string, name: string) {
    try {
      await completeWorkflow(id);
      toast.success(`"${name}" marked as completed`);
    } catch (err) {
      toast.error(
        err instanceof ApiError ? err.message : "Failed to complete workflow",
      );
    }
  }

  async function handleRun(id: string, name: string) {
    try {
      await runWorkflow(id);
      toast.success(`"${name}" is now running`);
    } catch (err) {
      toast.error(
        err instanceof ApiError ? err.message : "Failed to start workflow",
      );
    }
  }

  async function confirmDelete() {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await deleteWorkflow(deleteTarget.id);
      toast.success(`"${deleteTarget.name}" deleted`);
      setDeleteTarget(null);
    } catch (err) {
      toast.error(
        err instanceof ApiError ? err.message : "Failed to delete workflow",
      );
    } finally {
      setDeleting(false);
    }
  }

  if (!accessToken) {
    return <p className="text-sm text-slate-500">Connecting to API…</p>;
  }

  if (isLoading && workflows.length === 0) {
    return <p className="text-sm text-slate-500">Loading workflows…</p>;
  }

  return (
    <div className="mt-8 w-full">
      <ConfirmDialog
        open={deleteTarget !== null}
        onOpenChange={(open) => {
          if (!open && !deleting) setDeleteTarget(null);
        }}
        title="Delete workflow?"
        description={
          deleteTarget
            ? `Are you sure you want to delete "${deleteTarget.name}"? This cannot be undone.`
            : ""
        }
        confirmLabel="Delete"
        confirmVariant="destructive"
        loading={deleting}
        onConfirm={() => void confirmDelete()}
      />
      <EditWorkflowSheet
        workflow={editing}
        open={editing !== null}
        onOpenChange={(open) => {
          if (!open) setEditing(null);
        }}
      />
      {workflows.length === 0 ? (
        <p className="text-sm text-slate-500">
          No workflows yet. Create one to get started.
        </p>
      ) : (
        <div className="w-full overflow-x-auto rounded-xl border border-slate-200 bg-white">
          <table className="w-full table-fixed text-left text-sm">
            <colgroup>
              <col className="w-[18%]" />
              <col className="w-[10%]" />
              <col className="w-[10%]" />
              <col className="w-[8%]" />
              <col className="w-[18%]" />
              <col className="w-[18%]" />
              <col className="w-[18%]" />
            </colgroup>
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50 text-xs font-medium uppercase tracking-wide text-slate-500">
                <th className="px-4 py-3">Name</th>
                <th className="px-4 py-3">Pair</th>
                <th className="px-4 py-3">Type</th>
                <th className="px-4 py-3">Min / day</th>
                <th className="px-4 py-3">Start time</th>
                <th className="px-4 py-3">Created</th>
                <th className="px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {workflows.map((w) => (
                <tr key={w.id} className="text-slate-700">
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap items-center gap-2">
                      <Link
                        href={`/workflows/${w.id}`}
                        className="truncate font-medium text-slate-900 hover:underline"
                      >
                        {w.name}
                      </Link>
                      <WorkflowStatusBadge status={w.status} />
                    </div>
                  </td>
                  <td className="truncate px-4 py-3">{w.trading_pair}</td>
                  <td className="truncate px-4 py-3">{w.trading_type}</td>
                  <td className="px-4 py-3">{w.one_day_minimum_trade ?? "—"}</td>
                  <td className="truncate px-4 py-3">
                    {formatDateTime(w.starting_time)}
                  </td>
                  <td className="truncate px-4 py-3">
                    {formatDateTime(w.created_at)}
                  </td>
                  <td className="px-4 py-3">
                    <WorkflowRowActions
                      workflow={w}
                      onOpen={() => router.push(`/workflows/${w.id}`)}
                      onEdit={() => setEditing(w)}
                      onComplete={() => void handleComplete(w.id, w.name)}
                      onRun={() => void handleRun(w.id, w.name)}
                      onDelete={() => setDeleteTarget(w)}
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
