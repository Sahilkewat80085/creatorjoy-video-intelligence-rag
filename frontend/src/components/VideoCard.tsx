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

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toString();
}

function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}

function engagementColor(rate: number): string {
  if (rate >= 5) return "text-emerald-400 bg-emerald-400/10 border-emerald-400/30";
  if (rate >= 2) return "text-amber-400 bg-amber-400/10 border-amber-400/30";
  return "text-rose-400 bg-rose-400/10 border-rose-400/30";
}

export default function VideoCard({ video, label }: VideoCardProps) {
  const isYoutube = video.platform === "youtube";
  const engClass = engagementColor(video.engagement_rate);

  return (
    <div className="flex-1 min-w-0 rounded-2xl border border-white/10 bg-white/5 backdrop-blur-sm overflow-hidden">
      {/* Card Header */}
      <div className="px-6 py-4 border-b border-white/10 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div
            className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
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
          className={`flex items-center gap-1.5 text-xs px-2 py-1 rounded-full border ${
            isYoutube
              ? "bg-red-500/10 text-red-400 border-red-500/30"
              : "bg-pink-500/10 text-pink-400 border-pink-500/30"
          }`}
        >
          {isYoutube ? (
            <Clapperboard className="w-3 h-3" />
          ) : (
            <Film className="w-3 h-3" />
          )}
          <span className="capitalize">{video.platform}</span>
        </div>
      </div>

      {/* Creator Info */}
      <div className="px-6 py-4 border-b border-white/10">
        <h3 className="text-lg font-semibold text-white truncate">
          {video.creator_name || video.creator}
        </h3>
        {video.creator_name && (
          <p className="text-sm text-white/50 mt-0.5 truncate">@{video.creator}</p>
        )}
      </div>

      {/* Stats Grid */}
      <div className="px-6 py-4 grid grid-cols-2 gap-3">
        <div className="flex items-center gap-2 text-sm text-white/70">
          <Eye className="w-4 h-4 text-violet-400 shrink-0" />
          <span className="font-medium text-white">{formatNumber(video.views)}</span>
          <span className="text-white/40 text-xs">views</span>
        </div>
        <div className="flex items-center gap-2 text-sm text-white/70">
          <Heart className="w-4 h-4 text-rose-400 shrink-0" />
          <span className="font-medium text-white">{formatNumber(video.likes)}</span>
          <span className="text-white/40 text-xs">likes</span>
        </div>
        <div className="flex items-center gap-2 text-sm text-white/70">
          <MessageCircle className="w-4 h-4 text-cyan-400 shrink-0" />
          <span className="font-medium text-white">{formatNumber(video.comments)}</span>
          <span className="text-white/40 text-xs">comments</span>
        </div>
        <div className="flex items-center gap-2 text-sm text-white/70">
          <Clock className="w-4 h-4 text-amber-400 shrink-0" />
          <span className="font-medium text-white">{formatDuration(video.duration)}</span>
          <span className="text-white/40 text-xs">duration</span>
        </div>

        {/* Engagement rate — full width, highlighted */}
        <div
          className={`col-span-2 flex items-center justify-between rounded-xl border px-4 py-3 ${engClass}`}
        >
          <div className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4" />
            <span className="text-sm font-medium">Engagement Rate</span>
          </div>
          <span className="text-xl font-bold">{video.engagement_rate.toFixed(2)}%</span>
        </div>

        {/* Transcript Source */}
        <div className="col-span-2 flex items-center justify-between rounded-xl border border-white/10 bg-white/5 px-4 py-3">
          <div className="flex items-center gap-2 text-white/70">
            <span className="text-sm font-medium">Transcript Source</span>
          </div>
          <span className={`text-sm font-semibold capitalize ${
            video.transcript_source === 'native' ? 'text-emerald-400' :
            video.transcript_source === 'whisper' ? 'text-amber-400' :
            'text-rose-400'
          }`}>
            {video.transcript_source ? `${video.transcript_source} Transcript` : 'Transcript Unavailable'}
          </span>
        </div>
      </div>

      {/* Caption */}
      {video.caption && (
        <div className="px-6 pb-4">
          <p className="text-xs text-white/40 uppercase tracking-widest mb-1.5 font-medium">
            Caption
          </p>
          <p className="text-sm text-white/70 line-clamp-3">{video.caption}</p>
        </div>
      )}

      {/* Hashtags */}
      {video.hashtags && video.hashtags.length > 0 && (
        <div className="px-6 pb-5">
          <p className="text-xs text-white/40 uppercase tracking-widest mb-2 font-medium">
            Hashtags
          </p>
          <div className="flex flex-wrap gap-1.5">
            {video.hashtags.slice(0, 8).map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center gap-0.5 text-xs bg-white/5 border border-white/10 text-white/60 rounded-full px-2.5 py-0.5"
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
