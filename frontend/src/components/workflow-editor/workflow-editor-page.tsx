"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { AgentPalette } from "@/components/workflow-editor/agent-palette";
import { WorkflowCanvas } from "@/components/workflow-editor/workflow-canvas";
import { WorkflowStatusBadge } from "@/components/workflows/workflow-status-badge";
import { ApiError } from "@/services/api-client";
import * as workflowGraphService from "@/services/workflow-graph.service";
import * as workflowService from "@/services/workflow.service";
import type { Workflow } from "@/types/workflow";
import type { WorkflowGraphDefinition } from "@/types/workflow-graph";

type Props = {
  workflowId: string;
};

export function WorkflowEditorPage({ workflowId }: Props) {
  const [workflow, setWorkflow] = useState<Workflow | null>(null);
  const [initialGraph, setInitialGraph] = useState<
    WorkflowGraphDefinition | null | undefined
  >(undefined);
  const graphRef = useRef<WorkflowGraphDefinition | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      try {
        const [wf, graph] = await Promise.all([
          workflowService.getWorkflow(workflowId),
          workflowGraphService.getWorkflowGraph(workflowId),
        ]);
        if (cancelled) return;
        setWorkflow(wf);
        setInitialGraph(graph);
        graphRef.current = graph;
      } catch (err) {
        if (!cancelled) {
          toast.error(
            err instanceof ApiError ? err.message : "Failed to load workflow",
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, [workflowId]);

  const onGraphChange = useCallback((graph: WorkflowGraphDefinition) => {
    graphRef.current = graph;
  }, []);

  async function handleSave() {
    if (!graphRef.current) return;
    setSaving(true);
    try {
      await workflowGraphService.saveWorkflowGraph(
        workflowId,
        graphRef.current,
      );
      toast.success("Workflow graph saved");
    } catch (err) {
      toast.error(
        err instanceof ApiError ? err.message : "Failed to save graph",
      );
    } finally {
      setSaving(false);
    }
  }

  if (loading || initialGraph === undefined) {
    return (
      <p className="py-12 text-center text-sm text-slate-500">
        Loading workflow editor…
      </p>
    );
  }

  if (!workflow) {
    return (
      <p className="py-12 text-center text-sm text-red-600">
        Workflow not found.
      </p>
    );
  }

  const readOnly = workflow.status === "run";

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <header className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-200 bg-white px-4 py-3">
        <div className="flex min-w-0 items-center gap-3">
          <Link
            href="/"
            className="text-sm text-slate-500 hover:text-slate-900"
          >
            ← Back
          </Link>
          <h1 className="truncate text-lg font-semibold text-slate-900">
            {workflow.name}
          </h1>
          <WorkflowStatusBadge status={workflow.status} />
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-500">
            {workflow.trading_pair} · {workflow.trading_type}
          </span>
          {!readOnly && (
            <Button
              type="button"
              size="sm"
              disabled={saving}
              onClick={() => void handleSave()}
            >
              {saving ? "Saving…" : "Save graph"}
            </Button>
          )}
        </div>
      </header>

      {readOnly ? (
        <p className="border-b border-amber-200 bg-amber-50 px-4 py-2 text-sm text-amber-900">
          This workflow is running. The graph is read-only.
        </p>
      ) : null}

      <div className="flex min-h-0 flex-1">
        {!readOnly && <AgentPalette />}
        <div className="flex min-h-0 min-w-0 flex-1 flex-col">
          <WorkflowCanvas
            initialGraph={initialGraph}
            onGraphChange={onGraphChange}
            readOnly={readOnly}
          />
        </div>
      </div>
    </div>
  );
}
