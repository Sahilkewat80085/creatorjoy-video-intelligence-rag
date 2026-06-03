import { IngestResponse, Citation } from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "https://creatorjoy-video-intelligence-rag-production.up.railway.app";

export async function ingestVideos(
  videoAUrl: string,
  videoBUrl: string
): Promise<IngestResponse> {
  const res = await fetch(`${API_BASE_URL}/api/ingest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      video_a_url: videoAUrl,
      video_b_url: videoBUrl,
    }),
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || `Ingestion failed with status ${res.status}`);
  }

  return res.json();
}

export async function chat(
  sessionId: string,
  question: string
): Promise<{ answer: string; citations: Citation[] }> {
  const res = await fetch(`${API_BASE_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, question }),
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || `Chat failed with status ${res.status}`);
  }

  return res.json();
}

export async function* chatStream(
  sessionId: string,
  question: string
): AsyncGenerator<{ type: string; content?: string; citations?: Citation[] }> {
  const res = await fetch(`${API_BASE_URL}/api/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, question }),
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || `Stream failed with status ${res.status}`);
  }

  if (!res.body) throw new Error("No response body for streaming");

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";
    
    for (const line of lines) {
      if (line.trim()) {
        try {
          yield JSON.parse(line);
        } catch (e) {
          console.error("Failed to parse stream line:", line);
        }
      }
    }
  }
}
