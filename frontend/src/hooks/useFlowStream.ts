"use client";

import { useEffect, useState } from "react";
import { fetchLatestFlow } from "@/lib/api/flow-api";
import { FlowStreamClient } from "@/lib/stream/flow-stream";
import type { StreamStatus } from "@/types/candle";
import type { FlowSnapshot } from "@/types/flow";

const MAX_HISTORY = 300;

function appendHistory(list: FlowSnapshot[], next: FlowSnapshot): FlowSnapshot[] {
  const idx = list.findIndex((row) => row.bucket_epoch === next.bucket_epoch);
  if (idx >= 0) {
    const copy = [...list];
    copy[idx] = next;
    return copy;
  }
  return [...list, next]
    .sort((a, b) => a.bucket_epoch - b.bucket_epoch)
    .slice(-MAX_HISTORY);
}

export function useFlowStream(symbol: string) {
  const [flow, setFlow] = useState<FlowSnapshot | null>(null);
  const [history, setHistory] = useState<FlowSnapshot[]>([]);
  const [status, setStatus] = useState<StreamStatus>("connecting");
  const [statusDetail, setStatusDetail] = useState<string | undefined>();
  const [historyError, setHistoryError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setHistoryError(null);
    setHistory([]);
    fetchLatestFlow(symbol)
      .then((row) => {
        if (!cancelled && row) {
          setFlow(row);
          setHistory((prev) => appendHistory(prev, row));
        }
      })
      .catch((err: Error) => {
        if (!cancelled) {
          setHistoryError(err.message);
        }
      });

    const client = new FlowStreamClient(
      (snap) => {
        setFlow(snap);
        setHistory((prev) => appendHistory(prev, snap));
      },
      (next, detail) => {
        setStatus(next);
        setStatusDetail(detail);
      },
    );
    client.connect(symbol);

    return () => {
      cancelled = true;
      client.dispose();
    };
  }, [symbol]);

  return { flow, history, status, statusDetail, historyError };
}
