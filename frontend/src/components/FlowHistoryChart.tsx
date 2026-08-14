"use client";

import { useEffect, useRef } from "react";
import { ColorType, createChart, type IChartApi, type ISeriesApi, type UTCTimestamp } from "lightweight-charts";
import type { FlowSnapshot } from "@/types/flow";

export function FlowHistoryChart({ history }: { history: FlowSnapshot[] }) {
  const priceRef = useRef<HTMLDivElement>(null);
  const flowRef = useRef<HTMLDivElement>(null);
  const priceChart = useRef<IChartApi | null>(null);
  const flowChart = useRef<IChartApi | null>(null);
  const priceSeries = useRef<ISeriesApi<"Line"> | null>(null);
  const buySeries = useRef<ISeriesApi<"Line"> | null>(null);
  const sellSeries = useRef<ISeriesApi<"Line"> | null>(null);
  const deltaSeries = useRef<ISeriesApi<"Histogram"> | null>(null);

  useEffect(() => {
    if (!priceRef.current || !flowRef.current) return;

    const common = {
      layout: {
        background: { type: ColorType.Solid, color: "#0f1419" },
        textColor: "#c9d1d9",
      },
      grid: {
        vertLines: { color: "#21262d" },
        horzLines: { color: "#21262d" },
      },
      timeScale: { timeVisible: true, secondsVisible: true },
      rightPriceScale: { borderColor: "#30363d" },
    };

    const pChart = createChart(priceRef.current, {
      ...common,
      width: priceRef.current.clientWidth,
      height: 220,
    });
    priceSeries.current = pChart.addLineSeries({ color: "#58a6ff", lineWidth: 2, title: "Price" });

    const fChart = createChart(flowRef.current, {
      ...common,
      width: flowRef.current.clientWidth,
      height: 240,
    });
    buySeries.current = fChart.addLineSeries({ color: "#3fb950", lineWidth: 2, title: "Buy 1s" });
    sellSeries.current = fChart.addLineSeries({ color: "#f85149", lineWidth: 2, title: "Sell 1s" });
    deltaSeries.current = fChart.addHistogramSeries({ title: "Delta" });

    priceChart.current = pChart;
    flowChart.current = fChart;

    const onResize = () => {
      if (priceRef.current) pChart.applyOptions({ width: priceRef.current.clientWidth });
      if (flowRef.current) fChart.applyOptions({ width: flowRef.current.clientWidth });
    };
    window.addEventListener("resize", onResize);

    return () => {
      window.removeEventListener("resize", onResize);
      pChart.remove();
      fChart.remove();
      priceChart.current = null;
      flowChart.current = null;
    };
  }, []);

  useEffect(() => {
    const prices = history.map((h) => ({
      time: h.bucket_epoch as UTCTimestamp,
      value: h.price,
    }));
    const buys = history.map((h) => ({
      time: h.bucket_epoch as UTCTimestamp,
      value: h.buy_volume,
    }));
    const sells = history.map((h) => ({
      time: h.bucket_epoch as UTCTimestamp,
      value: h.sell_volume,
    }));
    const deltas = history.map((h) => ({
      time: h.bucket_epoch as UTCTimestamp,
      value: h.delta,
      color: h.delta >= 0 ? "#3fb950" : "#f85149",
    }));

    priceSeries.current?.setData(prices);
    buySeries.current?.setData(buys);
    sellSeries.current?.setData(sells);
    deltaSeries.current?.setData(deltas);
    priceChart.current?.timeScale().scrollToRealTime();
    flowChart.current?.timeScale().scrollToRealTime();
  }, [history]);

  return (
    <div className="flow-charts">
      <h3 className="chart-title">Price over time</h3>
      <div ref={priceRef} />
      <h3 className="chart-title">Buy / sell / delta (each second, kept on the chart)</h3>
      <div ref={flowRef} />
      {history.length < 2 && <p className="chart-empty-static">Collecting seconds… graph fills as 1s bars close.</p>}
    </div>
  );
}
