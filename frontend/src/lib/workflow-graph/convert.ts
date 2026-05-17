import type { Edge, Node } from "@xyflow/react";

import type {
  WorkflowGraphDefinition,
  WorkflowGraphEdge,
  WorkflowGraphNode,
} from "@/types/workflow-graph";

export function graphToFlow(definition: WorkflowGraphDefinition): {
  nodes: Node[];
  edges: Edge[];
} {
  const nodes: Node[] = definition.nodes.map((n) => ({
    id: n.id,
    type: n.type,
    position: n.position,
    data: n.data,
    parentId: n.parentId,
    extent: n.parentId ? ("parent" as const) : undefined,
    style:
      n.type === "parallel"
        ? {
            width: n.style?.width ?? 280,
            height: n.style?.height ?? 160,
            zIndex: 0,
          }
        : { zIndex: n.parentId ? 1 : 2 },
  }));

  const edges: Edge[] = definition.edges.map((e) => ({
    id: e.id,
    source: e.source,
    target: e.target,
    animated: true,
  }));

  return { nodes, edges };
}

export function flowToGraph(nodes: Node[], edges: Edge[]): WorkflowGraphDefinition {
  const graphNodes: WorkflowGraphNode[] = nodes.map((n) => ({
    id: n.id,
    type: n.type as WorkflowGraphNode["type"],
    position: n.position,
    data: n.data as WorkflowGraphNode["data"],
    parentId: n.parentId,
    style:
      n.type === "parallel"
        ? {
            width: (n.style?.width as number) ?? 280,
            height: (n.style?.height as number) ?? 160,
          }
        : undefined,
  }));

  const graphEdges: WorkflowGraphEdge[] = edges.map((e) => ({
    id: e.id,
    source: e.source,
    target: e.target,
  }));

  return { version: 1, nodes: graphNodes, edges: graphEdges };
}
