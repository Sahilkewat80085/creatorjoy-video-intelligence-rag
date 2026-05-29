CreatorJoy — RAG Chatbot Architecture

Full-Stack AI system for side-by-side creator video intelligence.
Built for performance, cost-efficiency, and 1,000+ creators/day at scale.


Table of Contents

System Overview
High-Level Architecture Diagram
Component Breakdown

Frontend
Backend API
Ingestion Pipeline
Embedding & Vector Storage
LangGraph RAG Pipeline
Streaming Layer


Data Flow — Step by Step
LangGraph State Machine
Vector DB Schema
Prompt Architecture
Tech Stack Decisions & Trade-offs
Cost Analysis
Scalability Plan
Folder Structure
Environment Variables


1. System Overview
CreatorJoy's RAG chatbot lets creators drop in two video URLs (YouTube + Instagram Reel) and have a streaming, memory-aware conversation that answers:

"Why did Video A get more engagement than Video B?"
"Compare the hooks in the first 5 seconds."
"Suggest improvements for B based on what worked in A."

Every response is streamed, cites its source (video + chunk), and remembers prior turns.

2. High-Level Architecture Diagram
┌─────────────────────────────────────────────────────────┐
│                    NEXT.JS FRONTEND                      │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Video Card  │  │  Video Card  │  │  Chat Panel  │  │
│  │  (YouTube A) │  │  (Instagram  │  │  (Streaming) │  │
│  │             │  │      B)      │  │  + Citations │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└────────────────────────┬────────────────────────────────┘
                         │ REST + SSE
                         ▼
┌─────────────────────────────────────────────────────────┐
│                   FASTAPI BACKEND                        │
│                                                         │
│  POST /api/ingest          GET /api/chat (SSE stream)   │
│  POST /api/chat/clear      GET /api/videos/{session}    │
└──────────┬──────────────────────────┬───────────────────┘
           │                          │
           ▼                          ▼
┌──────────────────┐       ┌──────────────────────────────┐
│ INGESTION MODULE │       │     LANGGRAPH RAG PIPELINE    │
│                  │       │                              │
│ ┌──────────────┐ │       │  ┌────────────────────────┐ │
│ │YouTube       │ │       │  │   memory_node          │ │
│ │Extractor     │ │       │  │   (sliding window)     │ │
│ │- transcript  │ │       │  └────────────┬───────────┘ │
│ │- metadata    │ │       │               │             │
│ │- yt-dlp      │ │       │  ┌────────────▼───────────┐ │
│ └──────────────┘ │       │  │   retriever_node       │ │
│                  │       │  │   (Qdrant MMR search   │ │
│ ┌──────────────┐ │       │  │    filter by video_id) │ │
│ │Instagram     │ │       │  └────────────┬───────────┘ │
│ │Extractor     │ │       │               │             │
│ │- instaloader │ │       │  ┌────────────▼───────────┐ │
│ │- metadata    │ │       │  │   prompt_node          │ │
│ └──────────────┘ │       │  │   (inject chunks +     │ │
│                  │       │  │    citations + history) │ │
│ ┌──────────────┐ │       │  └────────────┬───────────┘ │
│ │Engagement    │ │       │               │             │
│ │Calculator    │ │       │  ┌────────────▼───────────┐ │
│ │(likes+comm.) │ │       │  │   generator_node       │ │
│ │/ views × 100 │ │       │  │   (Gemini Flash /      │ │
│ └──────────────┘ │       │  │    streaming tokens)   │ │
│                  │       │  └────────────┬───────────┘ │
│ ┌──────────────┐ │       └──────────────┼─────────────┘
│ │Chunker       │ │                      │
│ │512 tok/50    │ │                      │ SSE stream
│ │overlap       │ │                      ▼
│ └──────────────┘ │       ┌──────────────────────────────┐
│                  │       │       FRONTEND CHAT PANEL     │
│ ┌──────────────┐ │       │  token by token + citations  │
│ │Embedder      │ │       └──────────────────────────────┘
│ │BGE-small-en  │ │
│ │(local/free)  │ │
│ └──────┬───────┘ │
└────────┼─────────┘
         │
         ▼
┌──────────────────┐
│   QDRANT (local) │
│                  │
│  Collection:     │
│  video_chunks    │
│                  │
│  Payload:        │
│  - video_id: A/B │
│  - chunk_index   │
│  - timestamp     │
│  - source_url    │
│  - text          │
│  - metadata {}   │
└──────────────────┘

