import { Citation } from "@/types";
import { FileText, Database } from "lucide-react";

interface CitationsProps {
  citations: Citation[];
}

export default function Citations({ citations }: CitationsProps) {
  if (!citations || citations.length === 0) return null;

  return (
    <div className="mt-2 flex flex-wrap gap-2 animate-in fade-in duration-300 slide-in-from-bottom-1">
      {citations.map((c, i) => {
        const isTranscript = c.source === "transcript";
        const videoId = c.video_id ?? c.video ?? "Unknown";
        const chunkIndex = c.chunk_index ?? 0;
        
        return (
          <span
            key={i}
            className="inline-flex items-center gap-1.5 text-[11px] px-3 py-1 rounded-full border border-white/10 bg-white/5 text-white/50 transition-all duration-200 hover:scale-[1.03] hover:bg-white/10 hover:text-white/80 hover:border-white/20 cursor-default select-none shadow-sm"
            title={isTranscript ? `Video ID: ${videoId} | Segment Chunk: ${chunkIndex}` : `Video metadata entry reference: ${videoId}`}
          >
            {isTranscript ? (
              <FileText className="w-3.5 h-3.5 text-violet-400 transition-colors" />
            ) : (
              <Database className="w-3.5 h-3.5 text-cyan-400 transition-colors" />
            )}
            <span>
              {isTranscript
                ? `Transcript: ${videoId.slice(0, 10)}... · Chunk ${chunkIndex}`
                : `Metadata: Video ${videoId}`}
            </span>
          </span>
        );
      })}
    </div>
  );
}

