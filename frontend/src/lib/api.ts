import { IngestResponse, Citation } from "@/types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "https://creatorjoy-video-intelligence-rag-production.up.railway.app";

/**
 * Utility function to perform a fetch request with a customizable timeout.
 */
async function fetchWithTimeout(
  url: string,
  options: RequestInit = {},
  timeoutMs = 60000
): Promise<Response> {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    clearTimeout(id);
    return response;
  } catch (error) {
    clearTimeout(id);
    throw error;
  }
}

/**
 * Ingests two video URLs into the RAG pipeline.
 */
export async function ingestVideos(
  videoAUrl: string,
  videoBUrl: string
): Promise<IngestResponse> {
  const res = await fetchWithTimeout(`${API_BASE_URL}/api/ingest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      video_a_url: videoAUrl,
      video_b_url: videoBUrl,
    }),
  }, 120000); // 2 minutes timeout for slow transcription fallback tasks

  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || `Ingestion failed with status code ${res.status}`);
  }

  return res.json();
}

/**
 * Requests RAG analysis answer directly (non-streaming).
 */
export async function chat(
  sessionId: string,
  question: string
): Promise<{ answer: string; citations: Citation[] }> {
  const res = await fetchWithTimeout(`${API_BASE_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, question }),
  }, 30000);

  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || `Chat failed with status code ${res.status}`);
  }

  return res.json();
}

/**
 * Requests RAG analysis answer as an async generator stream.
 */
export async function* chatStream(
  sessionId: string,
  question: string
): AsyncGenerator<{ type: string; content?: string; citations?: Citation[] }> {
  // Streaming doesn't use a short timeout but we can enforce a connection timeout
  const controller = new AbortController();
  const connectionTimeoutId = setTimeout(() => controller.abort(), 10000);

  const res = await fetch(`${API_BASE_URL}/api/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, question }),
    signal: controller.signal,
  });

  clearTimeout(connectionTimeoutId);

  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || `Streaming connection failed with status code ${res.status}`);
  }

  if (!res.body) {
    throw new Error("No readable response body provided for streaming.");
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        const trimmed = line.trim();
        if (trimmed) {
          try {
            yield JSON.parse(trimmed);
          } catch (e) {
            console.error("Failed to parse JSON token stream line:", trimmed, e);
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}

