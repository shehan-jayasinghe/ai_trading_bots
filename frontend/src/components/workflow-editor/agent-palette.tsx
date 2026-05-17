"use client";

import {
  AGENT_CATALOG,
  PALETTE_DRAG_TYPE,
} from "@/constants/agent-catalog";
import type { AgentKind } from "@/types/workflow-graph";

export function AgentPalette() {
  function onDragStart(
    event: React.DragEvent<HTMLButtonElement>,
    kind: AgentKind,
    label: string,
  ) {
    event.dataTransfer.setData(
      PALETTE_DRAG_TYPE,
      JSON.stringify({ kind, label }),
    );
    event.dataTransfer.effectAllowed = "move";
  }

  return (
    <aside className="flex h-full w-56 shrink-0 flex-col border-r border-slate-200 bg-slate-50">
      <div className="border-b border-slate-200 px-4 py-3">
        <h2 className="text-sm font-semibold text-slate-900">Agents</h2>
        <p className="mt-1 text-xs text-slate-500">Drag onto the canvas</p>
      </div>
      <ul className="flex flex-1 flex-col gap-2 overflow-y-auto p-3">
        {AGENT_CATALOG.map((agent) => (
          <li key={agent.kind}>
            <button
              type="button"
              draggable
              onDragStart={(e) => onDragStart(e, agent.kind, agent.label)}
              className="w-full cursor-grab rounded-lg border border-slate-200 bg-white px-3 py-2 text-left shadow-sm transition hover:border-slate-400 active:cursor-grabbing"
            >
              <p className="text-sm font-medium text-slate-900">
                {agent.label}
              </p>
              <p className="mt-0.5 text-xs text-slate-500">
                {agent.description}
              </p>
            </button>
          </li>
        ))}
      </ul>
    </aside>
  );
}
