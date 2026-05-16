import {
  WORKFLOW_STATUS_LABELS,
  WORKFLOW_STATUS_STYLES,
} from "@/constants/workflow-status";
import type { WorkflowStatus } from "@/types/workflow";

type Props = {
  status: WorkflowStatus;
};

export function WorkflowStatusBadge({ status }: Props) {
  return (
    <span
      className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${WORKFLOW_STATUS_STYLES[status]}`}
    >
      {WORKFLOW_STATUS_LABELS[status]}
    </span>
  );
}
