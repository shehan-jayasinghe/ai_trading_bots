"use client";

import { Handle, Position, type NodeProps } from "@xyflow/react";

import type { GraphNodeData } from "@/types/workflow-graph";

export function AgentNode({ data, selected }: NodeProps) {
  const nodeData = data as GraphNodeData;

  return (
    <div
      className={`min-w-[140px] rounded-lg border bg-white px-3 py-2 shadow-sm ${
        selected ? "border-slate-900 ring-2 ring-slate-200" : "border-slate-300"
      }`}
    >
      <Handle type="target" position={Position.Left} className="!bg-slate-500" />
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
        {nodeData.agentKind ?? "agent"}
      </p>
      <p className="text-sm font-semibold text-slate-900">{nodeData.label}</p>
      <Handle
        type="source"
        position={Position.Right}
        className="!bg-slate-500"
      />
    </div>
  );
}
