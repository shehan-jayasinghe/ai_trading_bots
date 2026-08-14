"use client";

import { useState } from "react";
import { CandleChart } from "@/components/CandleChart";
import { MaterialsPanel } from "@/components/MaterialsPanel";
import { StreamStatusBadge } from "@/components/StreamStatus";
import { useCandleStream } from "@/hooks/useCandleStream";
import { useFlowStream } from "@/hooks/useFlowStream";
import { ENTITY_CONFIG } from "@/lib/config";
import type { MarketEntity } from "@/types/candle";

type ViewMode = "candles" | "materials";

export function Dashboard() {
  const [entity, setEntity] = useState<MarketEntity>("btc");
  const [view, setView] = useState<ViewMode>("candles");
  const entityConfig = ENTITY_CONFIG[entity];
  const [timeframe, setTimeframe] = useState<string>(entityConfig.defaultTimeframe);

  const candlesState = useCandleStream(entity, timeframe);
  const flowState = useFlowStream("BTCUSDT");

  const switchEntity = (next: MarketEntity) => {
    setEntity(next);
    setTimeframe(ENTITY_CONFIG[next].defaultTimeframe);
  };

  const status = view === "materials" ? flowState.status : candlesState.status;
  const statusDetail = view === "materials" ? flowState.statusDetail : candlesState.statusDetail;
  const historyError = view === "materials" ? flowState.historyError : candlesState.historyError;

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div>
          <h1>Volume theory — live market</h1>
          <p className="subtitle">Spring Boot WebSocket → Next.js</p>
        </div>
        <StreamStatusBadge status={status} detail={statusDetail} historyError={historyError} />
      </header>

      <nav className="entity-tabs" aria-label="View">
        <button
          type="button"
          className={view === "candles" ? "tab active" : "tab"}
          onClick={() => setView("candles")}
        >
          Candles
        </button>
        <button
          type="button"
          className={view === "materials" ? "tab active" : "tab"}
          onClick={() => setView("materials")}
        >
          Materials
        </button>
      </nav>

      {view === "candles" && (
        <>
          <nav className="entity-tabs" aria-label="Market tabs">
            {(Object.keys(ENTITY_CONFIG) as MarketEntity[]).map((key) => (
              <button
                key={key}
                type="button"
                className={entity === key ? "tab active" : "tab"}
                onClick={() => switchEntity(key)}
              >
                {ENTITY_CONFIG[key].label}
              </button>
            ))}
          </nav>

          <div className="toolbar">
            <label htmlFor="timeframe">Timeframe</label>
            <select
              id="timeframe"
              value={timeframe}
              onChange={(e) => setTimeframe(e.target.value)}
            >
              {entityConfig.timeframes.map((tf) => (
                <option key={tf} value={tf}>
                  {tf}
                </option>
              ))}
            </select>
            <span className="candle-count">{candlesState.candles.length} candles</span>
          </div>

          <CandleChart
            candles={candlesState.candles}
            title={`${entityConfig.label} · ${timeframe}`}
          />
        </>
      )}

      {view === "materials" && (
        <>
          <p className="subtitle">Binance BTCUSDT · trades + order book · Kafka market-flow</p>
          <MaterialsPanel flow={flowState.flow} history={flowState.history} />
        </>
      )}
    </div>
  );
}
