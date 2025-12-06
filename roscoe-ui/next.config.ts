import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable standalone output for Docker
  output: 'standalone',
  
  // Exclude problematic packages from server bundle
  serverExternalPackages: ["thread-stream", "pino", "pino-pretty"],
  
  // Empty turbopack config to silence warning
  turbopack: {},
};

export default nextConfig;
