"use client";

import {
  Background,
  Controls,
  MiniMap,
  ReactFlow,
  ReactFlowProvider,
  addEdge,
  useEdgesState,
  useNodesState,
  useReactFlow,
  type Connection,
  type Edge,
  type Node,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { useCallback, useEffect, useMemo, useRef } from "react";

import { AgentNode } from "@/components/workflow-editor/nodes/agent-node";
import { ParallelGroupNode } from "@/components/workflow-editor/nodes/parallel-group-node";
import {
  AGENT_CATALOG,
  PALETTE_DRAG_TYPE,
} from "@/constants/agent-catalog";
import { flowToGraph, graphToFlow } from "@/lib/workflow-graph/convert";
import { createDefaultWorkflowGraph } from "@/lib/workflow-graph/defaults";
import type { AgentKind, WorkflowGraphDefinition } from "@/types/workflow-graph";

const nodeTypes = {
  agent: AgentNode,
  parallel: ParallelGroupNode,
};

type CanvasInnerProps = {
  initialGraph: WorkflowGraphDefinition | null;
  onGraphChange: (graph: WorkflowGraphDefinition) => void;
  readOnly?: boolean;
};

function CanvasInner({
  initialGraph,
  onGraphChange,
  readOnly = false,
}: CanvasInnerProps) {
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const { screenToFlowPosition } = useReactFlow();
  const initial = useMemo(
    () => graphToFlow(initialGraph ?? createDefaultWorkflowGraph()),
    [initialGraph],
  );
  const [nodes, setNodes, onNodesChange] = useNodesState(initial.nodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initial.edges);

  useEffect(() => {
    onGraphChange(flowToGraph(nodes, edges));
  }, [nodes, edges, onGraphChange]);

  const onConnect = useCallback(
    (connection: Connection) => {
      setEdges((eds) =>
        addEdge(
          { ...connection, id: `e-${connection.source}-${connection.target}` },
          eds,
        ),
      );
    },
    [setEdges],
  );

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();
      const raw = event.dataTransfer.getData(PALETTE_DRAG_TYPE);
      if (!raw || !reactFlowWrapper.current) return;

      const { kind, label } = JSON.parse(raw) as {
        kind: AgentKind;
        label: string;
      };
      const entry = AGENT_CATALOG.find((a) => a.kind === kind);
      if (!entry) return;

      const position = screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });

      const parentNode = nodes.find((n) => {
        if (n.type !== "parallel") return false;
        const width = (n.style?.width as number) ?? 280;
        const height = (n.style?.height as number) ?? 160;
        return (
          position.x >= n.position.x &&
          position.x <= n.position.x + width &&
          position.y >= n.position.y &&
          position.y <= n.position.y + height
        );
      });

      const id = `agent-${kind}-${crypto.randomUUID().slice(0, 8)}`;
      const newNode: Node = {
        id,
        type: "agent",
        position: parentNode
          ? {
              x: position.x - parentNode.position.x - 20,
              y: position.y - parentNode.position.y - 20,
            }
          : position,
        data: { label, agentKind: kind },
        parentId: parentNode?.id,
        extent: parentNode ? "parent" : undefined,
        style: { zIndex: parentNode ? 1 : 2 },
      };

      setNodes((nds) => nds.concat(newNode));
    },
    [nodes, screenToFlowPosition, setNodes],
  );

  const addParallelGroup = useCallback(() => {
    const id = `parallel-${crypto.randomUUID().slice(0, 8)}`;
    setNodes((nds) =>
      nds.concat({
        id,
        type: "parallel",
        position: { x: 120, y: 120 },
        data: { label: "Parallel group" },
        style: { width: 300, height: 180, zIndex: 0 },
      }),
    );
  }, [setNodes]);

  return (
    <div className="flex h-full min-h-0 w-full flex-1 flex-col">
      {!readOnly && (
        <div className="flex items-center gap-2 border-b border-slate-200 bg-white px-4 py-2">
          <button
            type="button"
            onClick={addParallelGroup}
            className="rounded-lg border border-blue-200 bg-blue-50 px-3 py-1.5 text-sm font-medium text-blue-800 hover:bg-blue-100"
          >
            + Parallel group
          </button>
          <p className="text-xs text-slate-500">
            Drop agents into a parallel box to run them together
          </p>
        </div>
      )}
      <div ref={reactFlowWrapper} className="h-full min-h-0 w-full flex-1">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onDrop={readOnly ? undefined : onDrop}
          onDragOver={readOnly ? undefined : onDragOver}
          nodeTypes={nodeTypes}
          nodesDraggable={!readOnly}
          nodesConnectable={!readOnly}
          elementsSelectable={!readOnly}
          fitView
          deleteKeyCode={readOnly ? null : ["Backspace", "Delete"]}
          className="h-full w-full bg-slate-100"
        >
          <Background gap={16} size={1} color="#cbd5e1" />
          <Controls />
          <MiniMap zoomable pannable />
        </ReactFlow>
      </div>
    </div>
  );
}

type Props = {
  initialGraph: WorkflowGraphDefinition | null;
  onGraphChange: (graph: WorkflowGraphDefinition) => void;
  readOnly?: boolean;
};

export function WorkflowCanvas({
  initialGraph,
  onGraphChange,
  readOnly,
}: Props) {
  return (
    <div className="h-full min-h-0 w-full">
      <ReactFlowProvider>
        <CanvasInner
          initialGraph={initialGraph}
          onGraphChange={onGraphChange}
          readOnly={readOnly}
        />
      </ReactFlowProvider>
    </div>
  );
}
