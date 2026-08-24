"use client";

import { useState, useRef, useEffect } from "react";
import { IngestResponse } from "@/types";
import IngestForm from "@/components/IngestForm";
import VideoCard from "@/components/VideoCard";
import Chat from "@/components/Chat";
import { Brain, ChevronDown, RotateCcw } from "lucide-react";

export default function Home() {
  const [sessionId, setSessionId] = useState<string>("");
  const [ingestData, setIngestData] = useState<IngestResponse | null>(null);
  const chatRef = useRef<HTMLDivElement>(null);

  // Generate session ID on the client to avoid NextJS SSR hydration mismatch
  useEffect(() => {
    setSessionId(crypto.randomUUID());
  }, []);

  function handleIngestSuccess(data: IngestResponse) {
    setIngestData(data);
    setTimeout(() => {
      chatRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 300);
  }

  function handleReset() {
    setIngestData(null);
  }

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white bg-grid-pattern relative">
      {/* Premium Ambient Background Blobs */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
        <div className="absolute -top-64 -left-64 w-[600px] h-[600px] rounded-full bg-violet-950/20 blur-[120px] animate-pulse-glow" />
        <div className="absolute top-1/2 -right-64 w-[500px] h-[500px] rounded-full bg-cyan-950/15 blur-[100px] animate-pulse-glow" style={{ animationDelay: "-5s" }} />
        <div className="absolute -bottom-32 left-1/3 w-[400px] h-[400px] rounded-full bg-indigo-950/25 blur-[120px] animate-pulse-glow" style={{ animationDelay: "-10s" }} />
      </div>

      <div className="relative z-10 max-w-6xl mx-auto px-4 py-10 flex flex-col gap-10">
        {/* Header */}
        <header className="text-center py-6 flex flex-col items-center animate-in fade-in duration-500">
          <div className="inline-flex items-center gap-3 mb-5 hover:scale-105 transition-transform cursor-default">
            <div className="w-10 h-10 rounded-2xl bg-violet-600/20 border border-violet-500/30 flex items-center justify-center shadow-lg shadow-violet-950/30">
              <Brain className="w-5 h-5 text-violet-400" />
            </div>
            <span className="text-xs font-semibold uppercase tracking-[0.25em] text-violet-400 border border-violet-500/20 px-3.5 py-1.5 rounded-full bg-violet-500/5 backdrop-blur-md">
              RAG-Powered content analyzer
            </span>
          </div>
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold bg-gradient-to-r from-white via-zinc-100 to-zinc-400 bg-clip-text text-transparent mb-4 tracking-tight">
            Creator Intelligence AI
          </h1>
          <p className="text-white/50 text-base md:text-lg max-w-lg mx-auto leading-relaxed">
            Compare YouTube and Instagram Reels content using retrieval-augmented LLM verification
          </p>
        </header>

        {/* Video sources Ingestion Section */}
        <section className="rounded-2xl border border-white/10 bg-white/[0.02] backdrop-blur-md p-6 shadow-xl shadow-black/25 transition-all hover:border-white/15 animate-in fade-in duration-700 slide-in-from-bottom-2">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-lg font-semibold text-white tracking-wide">Video Sources</h2>
              <p className="text-sm text-white/40 mt-1">
                Provide two video URLs (YouTube or Instagram Reel) to begin the ingestion process.
              </p>
            </div>
            {ingestData && (
              <button
                onClick={handleReset}
                className="flex items-center gap-1.5 text-xs text-white/40 hover:text-rose-400 transition-colors border border-white/10 hover:border-rose-500/20 rounded-xl px-3.5 py-2 bg-white/5 shadow-sm active:scale-95"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Reset Ingestion</span>
              </button>
            )}
          </div>
          <IngestForm onSuccess={handleIngestSuccess} />
        </section>

        {/* Comparison Dashboard */}
        {ingestData && (
          <section className="animate-in fade-in duration-500 slide-in-from-bottom-2">
            <div className="flex items-center gap-3 mb-5">
              <h2 className="text-lg font-semibold text-white tracking-wide">Video Comparison Dashboard</h2>
              <div className="h-px flex-1 bg-white/10" />
              <ChevronDown className="w-4 h-4 text-white/30" />
            </div>
            <div className="flex flex-col md:flex-row gap-5">
              <VideoCard video={ingestData.video_a} label="A" />
              <VideoCard video={ingestData.video_b} label="B" />
            </div>
          </section>
        )}

        {/* RAG Chat Engine */}
        <section
          ref={chatRef}
          className="rounded-2xl border border-white/10 bg-white/[0.02] backdrop-blur-md overflow-hidden flex flex-col shadow-xl shadow-black/25 transition-all hover:border-white/15 animate-in fade-in duration-700"
          style={{ minHeight: "520px" }}
        >
          <div className="px-6 py-5 border-b border-white/10 flex items-center justify-between shrink-0 bg-white/[0.01]">
            <div>
              <h2 className="text-lg font-semibold text-white tracking-wide">RAG AI Assistant</h2>
              <p className="text-sm text-white/40 mt-1">
                Ask queries about the ingested transcripts and metadata — answer nodes stream in real-time.
              </p>
            </div>
            <div className="flex items-center gap-2 text-xs text-white/30 border border-white/10 rounded-full px-3.5 py-1.5 backdrop-blur-sm select-none">
              <div
                className={`w-2 h-2 rounded-full ${
                  ingestData ? "bg-emerald-400 animate-pulse shadow-glow shadow-emerald-400/50" : "bg-white/10"
                }`}
              />
              <span className="font-medium">{ingestData ? "Ready to Chat" : "Awaiting Sources"}</span>
            </div>
          </div>
          <div className="flex-1 flex flex-col min-h-0">
            <Chat sessionId={sessionId} disabled={!ingestData} />
          </div>
        </section>

        {/* Footer */}
        <footer className="text-center text-xs text-white/20 pb-6 flex flex-col items-center gap-1">
          <span>Creator Intelligence AI R&D Project</span>
          {sessionId && (
            <span className="font-mono text-[10px] text-white/10 select-none">
              SESSION: {sessionId.toUpperCase()}
            </span>
          )}
        </footer>
      </div>
    </div>
  );
}

