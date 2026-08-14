const BACKEND_PORT = 8080;

/** Browser: same-origin (Next.js rewrites → Spring). SSR: env or localhost. */
function resolveApiUrl(): string {
  if (typeof window !== "undefined") {
    return window.location.origin;
  }
  return process.env.NEXT_PUBLIC_API_URL ?? `http://localhost:${BACKEND_PORT}`;
}

/** Match page host so ws://127.0.0.1:8080 works when opened via 127.0.0.1:3000. */
function resolveWsUrl(path: "/ws" | "/ws/flow"): string {
  if (typeof window !== "undefined") {
    return `ws://${window.location.hostname}:${BACKEND_PORT}${path}`;
  }
  if (path === "/ws/flow") {
    return process.env.NEXT_PUBLIC_WS_FLOW_URL ?? `ws://localhost:${BACKEND_PORT}/ws/flow`;
  }
  return process.env.NEXT_PUBLIC_WS_URL ?? `ws://localhost:${BACKEND_PORT}/ws`;
}

export const config = {
  get apiUrl() {
    return resolveApiUrl();
  },
  get wsUrl() {
    return resolveWsUrl("/ws");
  },
  get wsFlowUrl() {
    return resolveWsUrl("/ws/flow");
  },
  clerkEnabled: Boolean(process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY),
};

export const ENTITY_CONFIG = {
  btc: {
    label: "Binance BTC",
    defaultTimeframe: "1m",
    timeframes: ["1s", "1m", "2m", "5m"],
  },
  gold: {
    label: "Deriv Gold",
    defaultTimeframe: "1m",
    timeframes: ["1s", "1m", "2m", "3m", "5m"],
  },
} as const;
