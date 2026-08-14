import type { StreamStatus } from "@/types/candle";

interface StreamStatusProps {
  status: StreamStatus;
  detail?: string;
  historyError?: string | null;
}

const LABELS: Record<StreamStatus, string> = {
  connecting: "Connecting…",
  open: "Live",
  closed: "Disconnected",
  error: "Error",
};

export function StreamStatusBadge({ status, detail, historyError }: StreamStatusProps) {
  return (
    <div className="stream-status">
      <span className={`status-dot status-${status}`} />
      <span>{LABELS[status]}</span>
      {detail && <span className="status-detail">{detail}</span>}
      {historyError && <span className="status-error">History: {historyError}</span>}
    </div>
  );
}