3. Component Breakdown
3.1 Frontend (Next.js / React)
Purpose: Side-by-side video cards + real-time streaming chat panel.
Key Components:
ComponentResponsibilityVideoCard.tsxDisplays embedded video (YouTube iframe / Instagram metadata), engagement rate, follower count, hashtagsChatPanel.tsxSends messages, renders streamed tokens, displays citations per messageCitationBadge.tsxPill UI showing [Video A · Chunk 3] per responseIngestForm.tsxURL input form, triggers /api/ingest, shows loading stateuseStream.tsCustom hook for SSE — consumes streaming response token by token
Streaming approach: EventSource API (SSE) — no WebSocket needed, simpler, works with FastAPI StreamingResponse.

3.2 Backend (FastAPI)
Endpoints:
POST /api/ingest
  Body: { youtube_url: str, instagram_url: str, session_id: str }
  → Runs full ingestion pipeline, stores in Qdrant
  → Returns: { video_a: metadata, video_b: metadata, status: "done" }

GET  /api/chat
  Params: ?message=...&session_id=...
  → SSE stream of tokens + citations
  → Each event: { token: str } or { citations: [...] } or { done: true }

POST /api/chat/clear
  Body: { session_id: str }
  → Clears memory for that session

GET  /api/videos/{session_id}
  → Returns cached metadata for both videos
Session management: UUID per browser session, stored in-memory (Redis in production).

3.3 Ingestion Pipeline
YouTube:
python# Transcript
from youtube_transcript_api import YouTubeTranscriptApi
transcript = YouTubeTranscriptApi.get_transcript(video_id)

# Metadata (views, likes, duration, upload date)
import yt_dlp
ydl.extract_info(url, download=False)
Instagram:
pythonimport instaloader
L = instaloader.Instaloader()
post = Post.from_shortcode(L.context, shortcode)
# → post.likes, post.comments, post.video_view_count
# → post.owner_profile.followers, post.caption, post.hashtags
Engagement Rate:
pythondef compute_engagement(likes: int, comments: int, views: int) -> float:
    if views == 0:
        return 0.0
    return round((likes + comments) / views * 100, 4)
Chunking:
pythonfrom langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,        # tokens — good balance for transcript text
    chunk_overlap=50,      # preserve sentence continuity across chunks
    length_function=len,
)

Why 512 / 50? Transcripts are conversational — short, punchy sentences. 512 captures enough context per chunk without diluting retrieval precision. Smaller chunks (256) lose context; larger (1024) hurt retrieval accuracy.


3.4 Embedding & Vector Storage
Embedder: BAAI/bge-small-en-v1.5 via sentence-transformers

Free, local, no API key
384-dimensional vectors
~130MB download, runs on CPU
Production swap: text-embedding-3-small (OpenAI) at $0.02/1M tokens

Vector DB: Qdrant (local mode for demo, Qdrant Cloud for prod)
Collection schema:
json{
  "id": "uuid",
  "vector": [384 floats],
  "payload": {
    "video_id": "A",
    "session_id": "abc-123",
    "chunk_index": 3,
    "text": "The hook starts with a bold claim...",
    "source_url": "https://youtube.com/...",
    "start_time": 4.2,
    "creator": "@username",
    "platform": "youtube",
    "engagement_rate": 8.34,
    "views": 120000,
    "likes": 9800,
    "comments": 210,
    "upload_date": "2024-11-15"
  }
}

Why Qdrant? Supports payload filtering natively — critical for filter by video_id. ChromaDB is easier to set up but slower at scale. Qdrant has a free local mode AND a managed cloud tier.


3.5 LangGraph RAG Pipeline
Graph definition:
pythonfrom langgraph.graph import StateGraph, END

class ChatState(TypedDict):
    question: str
    history: list[dict]
    retrieved_chunks: list[dict]
    citations: list[dict]
    answer: str

graph = StateGraph(ChatState)
graph.add_node("memory_node", load_memory)
graph.add_node("retriever_node", retrieve_chunks)
graph.add_node("prompt_node", build_prompt)
graph.add_node("generator_node", stream_response)

graph.set_entry_point("memory_node")
graph.add_edge("memory_node", "retriever_node")
graph.add_edge("retriever_node", "prompt_node")
graph.add_edge("prompt_node", "generator_node")
graph.add_edge("generator_node", END)
Memory node: Sliding window of last 6 turns (3 user + 3 assistant). Prevents context blowout.
Retriever node: MMR (Maximal Marginal Relevance) search — avoids returning 5 near-identical chunks. Fetches top 6 chunks (3 per video) with filter={"video_id": "A"} and filter={"video_id": "B"} separately to guarantee both videos are represented.
Generator node: Streams tokens from Gemini Flash / GPT-4o-mini with citation metadata injected.

