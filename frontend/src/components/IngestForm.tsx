"use client";

import { useState } from "react";
import { ingestVideos } from "@/lib/api";
import { IngestResponse } from "@/types";
import { Link as LinkIcon, Zap, Loader2, AlertCircle, Sparkles } from "lucide-react";

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

    const urlA = videoAUrl.trim();
    const urlB = videoBUrl.trim();

    if (!urlA || !urlB) {
      setError("Please provide URLs for both Video A and Video B to proceed with the analysis.");
      return;
    }
    
    const isValidUrl = (url: string) => {
      const lower = url.toLowerCase();
      return lower.includes("youtube.com") || lower.includes("youtu.be") || lower.includes("instagram.com");
    };

    if (!isValidUrl(urlA)) {
      setError("Video URL A must be a valid YouTube (watch / Shorts) or Instagram Reel link.");
      return;
    }
    if (!isValidUrl(urlB)) {
      setError("Video URL B must be a valid YouTube (watch / Shorts) or Instagram Reel link.");
      return;
    }

    setLoading(true);
    try {
      const data = await ingestVideos(urlA, urlB);
      onSuccess(data);
    } catch (err: unknown) {
      const msg =
        err instanceof Error
          ? err.message
          : "Network connection refused. Please ensure the backend is running locally at http://localhost:8080.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="w-full animate-in fade-in duration-300">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-5">
        {/* Video A URL */}
        <div className="flex flex-col gap-2 group">
          <label className="text-[11px] font-semibold text-white/50 uppercase tracking-widest flex items-center gap-1.5 transition-colors group-focus-within:text-violet-400">
            <LinkIcon className="w-3.5 h-3.5 text-violet-400 shrink-0" />
            Video URL A (YouTube / Instagram)
          </label>
          <input
            type="url"
            value={videoAUrl}
            onChange={(e) => setVideoAUrl(e.target.value)}
            placeholder="e.g., https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            disabled={loading}
            className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white placeholder:text-white/20 focus:outline-none focus:border-violet-500/50 focus:bg-white/8 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-inner"
          />
        </div>

        {/* Video B URL */}
        <div className="flex flex-col gap-2 group">
          <label className="text-[11px] font-semibold text-white/50 uppercase tracking-widest flex items-center gap-1.5 transition-colors group-focus-within:text-cyan-400">
            <LinkIcon className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
            Video URL B (YouTube / Instagram)
          </label>
          <input
            type="url"
            value={videoBUrl}
            onChange={(e) => setVideoBUrl(e.target.value)}
            placeholder="e.g., https://www.instagram.com/reels/DYGZgr5IfaN/"
            disabled={loading}
            className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white placeholder:text-white/20 focus:outline-none focus:border-cyan-500/50 focus:bg-white/8 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-inner"
          />
        </div>
      </div>

      {error && (
        <div className="mb-5 flex items-start gap-3 px-4 py-3.5 rounded-xl bg-rose-500/10 border border-rose-500/25 text-rose-400 text-sm animate-in fade-in slide-in-from-top-1 duration-200">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
          <span className="font-medium">{error}</span>
        </div>
      )}

      <button
        type="submit"
        disabled={loading}
        className="w-full flex items-center justify-center gap-2 rounded-xl bg-violet-600 hover:bg-violet-500 active:scale-[0.99] disabled:opacity-60 disabled:cursor-not-allowed disabled:active:scale-100 text-white font-semibold py-3.5 transition-all text-sm shadow-md hover:shadow-violet-600/15"
      >
        {loading ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin text-white" />
            <span>Ingesting & processing transcripts (30-90s)...</span>
          </>
        ) : (
          <>
            <Sparkles className="w-4 h-4 text-violet-200" />
            <span>Analyze & Compare Videos</span>
          </>
        )}
      </button>

      {loading && (
        <div className="flex items-center justify-center gap-2 mt-3 text-center text-xs text-white/30 animate-pulse">
          <Zap className="w-3 h-3 text-amber-400" />
          <span>Local audio transcription fallbacks might execute if subtitles are disabled.</span>
        </div>
      )}
    </form>
  );
}

