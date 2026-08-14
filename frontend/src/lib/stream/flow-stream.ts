import type { FlowSnapshot } from "@/types/flow";
import type { StreamStatus } from "@/types/candle";
import { config } from "@/lib/config";

type MessageHandler = (snap: FlowSnapshot) => void;
type StatusHandler = (status: StreamStatus, detail?: string) => void;

export class FlowStreamClient {
  private ws: WebSocket | null = null;
  private symbol = "BTCUSDT";
  private onMessage: MessageHandler;
  private onStatus: StatusHandler;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;

  constructor(onMessage: MessageHandler, onStatus: StatusHandler) {
    this.onMessage = onMessage;
    this.onStatus = onStatus;
  }

  connect(symbol: string) {
    this.symbol = symbol;
    this.clearReconnect();
    this.close();
    this.onStatus("connecting");
    const ws = new WebSocket(config.wsFlowUrl);
    this.ws = ws;

    ws.onopen = () => {
      this.onStatus("open");
      ws.send(JSON.stringify({ symbol: this.symbol }));
    };

    ws.onmessage = (event) => {
      const raw = event.data as string;
      if (raw.includes('"status":"filter_updated"')) {
        return;
      }
      try {
        const snap = JSON.parse(raw) as FlowSnapshot;
        if (snap.symbol && snap.price != null) {
          this.onMessage(snap);
        }
      } catch {
        // ignore
      }
    };

    ws.onerror = () =>
      this.onStatus("error", "WebSocket error — is Spring Boot running on :8080?");
    ws.onclose = (event) => {
      const detail =
        event.code === 1006
          ? "Connection refused — start realtime-spring (port 8080)"
          : event.reason || undefined;
      this.onStatus("closed", detail);
      this.scheduleReconnect();
    };
  }

  dispose() {
    this.clearReconnect();
    this.close();
  }

  private close() {
    if (this.ws) {
      this.ws.onclose = null;
      this.ws.close();
      this.ws = null;
    }
  }

  private scheduleReconnect() {
    this.clearReconnect();
    this.reconnectTimer = setTimeout(() => this.connect(this.symbol), 3000);
  }

  private clearReconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }
}
