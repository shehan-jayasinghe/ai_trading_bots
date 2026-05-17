export type AgentKind =
  | "data"
  | "indicator"
  | "rag"
  | "decision"
  | "mm"
  | "trading"
  | "rag_write";

export type GraphNodeType = "agent" | "parallel";

export type GraphNodePosition = {
  x: number;
  y: number;
};

export type GraphNodeData = {
  label: string;
  agentKind?: AgentKind;
};

export type GraphNodeStyle = {
  width?: number;
  height?: number;
};

export type WorkflowGraphNode = {
  id: string;
  type: GraphNodeType;
  position: GraphNodePosition;
  data: GraphNodeData;
  parentId?: string;
  style?: GraphNodeStyle;
};

export type WorkflowGraphEdge = {
  id: string;
  source: string;
  target: string;
};

export type WorkflowGraphDefinition = {
  version: 1;
  nodes: WorkflowGraphNode[];
  edges: WorkflowGraphEdge[];
};
