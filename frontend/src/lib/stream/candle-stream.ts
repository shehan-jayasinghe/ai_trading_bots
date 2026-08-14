import type { CandleEnvelope, ClientFilter, StreamStatus } from "@/types/candle";
import { config } from "@/lib/config";

type MessageHandler = (candle: CandleEnvelope) => void;
type StatusHandler = (status: StreamStatus, detail?: string) => void;

export class CandleStreamClient {
  private ws: WebSocket | null = null;
  private filter: ClientFilter | null = null;
  private onMessage: MessageHandler;
  private onStatus: StatusHandler;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;

  constructor(onMessage: MessageHandler, onStatus: StatusHandler) {
    this.onMessage = onMessage;
    this.onStatus = onStatus;
  }

  connect(filter: ClientFilter) {
    this.filter = filter;
    this.clearReconnect();
    this.close();

    this.onStatus("connecting");
    const ws = new WebSocket(config.wsUrl);
    this.ws = ws;

    ws.onopen = () => {
      this.onStatus("open");
      ws.send(JSON.stringify({ entity: filter.entity, timeframe: filter.timeframe }));
    };

    ws.onmessage = (event) => {
      const raw = event.data as string;
      if (raw.includes('"status":"filter_updated"')) {
        return;
      }
      try {
        const candle = JSON.parse(raw) as CandleEnvelope;
        if (candle.entity && candle.payload) {
          this.onMessage(candle);
        }
      } catch {
        // ignore non-candle frames
      }
    };

    ws.onerror = () => {
      this.onStatus("error", "WebSocket error");
    };

    ws.onclose = () => {
      this.onStatus("closed");
      this.scheduleReconnect();
    };
  }

  updateFilter(filter: ClientFilter) {
    this.filter = filter;
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ entity: filter.entity, timeframe: filter.timeframe }));
      return;
    }
    this.connect(filter);
  }

  close() {
    if (this.ws) {
      this.ws.onclose = null;
      this.ws.close();
      this.ws = null;
    }
  }

  dispose() {
    this.clearReconnect();
    this.close();
  }

  private scheduleReconnect() {
    if (!this.filter) return;
    this.clearReconnect();
    this.reconnectTimer = setTimeout(() => {
      if (this.filter) {
        this.connect(this.filter);
      }
    }, 3000);
  }

  private clearReconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }
}