3.6 Streaming Layer
FastAPI StreamingResponse (text/event-stream)
  → yields JSON events:
      data: {"type": "token", "content": "The "}
      data: {"type": "token", "content": "hook "}
      data: {"type": "citations", "content": [...]}
      data: {"type": "done"}

Frontend EventSource
  → appends tokens to message bubble in real-time
  → renders citations after stream closes

4. Data Flow — Step by Step
1. User pastes YouTube URL + Instagram URL → clicks "Analyze"

2. Frontend → POST /api/ingest { urls, session_id }

3. Backend:
   a. Parallel fetch: YouTube extractor + Instagram extractor
   b. Compute engagement rates for both
   c. Chunk transcripts (512/50)
   d. Embed all chunks (BGE-small, local)
   e. Upsert to Qdrant with video_id tags (A/B) + full metadata
   f. Return metadata to frontend → render video cards

4. User types: "Why did Video A get more engagement than B?"

5. Frontend → GET /api/chat?message=...&session_id=... (SSE)

6. LangGraph pipeline:
   a. memory_node: load last 6 turns from session store
   b. retriever_node: MMR search Qdrant, 3 chunks from A + 3 from B
   c. prompt_node: format system prompt with chunks + citations + history
   d. generator_node: stream tokens from LLM

7. SSE events flow back → frontend renders token by token

8. Stream closes → citations rendered as badges under the message

9. Turn saved to session memory → ready for next question

5. LangGraph State Machine
         ┌─────────────┐
  START → │ memory_node │  Load conversation history
         └──────┬──────┘
                │
         ┌──────▼──────┐
         │retriever_node│  Qdrant MMR search (Video A + B separately)
         └──────┬──────┘
                │
         ┌──────▼──────┐
         │ prompt_node │  Inject: chunks + citations + history + metadata
         └──────┬──────┘
                │
         ┌──────▼──────────┐
         │ generator_node  │  Stream LLM response token by token
         └──────┬──────────┘
                │
               END  →  Save turn to memory

6. Vector DB Schema
Collection: video_chunks
Distance metric: Cosine
Vector size: 384 (BGE-small) or 1536 (OpenAI)
Indexes for filtering:

session_id — isolate per-user data
video_id — filter A vs B in retrieval
platform — youtube / instagram


7. Prompt Architecture
SYSTEM:
You are a creator intelligence assistant. You analyze video transcripts
and metadata to give data-driven insights to content creators.

Always:
- Cite your sources as [Video A · Chunk N] or [Video B · Chunk N]
- Use engagement rates and metadata when answering comparison questions
- Be specific — quote exact transcript moments when relevant
- Keep answers concise and actionable

Video A ({platform}): {title}
- Creator: {creator}, Followers: {followers}
- Views: {views}, Likes: {likes}, Comments: {comments}
- Engagement Rate: {engagement_rate}%
- Upload Date: {upload_date}

Video B ({platform}): {title}
- Creator: {creator}, Followers: {followers}
- Views: {views}, Likes: {likes}, Comments: {comments}
- Engagement Rate: {engagement_rate}%
- Upload Date: {upload_date}

RETRIEVED CONTEXT:
[Video A · Chunk 1] (timestamp: 0:00–0:08)
"{chunk_text}"

[Video B · Chunk 2] (timestamp: 0:03–0:12)
"{chunk_text}"

... (up to 6 chunks total)

CONVERSATION HISTORY:
{last_6_turns}

USER: {question}
ASSISTANT:

8. Tech Stack Decisions & Trade-offs
DecisionChoiceWhyAlternative & When to SwitchLLMGemini 1.5 FlashFree tier, fast, 1M contextGPT-4o-mini at scale (cheaper per token than GPT-4o, more reliable)EmbeddingsBGE-small-en-v1.5Free, local, no API dependencytext-embedding-3-small in prod ($0.02/1M tokens, higher quality)Vector DBQdrant localPayload filtering, fast, free local modeQdrant Cloud at 1,000+ creators/dayOrchestrationLangGraphExplicit state machine, easier to debug than LangChain chainsLangChain LCEL for simpler use casesChunk size512 / 50 overlapGood for short conversational transcript sentences1024 for long-form documentary-style contentMemorySliding window (6 turns)Bounded token usage, no context blowoutFull history for short sessions, summarization for long onesRetrievalMMR (not pure similarity)Avoids redundant chunks, ensures diversityPure cosine similarity if speed is criticalStreamingSSE (not WebSocket)Simpler, stateless, works with FastAPI nativelyWebSocket only if bidirectional real-time neededInstagraminstaloaderFree, open sourceRapidAPI scraper if instaloader gets rate-limited

