export type MarketEntity = "btc" | "gold";

export interface CandleOhlcv {
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  trade_count?: number;
}

export interface CandleEnvelope {
  entity: MarketEntity;
  source: string;
  symbol: string;
  timeframe: string;
  bucket_epoch: number;
  event_time_ms: number;
  payload: CandleOhlcv;
}

export interface ClientFilter {
  entity: MarketEntity;
  timeframe: string;
}

export type StreamStatus = "connecting" | "open" | "closed" | "error";
