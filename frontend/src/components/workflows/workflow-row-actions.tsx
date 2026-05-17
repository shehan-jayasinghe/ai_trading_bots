"use client";

import { Select } from "@/components/ui/select";
import type { Workflow } from "@/types/workflow";

type WorkflowAction = "edit" | "complete" | "run" | "delete";

type Props = {
  workflow: Workflow;
  onEdit: () => void;
  onComplete: () => void;
  onRun: () => void;
  onDelete: () => void;
};

export function WorkflowRowActions({
  workflow,
  onEdit,
  onComplete,
  onRun,
  onDelete,
}: Props) {
  const canEdit = workflow.status !== "run";
  const canComplete =
    workflow.status !== "run" && workflow.status !== "completed";
  const canRun = workflow.status === "completed";

  function handleChange(e: React.ChangeEvent<HTMLSelectElement>) {
    const action = e.target.value as WorkflowAction;
    e.target.value = "";
    if (!action) return;

    switch (action) {
      case "edit":
        onEdit();
        break;
      case "complete":
        onComplete();
        break;
      case "run":
        onRun();
        break;
      case "delete":
        onDelete();
        break;
    }
  }

  return (
    <Select
      className="h-9 w-36 shrink-0 bg-white text-sm"
      defaultValue=""
      onChange={handleChange}
      aria-label={`Actions for ${workflow.name}`}
    >
      <option value="" disabled>
        Actions
      </option>
      <option value="edit" disabled={!canEdit}>
        Edit
      </option>
      <option value="complete" disabled={!canComplete}>
        Complete
      </option>
      <option value="run" disabled={!canRun}>
        Run
      </option>
      <option value="delete">Delete</option>
    </Select>
  );
}
