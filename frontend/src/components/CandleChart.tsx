"use client";

import {
  ColorType,
  createChart,
  type IChartApi,
  type ISeriesApi,
  type CandlestickData,
  type Time,
} from "lightweight-charts";
import { useEffect, useRef } from "react";
import type { CandleEnvelope } from "@/types/candle";

interface CandleChartProps {
  candles: CandleEnvelope[];
  title: string;
}

function toChartData(candles: CandleEnvelope[]): CandlestickData<Time>[] {
  return candles.map((c) => ({
    time: c.bucket_epoch as Time,
    open: c.payload.open,
    high: c.payload.high,
    low: c.payload.low,
    close: c.payload.close,
  }));
}

export function CandleChart({ candles, title }: CandleChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const chart = createChart(containerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: "#0f1419" },
        textColor: "#c9d1d9",
      },
      grid: {
        vertLines: { color: "#21262d" },
        horzLines: { color: "#21262d" },
      },
      width: containerRef.current.clientWidth,
      height: 420,
      timeScale: { timeVisible: true, secondsVisible: true },
    });

    const series = chart.addCandlestickSeries({
      upColor: "#3fb950",
      downColor: "#f85149",
      borderVisible: false,
      wickUpColor: "#3fb950",
      wickDownColor: "#f85149",
    });

    chartRef.current = chart;
    seriesRef.current = series;

    const onResize = () => {
      if (containerRef.current) {
        chart.applyOptions({ width: containerRef.current.clientWidth });
      }
    };
    window.addEventListener("resize", onResize);

    return () => {
      window.removeEventListener("resize", onResize);
      chart.remove();
      chartRef.current = null;
      seriesRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!seriesRef.current) return;
    seriesRef.current.setData(toChartData(candles));
    chartRef.current?.timeScale().scrollToRealTime();
  }, [candles]);

  return (
    <section className="chart-panel">
      <h2 className="chart-title">{title}</h2>
      <div ref={containerRef} className="chart-container" />
      {candles.length === 0 && <p className="chart-empty">Waiting for candle data…</p>}
    </section>
  );
}
