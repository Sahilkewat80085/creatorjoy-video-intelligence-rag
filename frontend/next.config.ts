import type { NextConfig } from "next";

// Target endpoint URL of the RAG microservice. Defaults to Railway staging/production environment.
const BACKEND_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "https://creatorjoy-video-intelligence-rag-production.up.railway.app";

const nextConfig: NextConfig = {
  /**
   * Configures NextJS rewrites to seamlessly proxy api requests to backend pipelines
   * without triggering Cross-Origin Resource Sharing (CORS) exceptions in browsers.
   */
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${BACKEND_URL}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;

