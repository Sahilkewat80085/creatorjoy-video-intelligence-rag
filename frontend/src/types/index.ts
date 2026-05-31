export interface VideoData {
  platform: "youtube" | "instagram";
  video_id: string;
  source_url: string;
  creator: string;
  creator_name: string | null;
  views: number;
  likes: number;
  comments: number;
  engagement_rate: number;
  hashtags: string[];
  caption: string | null;
  transcript: string;
  duration: number;
}

export interface IngestResponse {
  status: "success" | "error";
  video_a: VideoData;
  video_b: VideoData;
}

export interface Citation {
  source: "transcript" | "metadata";
  video_id?: string;
  chunk_index?: number;
  video?: string;
}

export interface ChatResponse {
  answer: string;
  citations: Citation[];
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  isStreaming?: boolean;
}
