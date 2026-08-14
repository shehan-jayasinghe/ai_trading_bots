"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { fetchRecentCandles } from "@/lib/api/candle-api";
import { CandleStreamClient } from "@/lib/stream/candle-stream";
import type { CandleEnvelope, MarketEntity, StreamStatus } from "@/types/candle";

const MAX_CANDLES = 500;

function upsertCandle(list: CandleEnvelope[], next: CandleEnvelope): CandleEnvelope[] {
  const idx = list.findIndex(
    (c) => c.timeframe === next.timeframe && c.bucket_epoch === next.bucket_epoch,
  );
  if (idx >= 0) {
    const copy = [...list];
    copy[idx] = next;
    return copy;
  }
  const merged = [...list, next].sort((a, b) => a.bucket_epoch - b.bucket_epoch);
  return merged.slice(-MAX_CANDLES);
}

export function useCandleStream(entity: MarketEntity, timeframe: string) {
  const [candles, setCandles] = useState<CandleEnvelope[]>([]);
  const [status, setStatus] = useState<StreamStatus>("connecting");
  const [statusDetail, setStatusDetail] = useState<string | undefined>();
  const [historyError, setHistoryError] = useState<string | null>(null);
  const clientRef = useRef<CandleStreamClient | null>(null);

  const handleMessage = useCallback((candle: CandleEnvelope) => {
    if (candle.entity !== entity || candle.timeframe !== timeframe) {
      return;
    }
    setCandles((prev) => upsertCandle(prev, candle));
  }, [entity, timeframe]);

  useEffect(() => {
    let cancelled = false;
    setHistoryError(null);
    setCandles([]);

    fetchRecentCandles(entity, timeframe)
      .then((rows) => {
        if (!cancelled) {
          setCandles(rows);
        }
      })
      .catch((err: Error) => {
        if (!cancelled) {
          setHistoryError(err.message);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [entity, timeframe]);

  useEffect(() => {
    const client = new CandleStreamClient(
      handleMessage,
      (nextStatus, detail) => {
        setStatus(nextStatus);
        setStatusDetail(detail);
      },
    );
    clientRef.current = client;
    client.connect({ entity, timeframe });

    return () => {
      client.dispose();
      clientRef.current = null;
    };
  }, [entity, timeframe, handleMessage]);

  return { candles, status, statusDetail, historyError };
}
