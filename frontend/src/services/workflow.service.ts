import { apiRequest } from "@/services/api-client";
import type { Workflow, WorkflowCreate, WorkflowUpdate } from "@/types/workflow";

export function listWorkflows() {
  return apiRequest<Workflow[]>("/workflows");
}

export function createWorkflow(body: WorkflowCreate) {
  return apiRequest<Workflow>("/workflows", { method: "POST", body });
}

export function getWorkflow(id: string) {
  return apiRequest<Workflow>(`/workflows/${id}`);
}

export function updateWorkflow(id: string, body: WorkflowUpdate) {
  return apiRequest<Workflow>(`/workflows/${id}`, { method: "PATCH", body });
}

export function beginEditWorkflow(id: string) {
  return apiRequest<Workflow>(`/workflows/${id}/edit`, { method: "POST" });
}

export function completeWorkflow(id: string) {
  return apiRequest<Workflow>(`/workflows/${id}/complete`, { method: "POST" });
}

export function runWorkflow(id: string) {
  return apiRequest<Workflow>(`/workflows/${id}/run`, { method: "POST" });
}

export function deleteWorkflow(id: string) {
  return apiRequest<void>(`/workflows/${id}`, { method: "DELETE" });
}
