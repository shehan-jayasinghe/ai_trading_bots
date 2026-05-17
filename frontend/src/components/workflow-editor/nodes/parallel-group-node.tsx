"use client";

import { Handle, NodeResizer, Position, type NodeProps } from "@xyflow/react";

import type { GraphNodeData } from "@/types/workflow-graph";

export function ParallelGroupNode({ data, selected }: NodeProps) {
  const nodeData = data as GraphNodeData;

  return (
    <div
      className={`h-full w-full rounded-xl border-2 border-dashed bg-slate-50/80 ${
        selected ? "border-blue-500" : "border-blue-300"
      }`}
    >
      <NodeResizer
        minWidth={200}
        minHeight={120}
        isVisible={selected}
        lineClassName="border-blue-400"
        handleClassName="h-2 w-2 bg-blue-500"
      />
      <Handle type="target" position={Position.Left} className="!bg-blue-500" />
      <div className="px-3 py-2">
        <p className="text-xs font-semibold uppercase tracking-wide text-blue-700">
          Parallel
        </p>
        <p className="text-sm text-slate-700">{nodeData.label}</p>
        <p className="mt-1 text-xs text-slate-500">
          Agents inside run in parallel
        </p>
      </div>
      <Handle
        type="source"
        position={Position.Right}
        className="!bg-blue-500"
      />
    </div>
  );
}
