"use client";

import { useState } from "react";
import { CandleChart } from "@/components/CandleChart";
import { StreamStatusBadge } from "@/components/StreamStatus";
import { useCandleStream } from "@/hooks/useCandleStream";
import { ENTITY_CONFIG } from "@/lib/config";
import type { MarketEntity } from "@/types/candle";

export function Dashboard() {
  const [entity, setEntity] = useState<MarketEntity>("btc");
  const entityConfig = ENTITY_CONFIG[entity];
  const [timeframe, setTimeframe] = useState<string>(entityConfig.defaultTimeframe);

  const { candles, status, statusDetail, historyError } = useCandleStream(entity, timeframe);

  const switchEntity = (next: MarketEntity) => {
    setEntity(next);
    setTimeframe(ENTITY_CONFIG[next].defaultTimeframe);
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div>
          <h1>Volume theory — live candles</h1>
          <p className="subtitle">Spring Boot WebSocket → Next.js</p>
        </div>
        <StreamStatusBadge status={status} detail={statusDetail} historyError={historyError} />
      </header>

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
        <span className="candle-count">{candles.length} candles</span>
      </div>

      <CandleChart
        candles={candles}
        title={`${entityConfig.label} · ${timeframe}`}
      />
    </div>
  );
}
