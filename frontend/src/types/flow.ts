export interface FlowWindow {
  buy_volume: number;
  sell_volume: number;
  delta: number;
  buy_aggression: number | null;
}

export interface FlowSnapshot {
  symbol: string;
  entity?: string;
  source?: string;
  window_sec: number;
  bucket_epoch: number;
  price: number;
  buy_volume: number;
  sell_volume: number;
  delta: number;
  buy_aggression: number | null;
  pressure: string;
  bid_liquidity: number;
  ask_liquidity: number;
  liquidity_imbalance: number | null;
  reaction: string;
  windows?: {
    "5s"?: FlowWindow;
    "15s"?: FlowWindow;
    "1m"?: FlowWindow;
  };
}
