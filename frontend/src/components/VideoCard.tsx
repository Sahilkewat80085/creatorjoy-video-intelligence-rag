import { VideoData } from "@/types";
import {
  Eye,
  Heart,
  MessageCircle,
  TrendingUp,
  Clock,
  Clapperboard,
  Film,
  Hash,
} from "lucide-react";

interface VideoCardProps {
  video: VideoData;
  label: "A" | "B";
}

function formatNumber(n: number | undefined | null): string {
  if (n === undefined || n === null) return "0";
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toString();
}

function formatDuration(seconds: number | undefined | null): string {
  if (seconds === undefined || seconds === null || seconds < 0) return "0:00";
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}

function engagementColor(rate: number | undefined | null): string {
  const r = rate ?? 0;
  if (r >= 5) return "text-emerald-400 bg-emerald-400/10 border-emerald-400/20 shadow-emerald-950/20";
  if (r >= 2) return "text-amber-400 bg-amber-400/10 border-amber-400/20 shadow-amber-950/20";
  return "text-rose-400 bg-rose-400/10 border-rose-400/20 shadow-rose-950/20";
}

export default function VideoCard({ video, label }: VideoCardProps) {
  if (!video) return null;
  const isYoutube = video.platform === "youtube";
  const engagementRate = video.engagement_rate ?? 0;
  const engClass = engagementColor(engagementRate);

  return (
    <div className="flex-1 min-w-0 rounded-2xl border border-white/10 bg-white/5 backdrop-blur-sm overflow-hidden transition-all duration-300 hover:border-white/20 hover:shadow-lg hover:shadow-black/20 group animate-in fade-in duration-500 slide-in-from-bottom-2">
      {/* Card Header */}
      <div className="px-6 py-4 border-b border-white/10 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div
            className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-transform group-hover:scale-105 ${
              label === "A"
                ? "bg-violet-500/20 text-violet-300 border border-violet-500/30"
                : "bg-cyan-500/20 text-cyan-300 border border-cyan-500/30"
            }`}
          >
            {label}
          </div>
          <span className="text-sm font-medium text-white/60">Video {label}</span>
        </div>
        <div
          className={`flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full border transition-all ${
            isYoutube
              ? "bg-red-500/10 text-red-400 border-red-500/20 hover:bg-red-500/20"
              : "bg-pink-500/10 text-pink-400 border-pink-500/20 hover:bg-pink-500/20"
          }`}
        >
          {isYoutube ? (
            <Clapperboard className="w-3.5 h-3.5" />
          ) : (
            <Film className="w-3.5 h-3.5" />
          )}
          <span className="capitalize font-medium">{video.platform || "Video"}</span>
        </div>
      </div>

      {/* Creator Info */}
      <div className="px-6 py-4 border-b border-white/10">
        <h3 className="text-lg font-semibold text-white truncate transition-colors group-hover:text-violet-200">
          {video.creator_name || video.creator || "Anonymous Creator"}
        </h3>
        {(video.creator_name || video.creator) && (
          <p className="text-sm text-white/50 mt-0.5 truncate">
            @{video.creator || (video.creator_name ? video.creator_name.toLowerCase().replace(/\s+/g, '') : "anonymous")}
          </p>
        )}
      </div>

      {/* Stats Grid */}
      <div className="px-6 py-4 grid grid-cols-2 gap-4">
        <div className="flex items-center gap-2 text-sm text-white/70">
          <Eye className="w-4 h-4 text-violet-400 shrink-0" />
          <span className="font-semibold text-white">{formatNumber(video.views)}</span>
          <span className="text-white/40 text-[11px] uppercase tracking-wider">views</span>
        </div>
        <div className="flex items-center gap-2 text-sm text-white/70">
          <Heart className="w-4 h-4 text-rose-400 shrink-0" />
          <span className="font-semibold text-white">{formatNumber(video.likes)}</span>
          <span className="text-white/40 text-[11px] uppercase tracking-wider">likes</span>
        </div>
        <div className="flex items-center gap-2 text-sm text-white/70">
          <MessageCircle className="w-4 h-4 text-cyan-400 shrink-0" />
          <span className="font-semibold text-white">{formatNumber(video.comments)}</span>
          <span className="text-white/40 text-[11px] uppercase tracking-wider">comments</span>
        </div>
        <div className="flex items-center gap-2 text-sm text-white/70">
          <Clock className="w-4 h-4 text-amber-400 shrink-0" />
          <span className="font-semibold text-white">{formatDuration(video.duration)}</span>
          <span className="text-white/40 text-[11px] uppercase tracking-wider">duration</span>
        </div>

        {/* Engagement rate — full width, highlighted */}
        <div
          className={`col-span-2 flex items-center justify-between rounded-xl border px-4 py-3 shadow-inner transition-transform group-hover:scale-[1.01] ${engClass}`}
        >
          <div className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4 animate-pulse" />
            <span className="text-sm font-medium">Engagement Rate</span>
          </div>
          <span className="text-xl font-bold">{engagementRate.toFixed(2)}%</span>
        </div>

        {/* Transcript Source */}
        <div className="col-span-2 flex items-center justify-between rounded-xl border border-white/10 bg-white/5 px-4 py-3">
          <div className="flex items-center gap-2 text-white/70">
            <span className="text-sm font-medium">Transcript Source</span>
          </div>
          <span className={`text-xs font-semibold uppercase tracking-wider px-2 py-0.5 rounded-md ${
            video.transcript_source === 'native' ? 'text-emerald-400 bg-emerald-400/5 border border-emerald-500/20' :
            video.transcript_source === 'whisper' ? 'text-amber-400 bg-amber-400/5 border border-amber-500/20' :
            'text-rose-400 bg-rose-400/5 border border-rose-500/20'
          }`}>
            {video.transcript_source ? `${video.transcript_source}` : 'Unavailable'}
          </span>
        </div>
      </div>

      {/* Caption */}
      {video.caption && (
        <div className="px-6 pb-4">
          <p className="text-[10px] text-white/40 uppercase tracking-widest mb-1.5 font-medium">
            Caption
          </p>
          <p className="text-sm text-white/70 leading-relaxed line-clamp-3 group-hover:line-clamp-none transition-all duration-300">
            {video.caption}
          </p>
        </div>
      )}

      {/* Hashtags */}
      {video.hashtags && video.hashtags.length > 0 && (
        <div className="px-6 pb-5">
          <p className="text-[10px] text-white/40 uppercase tracking-widest mb-2 font-medium">
            Hashtags
          </p>
          <div className="flex flex-wrap gap-1.5">
            {video.hashtags.slice(0, 8).map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center gap-0.5 text-xs bg-white/5 border border-white/10 text-white/60 rounded-full px-2.5 py-0.5 hover:bg-white/10 hover:text-white/80 transition-all select-none"
              >
                <Hash className="w-2.5 h-2.5" />
                {tag.replace(/^#/, "")}
              </span>
            ))}
            {video.hashtags.length > 8 && (
              <span className="text-xs text-white/30 px-1 py-0.5">
                +{video.hashtags.length - 8} more
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
