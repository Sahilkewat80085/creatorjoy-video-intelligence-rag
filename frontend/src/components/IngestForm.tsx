"use client";

import { useState } from "react";
import { ingestVideos } from "@/lib/api";
import { IngestResponse } from "@/types";
import { Link as LinkIcon, Zap, Loader2, AlertCircle } from "lucide-react";

interface IngestFormProps {
  onSuccess: (data: IngestResponse) => void;
}

export default function IngestForm({ onSuccess }: IngestFormProps) {
  const [videoAUrl, setVideoAUrl] = useState("");
  const [videoBUrl, setVideoBUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (!videoAUrl.trim() || !videoBUrl.trim()) {
      setError("Both URLs are required.");
      return;
    }
    
    const isValidUrl = (url: string) => url.includes("youtube.com") || url.includes("youtu.be") || url.includes("instagram.com");

    if (!isValidUrl(videoAUrl)) {
      setError("Video A must be a valid YouTube or Instagram URL.");
      return;
    }
    if (!isValidUrl(videoBUrl)) {
      setError("Video B must be a valid YouTube or Instagram URL.");
      return;
    }

    setLoading(true);
    try {
      const data = await ingestVideos(videoAUrl.trim(), videoBUrl.trim());
      onSuccess(data);
    } catch (err: unknown) {
      const msg =
        err instanceof Error
          ? err.message
          : "Ingestion failed. Ensure the backend is running at localhost:8080.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        {/* Video A URL */}
        <div className="flex flex-col gap-1.5">
          <label className="text-xs font-medium text-white/50 uppercase tracking-widest flex items-center gap-1.5">
            <LinkIcon className="w-3.5 h-3.5 text-blue-400" />
            Video URL A
          </label>
          <input
            type="url"
            value={videoAUrl}
            onChange={(e) => setVideoAUrl(e.target.value)}
            placeholder="Paste a YouTube or Instagram Reel URL"
            disabled={loading}
            className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white placeholder:text-white/25 focus:outline-none focus:border-violet-500/60 focus:bg-white/8 transition-all disabled:opacity-50"
          />
        </div>

        {/* Video B URL */}
        <div className="flex flex-col gap-1.5">
          <label className="text-xs font-medium text-white/50 uppercase tracking-widest flex items-center gap-1.5">
            <LinkIcon className="w-3.5 h-3.5 text-blue-400" />
            Video URL B
          </label>
          <input
            type="url"
            value={videoBUrl}
            onChange={(e) => setVideoBUrl(e.target.value)}
            placeholder="Paste a YouTube or Instagram Reel URL"
            disabled={loading}
            className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white placeholder:text-white/25 focus:outline-none focus:border-violet-500/60 focus:bg-white/8 transition-all disabled:opacity-50"
          />
        </div>
      </div>

      {error && (
        <div className="mb-4 flex items-start gap-3 px-4 py-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-sm">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      <button
        type="submit"
        disabled={loading}
        className="w-full flex items-center justify-center gap-2 rounded-xl bg-violet-600 hover:bg-violet-500 active:scale-[0.98] disabled:opacity-60 disabled:cursor-not-allowed text-white font-semibold py-3 transition-all text-sm"
      >
        {loading ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" />
            Ingesting & embedding videos…
          </>
        ) : (
          <>
            <Zap className="w-4 h-4" />
            Analyze Videos
          </>
        )}
      </button>

      {loading && (
        <p className="text-center text-xs text-white/30 mt-2">
          This may take 30–90 seconds while we fetch, embed, and index the videos.
        </p>
      )}
    </form>
  );
}
