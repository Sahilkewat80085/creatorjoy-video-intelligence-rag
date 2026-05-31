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

  // Generate session ID on the client to avoid hydration mismatch
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
    <div className="min-h-screen bg-[#0a0a0f] text-white">
      {/* Ambient background blobs */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute -top-64 -left-64 w-[600px] h-[600px] rounded-full bg-violet-900/20 blur-3xl" />
        <div className="absolute top-1/2 -right-64 w-[500px] h-[500px] rounded-full bg-cyan-900/15 blur-3xl" />
        <div className="absolute -bottom-32 left-1/3 w-[400px] h-[400px] rounded-full bg-indigo-900/20 blur-3xl" />
      </div>

      <div className="relative z-10 max-w-6xl mx-auto px-4 py-8 flex flex-col gap-8">
        {/* ── HEADER ── */}
        <header className="text-center py-6">
          <div className="inline-flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-2xl bg-violet-600/20 border border-violet-500/30 flex items-center justify-center">
              <Brain className="w-5 h-5 text-violet-400" />
            </div>
            <span className="text-xs font-semibold uppercase tracking-[0.2em] text-violet-400 border border-violet-500/30 px-3 py-1 rounded-full bg-violet-500/10">
              RAG-Powered Analysis
            </span>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-br from-white via-white/90 to-white/50 bg-clip-text text-transparent mb-3 tracking-tight">
            Creator Intelligence AI
          </h1>
          <p className="text-white/50 text-base md:text-lg max-w-xl mx-auto">
            Compare creator content across platforms using retrieval-augmented generation
          </p>
        </header>

        {/* ── INGEST SECTION ── */}
        <section className="rounded-2xl border border-white/10 bg-white/[0.03] backdrop-blur-sm p-6">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h2 className="text-lg font-semibold text-white">Video Sources</h2>
              <p className="text-sm text-white/40 mt-0.5">
                Provide two video URLs (YouTube or Instagram Reel) to begin
              </p>
            </div>
            {ingestData && (
              <button
                onClick={handleReset}
                className="flex items-center gap-1.5 text-xs text-white/40 hover:text-white/70 transition-colors border border-white/10 hover:border-white/20 rounded-lg px-3 py-1.5"
              >
                <RotateCcw className="w-3 h-3" />
                Reset
              </button>
            )}
          </div>
          <IngestForm onSuccess={handleIngestSuccess} />
        </section>

        {/* ── VIDEO COMPARISON ── */}
        {ingestData && (
          <section>
            <div className="flex items-center gap-3 mb-4">
              <h2 className="text-lg font-semibold text-white">Video Comparison</h2>
              <div className="h-px flex-1 bg-white/10" />
              <ChevronDown className="w-4 h-4 text-white/30" />
            </div>
            <div className="flex flex-col md:flex-row gap-4">
              <VideoCard video={ingestData.video_a} label="A" />
              <VideoCard video={ingestData.video_b} label="B" />
            </div>
          </section>
        )}

        {/* ── CHAT ── */}
        <section
          ref={chatRef}
          className="rounded-2xl border border-white/10 bg-white/[0.03] backdrop-blur-sm overflow-hidden flex flex-col"
          style={{ minHeight: "520px" }}
        >
          <div className="px-6 py-4 border-b border-white/10 flex items-center justify-between shrink-0">
            <div>
              <h2 className="text-lg font-semibold text-white">AI Chat</h2>
              <p className="text-sm text-white/40 mt-0.5">
                Ask questions about the ingested videos — answers stream in real-time
              </p>
            </div>
            <div className="flex items-center gap-2 text-xs text-white/30 border border-white/10 rounded-full px-3 py-1">
              <div
                className={`w-1.5 h-1.5 rounded-full ${
                  ingestData ? "bg-emerald-400 animate-pulse" : "bg-white/20"
                }`}
              />
              {ingestData ? "Ready" : "Awaiting ingestion"}
            </div>
          </div>
          <div className="flex-1 flex flex-col min-h-0">
            <Chat sessionId={sessionId} disabled={!ingestData} />
          </div>
        </section>

        {/* Footer */}
        <footer className="text-center text-xs text-white/20 pb-4">
          Session ID:{" "}
          <span className="font-mono">{sessionId.slice(0, 8)}…</span>
        </footer>
      </div>
    </div>
  );
}
