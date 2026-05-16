import { apiRequest } from "@/services/api-client";
import type { Workflow, WorkflowCreate } from "@/types/workflow";

export function listWorkflows() {
  return apiRequest<Workflow[]>("/workflows");
}

export function createWorkflow(body: WorkflowCreate) {
  return apiRequest<Workflow>("/workflows", { method: "POST", body });
}

export function getWorkflow(id: string) {
  return apiRequest<Workflow>(`/workflows/${id}`);
}

export function deleteWorkflow(id: string) {
  return apiRequest<void>(`/workflows/${id}`, { method: "DELETE" });
}
