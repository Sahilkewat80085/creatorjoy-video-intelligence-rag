<div align="center">
  
# CreatorJoy Video Intelligence RAG

*An intelligent, full-stack Retrieval-Augmented Generation (RAG) platform that turns YouTube and Instagram videos into interactive, chat-able knowledge bases.*

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-black?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org/)
[![Qdrant](https://img.shields.io/badge/Qdrant-f90b47?style=for-the-badge&logo=qdrant&logoColor=white)](https://qdrant.tech/)
[![Gemini](https://img.shields.io/badge/Google_Gemini-8E75B2?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=for-the-badge)](https://langchain-ai.github.io/langgraph/)

</div>

---

## Introduction 

This repository contains a deeply engineered, production-ready RAG application designed to handle edge cases gracefully. 

When architecting this solution, the core focus was resiliency and accuracy. Internet-hosted video content is often unstandardized; transcripts are frequently missing, APIs experience downtime, and LLMs are prone to hallucination. This platform solves these real-world problems to provide a seamless user experience.

### Technical Highlights
1. **The Whisper Fallback System:** If a video lacks a native transcript (e.g., Instagram Reels or undocumented YouTube videos), the ingestion pipeline automatically downloads the media using `yt-dlp`, extracts the audio, and transcribes it locally using `faster-whisper`.
2. **Strict Citation Engine:** The system actively evaluates whether its generated answers were derived from Metadata (views, likes, comments) or the Transcript, returning exact references to the frontend for transparent sourcing.
3. **Robust Defensive Engineering:** The backend (`FastAPI`) is hardened against unexpected LLM behavior. If the `gemini-2.5-flash` model encounters a safety filter or generates an empty response due to a lack of context, the backend safely catches the `ValueError` and streams a graceful fallback message instead of crashing with a 502 Gateway Error.
4. **LangGraph Memory Persistence:** The chat agent utilizes conversation history injected directly into the LangGraph state. This allows the system to resolve pronouns and context across multiple turns of dialogue (e.g., asking "Who is the creator of Video A?" followed by "How many views does he have?").

---

## System Architecture

This project is decoupled into an independent Frontend and Backend.

### The Backend (Python / FastAPI)
Deployed on **Railway** (`https://creatorjoy-video-intelligence-rag-production.up.railway.app`).
* **Ingestion Pipeline:** Utilizes the `Apify SDK` for deep metadata scraping, falling back to `yt-dlp` and `faster-whisper` for missing transcripts.
* **Vector Database:** `Qdrant` is used to chunk, embed, and store the transcript and metadata payloads.
* **LLM Orchestration:** Built with `LangGraph` for stateful multi-step agent routing, and `google-generativeai` (`gemini-2.5-flash`) for the generative pipeline.
* **Streaming API:** Implements Server-Sent Events (SSE) via `StreamingResponse` to stream tokens directly to the UI in real-time.

### The Frontend (Next.js / React)
Deployed on **Vercel**.
* **Framework:** Next.js with React and TypeScript.
* **Design:** Clean, responsive UI tailored for high user engagement.
* **Dynamic Routing:** Communicates seamlessly with the production Railway backend using `NEXT_PUBLIC_API_URL` environment variables, bypassing Next.js API route timeout limits.

---

## Getting Started Locally

To run this application locally, follow the instructions below.

### Prerequisites
- Python 3.10+
- Node.js 18+
- API Keys for: **Gemini**, **Apify**, and a **Qdrant** instance (local or cloud).

### 1. Start the Backend
```bash
cd Backend
python -m venv venv
source venv/bin/activate  # Or `.\venv\Scripts\Activate` on Windows
pip install -r requirements.txt

# Create a .env file and add your keys:
# GEMINI_API_KEY=...
# APIFY_API_TOKEN=...
# QDRANT_URL=...
# QDRANT_API_KEY=...

# Run the server
uvicorn main:app --reload --port 8080
```

### 2. Start the Frontend
```bash
cd frontend
npm install

# Create a .env.local file:
# NEXT_PUBLIC_API_URL=http://localhost:8080

npm run dev
```

Visit `http://localhost:3000` to interact with the application.

---

## Evaluation Scenarios

To effectively evaluate the system, consider the following test cases:
1. **The Pronoun Test:** Ingest a video. Ask for the creator's name. Follow up with "What is the primary topic they discuss in the video?". Observe the LangGraph memory resolving the context.
2. **The Missing Transcript Test:** Ingest an Instagram Reel or a YouTube Short without captions. Monitor the backend terminal to see the Whisper fallback pipeline execute to generate the transcript locally.
3. **The Out-of-Scope Test:** Ask an unrelated factual question (e.g., "Who is the president of the United States?"). The prompt engineering will force the model to respond that it cannot determine the answer from the available video data, mitigating hallucination.

---

<div align="center">
  <i>Built for the CreatorJoy Video Intelligence evaluation.</i>
</div>
