import "./globals.css";
import type { Metadata } from "next";
import { ClerkProvider } from "@clerk/nextjs";
import { config } from "@/lib/config";

export const metadata: Metadata = {
  title: "AI Trading — Live Candles",
  description: "Binance BTC and Deriv gold candle stream",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const body = (
    <html lang="en">
      <body>{children}</body>
    </html>
  );

  if (!config.clerkEnabled) {
    return body;
  }

  return <ClerkProvider>{body}</ClerkProvider>;
}
