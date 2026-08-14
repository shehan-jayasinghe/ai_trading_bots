import Link from "next/link";
import { config } from "@/lib/config";

export default function HomePage() {
  return (
    <main className="landing">
      <h1>AI Trading Bots</h1>
      <p>Live candle charts from Kafka via Spring Boot WebSocket.</p>
      <Link href="/dashboard" className="primary-btn">
        Open dashboard
      </Link>
      {!config.clerkEnabled && (
        <p className="hint">Clerk keys not set — dashboard is open without login.</p>
      )}
    </main>
  );
}