9. Cost Analysis
Demo (Local)
ItemCostEmbeddings (BGE-small, local)$0LLM (Gemini Flash free tier)$0Qdrant (local mode)$0Transcripts (youtube-transcript-api)$0Total$0
Production — 1,000 Creators/Day
Assumptions: avg 2 videos/creator, avg 10 chat turns/session, avg 500 tokens/turn.
ItemUsageCost/DayEmbeddings (text-embedding-3-small)2,000 videos × ~5,000 tokens~$0.20LLM input (GPT-4o-mini)10,000 turns × 2,000 tokens~$3.00LLM output (GPT-4o-mini)10,000 turns × 500 tokens~$1.50Qdrant Cloud2M vectors~$25/month = ~$0.83/dayTotal~$5.50/day

At 1,000 creators/day: $0.0055 per creator. Extremely low CAC.

Further cost levers:

Cache embeddings per video URL — if the same video is analyzed twice, skip re-embedding
Use Groq (Llama 3.1 70B) instead of GPT-4o-mini — free up to 500K tokens/day
Async batch embedding for ingestion (not real-time) — use OpenAI batch API at 50% discount


10. Scalability Plan
Current (Demo): Single Machine
1 FastAPI process → in-memory sessions → local Qdrant → local BGE model
1,000 Creators/Day
Load Balancer (Nginx)
  ↓
FastAPI (2–3 workers, Uvicorn + Gunicorn)
  ↓
Redis (session/memory store — replaces in-memory dict)
  ↓
Qdrant Cloud (managed, horizontally scalable)
  ↓
OpenAI API (embeddings + LLM — no infra to manage)
Ingestion at scale: Move to async job queue:
POST /ingest → push job to Redis Queue (RQ / Celery)
  → Worker picks up → runs extraction + embedding + upsert
  → Webhook/polling to notify frontend when ready
What breaks at 10,000 users?

In-memory session store → replace with Redis
Local Qdrant → replace with Qdrant Cloud or Weaviate
Single FastAPI process → horizontal scaling behind load balancer
BGE local model → becomes bottleneck; move to hosted embeddings API
Synchronous ingestion → async job queue mandatory


11. Folder Structure
creatorjoy/
├── frontend/                  # Next.js app
│   ├── components/
│   │   ├── VideoCard.tsx
│   │   ├── ChatPanel.tsx
│   │   ├── CitationBadge.tsx
│   │   └── IngestForm.tsx
│   ├── hooks/
│   │   └── useStream.ts
│   ├── pages/
│   │   ├── index.tsx
│   │   └── api/              # Next.js API routes (optional proxy)
│   └── styles/
│
├── backend/                   # FastAPI app
│   ├── main.py                # App entrypoint, CORS, routes
│   ├── routers/
│   │   ├── ingest.py          # POST /api/ingest
│   │   └── chat.py            # GET /api/chat (SSE)
│   ├── services/
│   │   ├── youtube_extractor.py
│   │   ├── instagram_extractor.py
│   │   ├── engagement.py
│   │   ├── chunker.py
│   │   ├── embedder.py
│   │   └── qdrant_store.py
│   ├── rag/
│   │   ├── graph.py           # LangGraph state machine
│   │   ├── nodes/
│   │   │   ├── memory_node.py
│   │   │   ├── retriever_node.py
│   │   │   ├── prompt_node.py
│   │   │   └── generator_node.py
│   │   └── prompts.py
│   ├── models/
│   │   └── schemas.py         # Pydantic models
│   └── config.py              # Settings, env vars
│
├── docs/
│   └── ARCHITECTURE.md        # This file
│
├── .env.example
├── README.md
└── docker-compose.yml         # Qdrant + backend + frontend

12. Environment Variables
bash# .env.example

# LLM
GOOGLE_API_KEY=                # Gemini Flash
OPENAI_API_KEY=                # Optional: GPT-4o-mini fallback

# Vector DB
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=                # Only for Qdrant Cloud

# Instagram (if using RapidAPI fallback)
RAPIDAPI_KEY=

# App
SESSION_SECRET=
CORS_ORIGINS=http://localhost:3000

# Embeddings (local by default, no key needed for BGE)
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
# EMBEDDING_MODEL=text-embedding-3-small  # OpenAI prod swap

Summary
This architecture is:

$0 to demo — fully free stack, no credit card required
$5.50/day at 1,000 creators — lowest cost per creator in class
Production-ready path — Redis, Qdrant Cloud, async queues are drop-in swaps
LangGraph explicit state — debuggable, testable, each node is isolated
Citation-native — metadata flows from chunk storage through retrieval into every LLM prompt
Streaming-first — SSE from FastAPI, token-by-token in the frontend