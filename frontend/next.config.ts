import type { NextConfig } from "next";

const backendUrl = process.env.BACKEND_URL ?? "http://127.0.0.1:8080";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      { source: "/api/candles", destination: `${backendUrl}/api/candles` },
      { source: "/api/flow", destination: `${backendUrl}/api/flow` },
      { source: "/health", destination: `${backendUrl}/health` },
      { source: "/backend/:path*", destination: `${backendUrl}/:path*` },
    ];
  },
};

export default nextConfig;
