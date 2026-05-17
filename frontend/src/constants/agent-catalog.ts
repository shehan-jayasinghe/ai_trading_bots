import type { AgentKind } from "@/types/workflow-graph";

export type AgentCatalogEntry = {
  kind: AgentKind;
  label: string;
  description: string;
};

export const AGENT_CATALOG: AgentCatalogEntry[] = [
  {
    kind: "data",
    label: "Market data",
    description: "Fetch ticks and candles from Deriv",
  },
  {
    kind: "indicator",
    label: "Indicator",
    description: "Compute technical signal",
  },
  {
    kind: "rag",
    label: "RAG load",
    description: "Load historical context",
  },
  {
    kind: "decision",
    label: "Decision",
    description: "Rules or crew decision",
  },
  {
    kind: "mm",
    label: "Money mgmt",
    description: "Stake sizing",
  },
  {
    kind: "trading",
    label: "Trade",
    description: "Place contract on Deriv",
  },
  {
    kind: "rag_write",
    label: "RAG write",
    description: "Persist trade outcome",
  },
];

export const AGENT_KIND_SET = new Set(AGENT_CATALOG.map((a) => a.kind));

export const PALETTE_DRAG_TYPE = "application/deriv-agent";
