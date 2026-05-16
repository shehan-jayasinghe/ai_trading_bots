import { create } from "zustand";

import * as workflowService from "@/services/workflow.service";
import type { Workflow, WorkflowCreate, WorkflowUpdate } from "@/types/workflow";

type WorkflowState = {
  workflows: Workflow[];
  isLoading: boolean;
  error: string | null;
  fetchWorkflows: () => Promise<void>;
  createWorkflow: (data: WorkflowCreate) => Promise<void>;
  beginEditWorkflow: (id: string) => Promise<void>;
  updateWorkflow: (id: string, data: WorkflowUpdate) => Promise<void>;
  runWorkflow: (id: string) => Promise<void>;
  deleteWorkflow: (id: string) => Promise<void>;
};

export const useWorkflowStore = create<WorkflowState>((set, get) => ({
  workflows: [],
  isLoading: false,
  error: null,

  fetchWorkflows: async () => {
    set({ isLoading: true, error: null });
    try {
      const workflows = await workflowService.listWorkflows();
      set({ workflows, isLoading: false });
    } catch (e) {
      set({
        error: e instanceof Error ? e.message : "Failed to load workflows",
        isLoading: false,
      });
    }
  },

  createWorkflow: async (data) => {
    set({ error: null });
    await workflowService.createWorkflow(data);
    await get().fetchWorkflows();
  },

  beginEditWorkflow: async (id) => {
    set({ error: null });
    await workflowService.beginEditWorkflow(id);
    await get().fetchWorkflows();
  },

  updateWorkflow: async (id, data) => {
    set({ error: null });
    await workflowService.updateWorkflow(id, data);
    await get().fetchWorkflows();
  },

  runWorkflow: async (id) => {
    set({ error: null });
    await workflowService.runWorkflow(id);
    await get().fetchWorkflows();
  },

  deleteWorkflow: async (id) => {
    set({ error: null });
    await workflowService.deleteWorkflow(id);
    await get().fetchWorkflows();
  },
}));
