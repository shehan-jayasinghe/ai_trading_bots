import type { FlowSnapshot } from "@/types/flow";
import { config } from "@/lib/config";

export async function fetchLatestFlow(symbol: string): Promise<FlowSnapshot | null> {
  const url = new URL("/api/flow", config.apiUrl);
  url.searchParams.set("symbol", symbol);
  const res = await fetch(url.toString(), { cache: "no-store" });
  if (res.status === 204) {
    return null;
  }
  if (!res.ok) {
    throw new Error(`Flow fetch failed: ${res.status}`);
  }
  return res.json() as Promise<FlowSnapshot>;
}
