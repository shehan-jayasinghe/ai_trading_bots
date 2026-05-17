import { apiRequest } from "@/services/api-client";
import type { WorkflowGraphDefinition } from "@/types/workflow-graph";

export function getWorkflowGraph(workflowId: string) {
  return apiRequest<WorkflowGraphDefinition | null>(
    `/workflows/${workflowId}/graph`,
  );
}

export function saveWorkflowGraph(
  workflowId: string,
  graph: WorkflowGraphDefinition,
) {
  return apiRequest<WorkflowGraphDefinition>(`/workflows/${workflowId}/graph`, {
    method: "PUT",
    body: graph,
  });
}
