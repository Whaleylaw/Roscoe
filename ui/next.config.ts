import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Allow cross-origin requests from VM IP
  experimental: {
    serverActions: {
      bodySizeLimit: "2mb",
    },
  },

  // Turbopack config (empty to silence warning)
  turbopack: {},

  // Webpack config for PDF.js
  webpack: (config) => {
    config.resolve.alias.canvas = false;
    return config;
  },
};

export default nextConfig;
