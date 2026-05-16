import type { WorkflowStatus } from "@/types/workflow";

export const WORKFLOW_STATUS_LABELS: Record<WorkflowStatus, string> = {
  draft: "Draft",
  edit: "Editing",
  run: "Running",
};

export const WORKFLOW_STATUS_STYLES: Record<WorkflowStatus, string> = {
  draft: "bg-slate-100 text-slate-700",
  edit: "bg-amber-100 text-amber-800",
  run: "bg-emerald-100 text-emerald-800",
};
