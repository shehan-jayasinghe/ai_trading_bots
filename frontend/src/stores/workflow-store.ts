import { create } from "zustand";

import * as workflowService from "@/services/workflow.service";
import type { Workflow, WorkflowCreate } from "@/types/workflow";

type WorkflowState = {
  workflows: Workflow[];
  isLoading: boolean;
  error: string | null;
  fetchWorkflows: () => Promise<void>;
  createWorkflow: (data: WorkflowCreate) => Promise<void>;
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

  deleteWorkflow: async (id) => {
    set({ error: null });
    await workflowService.deleteWorkflow(id);
    await get().fetchWorkflows();
  },
}));
