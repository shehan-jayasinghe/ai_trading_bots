export const config = {
  apiUrl: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080",
  wsUrl: process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8080/ws",
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
