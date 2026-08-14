"use client";

import { FlowHistoryChart } from "@/components/FlowHistoryChart";
import type { FlowSnapshot, FlowWindow } from "@/types/flow";

function fmt(n: number | null | undefined, digits = 3): string {
  if (n == null || Number.isNaN(n)) return "—";
  return n.toLocaleString(undefined, { maximumFractionDigits: digits });
}

function pct(n: number | null | undefined): string {
  if (n == null) return "—";
  return `${(n * 100).toFixed(1)}%`;
}

function WindowRow({ label, w }: { label: string; w?: FlowWindow }) {
  if (!w) return null;
  return (
    <tr>
      <td>{label}</td>
      <td>{fmt(w.buy_volume)}</td>
      <td>{fmt(w.sell_volume)}</td>
      <td className={w.delta >= 0 ? "pos" : "neg"}>{fmt(w.delta)}</td>
      <td>{pct(w.buy_aggression)}</td>
    </tr>
  );
}

export function MaterialsPanel({
  flow,
  history,
}: {
  flow: FlowSnapshot | null;
  history: FlowSnapshot[];
}) {
  if (!flow) {
    return <p className="chart-empty-static">Waiting for market-flow materials…</p>;
  }

  const m1 = flow.windows?.["1m"];
  const agr = m1?.buy_aggression ?? flow.buy_aggression;
  const imb = flow.liquidity_imbalance;

  return (
    <section className="materials">
      <div className="materials-hero">
        <div>
          <div className="materials-symbol">{flow.symbol} · last {history.length}s kept on chart</div>
          <div className="materials-price">{fmt(flow.price, 2)}</div>
        </div>
        <div className={`reaction reaction-${flow.reaction}`}>
          {flow.reaction === "none" ? "No reaction yet" : flow.reaction.replace(/_/g, " ")}
        </div>
      </div>

      <p className="subtitle">Cards below use the rolling <strong>1 minute</strong> (easier to track). Instant 1s is in the table and graph.</p>

      <div className="metric-grid">
        <article>
          <h3>Buy volume (1m)</h3>
          <p>{fmt(m1?.buy_volume ?? flow.buy_volume)}</p>
          <span className="metric-sub">this second {fmt(flow.buy_volume)}</span>
        </article>
        <article>
          <h3>Sell volume (1m)</h3>
          <p>{fmt(m1?.sell_volume ?? flow.sell_volume)}</p>
          <span className="metric-sub">this second {fmt(flow.sell_volume)}</span>
        </article>
        <article>
          <h3>Delta (1m)</h3>
          <p className={(m1?.delta ?? flow.delta) >= 0 ? "pos" : "neg"}>{fmt(m1?.delta ?? flow.delta)}</p>
          <span className="metric-sub">this second {fmt(flow.delta)}</span>
        </article>
        <article>
          <h3>Buy aggression (1m)</h3>
          <p>{pct(agr)}</p>
          <span className="metric-sub">{flow.pressure} · 1s {pct(flow.buy_aggression)}</span>
        </article>
        <article>
          <h3>Bid liquidity (0.5%)</h3>
          <p>{fmt(flow.bid_liquidity)}</p>
        </article>
        <article>
          <h3>Ask liquidity (0.5%)</h3>
          <p>{fmt(flow.ask_liquidity)}</p>
        </article>
        <article>
          <h3>Liquidity imbalance</h3>
          <p className={(imb ?? 0) >= 0 ? "pos" : "neg"}>{pct(imb)}</p>
        </article>
      </div>

      <FlowHistoryChart history={history} />

      <table className="window-table">
        <thead>
          <tr>
            <th>Window</th>
            <th>Buy</th>
            <th>Sell</th>
            <th>Delta</th>
            <th>Aggression</th>
          </tr>
        </thead>
        <tbody>
          <WindowRow label="1s (now)" w={{
            buy_volume: flow.buy_volume,
            sell_volume: flow.sell_volume,
            delta: flow.delta,
            buy_aggression: flow.buy_aggression,
          }} />
          <WindowRow label="5s" w={flow.windows?.["5s"]} />
          <WindowRow label="15s" w={flow.windows?.["15s"]} />
          <WindowRow label="1m" w={flow.windows?.["1m"]} />
        </tbody>
      </table>
    </section>
  );
}
