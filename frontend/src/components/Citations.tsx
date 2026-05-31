import { Citation } from "@/types";
import { FileText, Database } from "lucide-react";

interface CitationsProps {
  citations: Citation[];
}

export default function Citations({ citations }: CitationsProps) {
  if (!citations || citations.length === 0) return null;

  return (
    <div className="mt-2 flex flex-wrap gap-1.5">
      {citations.map((c, i) => (
        <span
          key={i}
          className="inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full border border-white/10 bg-white/5 text-white/50"
        >
          {c.source === "transcript" ? (
            <FileText className="w-3 h-3 text-violet-400" />
          ) : (
            <Database className="w-3 h-3 text-cyan-400" />
          )}
          {c.source === "transcript"
            ? `Transcript: ${c.video_id ?? ""} · Chunk ${c.chunk_index ?? 0}`
            : `Metadata: Video ${c.video ?? ""}`}
        </span>
      ))}
    </div>
  );
}
