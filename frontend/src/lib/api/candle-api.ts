import type { CandleEnvelope, MarketEntity } from "@/types/candle";
import { config } from "@/lib/config";

export async function fetchRecentCandles(
  entity: MarketEntity,
  timeframe: string,
): Promise<CandleEnvelope[]> {
  const url = new URL("/api/candles", config.apiUrl);
  url.searchParams.set("entity", entity);
  url.searchParams.set("timeframe", timeframe);

  const res = await fetch(url.toString(), { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`History fetch failed: ${res.status}`);
  }
  return res.json() as Promise<CandleEnvelope[]>;
}

export async function fetchHealth(): Promise<{ ok: boolean; websocketSessions?: number }> {
  const res = await fetch(`${config.apiUrl}/health`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Health check failed: ${res.status}`);
  }
  return res.json();
}
