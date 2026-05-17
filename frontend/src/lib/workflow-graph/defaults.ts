import type { WorkflowGraphDefinition } from "@/types/workflow-graph";

/** Default pipeline must include data, decision, and trading agents (any layout). */
export function createDefaultWorkflowGraph(): WorkflowGraphDefinition {
  return {
    version: 1,
    nodes: [
      {
        id: "agent-data",
        type: "agent",
        position: { x: 40, y: 120 },
        data: { label: "Market data", agentKind: "data" },
      },
      {
        id: "parallel-signals",
        type: "parallel",
        position: { x: 240, y: 80 },
        data: { label: "Parallel" },
        style: { width: 320, height: 180 },
      },
      {
        id: "agent-indicator",
        type: "agent",
        position: { x: 24, y: 48 },
        parentId: "parallel-signals",
        data: { label: "Indicator", agentKind: "indicator" },
      },
      {
        id: "agent-rag",
        type: "agent",
        position: { x: 160, y: 48 },
        parentId: "parallel-signals",
        data: { label: "RAG load", agentKind: "rag" },
      },
      {
        id: "agent-decision",
        type: "agent",
        position: { x: 620, y: 120 },
        data: { label: "Decision", agentKind: "decision" },
      },
      {
        id: "agent-mm",
        type: "agent",
        position: { x: 820, y: 120 },
        data: { label: "Money mgmt", agentKind: "mm" },
      },
      {
        id: "agent-trading",
        type: "agent",
        position: { x: 1020, y: 120 },
        data: { label: "Trade", agentKind: "trading" },
      },
      {
        id: "agent-rag-write",
        type: "agent",
        position: { x: 1220, y: 120 },
        data: { label: "RAG write", agentKind: "rag_write" },
      },
    ],
    edges: [
      { id: "e-data-parallel", source: "agent-data", target: "parallel-signals" },
      {
        id: "e-parallel-decision",
        source: "parallel-signals",
        target: "agent-decision",
      },
      { id: "e-decision-mm", source: "agent-decision", target: "agent-mm" },
      { id: "e-mm-trade", source: "agent-mm", target: "agent-trading" },
      {
        id: "e-trade-ragwrite",
        source: "agent-trading",
        target: "agent-rag-write",
      },
    ],
  };
}
