"use client";

import { CreateWorkflowSheet } from "@/components/workflows/create-workflow-sheet";
import { WorkflowList } from "@/components/workflows/workflow-list";

export function WorkflowsDashboard() {
  return (
    <section className="mt-8">
      <div className="flex items-center justify-between gap-4">
        <h2 className="text-lg font-semibold text-slate-900">Workflows</h2>
        <CreateWorkflowSheet />
      </div>
      <WorkflowList />
    </section>
  );
}
