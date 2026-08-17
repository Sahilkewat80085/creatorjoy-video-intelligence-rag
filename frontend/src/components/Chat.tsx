"use client";

import { useEffect, useRef, useState } from "react";
import { Message } from "@/types";
import { chatStream } from "@/lib/api";
import Citations from "./Citations";
import { Send, Bot, User, Loader2, Sparkles } from "lucide-react";

interface ChatProps {
  sessionId: string;
  disabled: boolean;
}

function TypingDots() {
  return (
    <span className="inline-flex items-center gap-1.5 px-1.5 py-0.5">
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          className="w-2 h-2 rounded-full bg-violet-400 animate-bounce"
          style={{ animationDelay: `${i * 0.15}s` }}
        />
      ))}
    </span>
  );
}

export default function Chat({ sessionId, disabled }: ChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Handle auto-resizing of the input textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    textarea.style.height = "auto";
    textarea.style.height = `${Math.min(textarea.scrollHeight, 144)}px`;
  }, [input]);

  async function handleSend() {
    const question = input.trim();
    if (!question || isStreaming || disabled) return;

    setError(null);
    setInput("");

    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: question,
    };

    const assistantId = crypto.randomUUID();
    const assistantMsg: Message = {
      id: assistantId,
      role: "assistant",
      content: "",
      citations: [],
      isStreaming: true,
    };

    setMessages((prev) => [...prev, userMsg, assistantMsg]);
    setIsStreaming(true);

    try {
      let accumulated = "";
      for await (const chunk of chatStream(sessionId, question)) {
        if (chunk.type === "token" && chunk.content) {
          accumulated += chunk.content;
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId ? { ...m, content: accumulated } : m
            )
          );
        } else if (chunk.type === "citations" && chunk.citations) {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId ? { ...m, citations: chunk.citations } : m
            )
          );
        }
      }

      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId ? { ...m, isStreaming: false } : m
        )
      );
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Streaming connection lost.";
      setError(msg);
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? { ...m, content: "Sorry, I encountered an issue processing that query.", isStreaming: false }
            : m
        )
      );
    } finally {
      setIsStreaming(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="flex flex-col h-full min-h-0 bg-transparent">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6 scrollbar-thin scrollbar-thumb-white/10">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center py-16 animate-in fade-in duration-500">
            <div className="w-16 h-16 rounded-2xl bg-violet-500/10 border border-violet-500/20 flex items-center justify-center mb-4 shadow-inner">
              <Bot className="w-8 h-8 text-violet-400 animate-pulse" />
            </div>
            <h3 className="text-white/70 font-semibold mb-2 flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-violet-300" />
              Ask anything about the videos
            </h3>
            <p className="text-sm text-white/40 max-w-sm leading-relaxed">
              Compare statistics, request transcripts summaries, or check engagement metrics.
            </p>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-3 animate-in fade-in slide-in-from-bottom-2 duration-300 ${msg.role === "user" ? "flex-row-reverse" : "flex-row"}`}
          >
            {/* Avatar */}
            <div
              className={`w-8 h-8 shrink-0 rounded-full flex items-center justify-center border shadow-sm transition-transform hover:scale-105 ${
                msg.role === "user"
                  ? "bg-violet-500/20 border-violet-500/30 text-violet-300"
                  : "bg-cyan-500/20 border-cyan-500/30 text-cyan-300"
              }`}
            >
              {msg.role === "user" ? (
                <User className="w-4 h-4" />
              ) : (
                <Bot className="w-4 h-4" />
              )}
            </div>

            {/* Bubble */}
            <div className={`flex flex-col max-w-[75%] ${msg.role === "user" ? "items-end" : "items-start"}`}>
              <div
                className={`rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap transition-all shadow-sm ${
                  msg.role === "user"
                    ? "bg-violet-600/25 border border-violet-500/20 text-white rounded-tr-sm"
                    : "bg-white/5 border border-white/10 text-white/90 rounded-tl-sm"
                }`}
              >
                {msg.content || (msg.isStreaming ? <TypingDots /> : "")}
                {msg.isStreaming && msg.content && (
                  <span className="ml-1 inline-block w-1.5 h-4 bg-violet-400 animate-pulse align-middle" />
                )}
              </div>
              {msg.citations && msg.citations.length > 0 && (
                <Citations citations={msg.citations} />
              )}
            </div>
          </div>
        ))}

        <div ref={bottomRef} />
      </div>

      {/* Error Banner */}
      {error && (
        <div className="mx-4 mb-3 px-4 py-3 rounded-xl bg-rose-500/10 border border-rose-500/25 text-rose-400 text-sm animate-in fade-in slide-in-from-bottom-1 duration-200">
          {error}
        </div>
      )}

      {/* Disabled notice */}
      {disabled && (
        <div className="mx-4 mb-3 px-4 py-3 rounded-xl bg-amber-500/10 border border-amber-500/25 text-amber-400 text-sm text-center font-medium animate-in fade-in duration-300">
          Ingest and analyze videos above to start the conversation.
        </div>
      )}

      {/* Input Row */}
      <div className="px-4 pb-4">
        <div className="flex items-end gap-3 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 focus-within:border-violet-500/40 focus-within:bg-white/8 transition-all duration-200 shadow-inner">
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isStreaming || disabled}
            placeholder={
              disabled ? "Analyze video urls to unlock chat..." : "Ask a query about the video transcripts..."
            }
            className="flex-1 resize-none bg-transparent text-white/90 placeholder:text-white/20 text-sm focus:outline-none disabled:opacity-40 max-h-36 overflow-y-auto py-1"
          />
          <button
            onClick={handleSend}
            disabled={isStreaming || disabled || !input.trim()}
            className="shrink-0 w-9 h-9 rounded-xl flex items-center justify-center bg-violet-600 hover:bg-violet-500 active:scale-95 disabled:opacity-30 disabled:cursor-not-allowed disabled:active:scale-100 transition-all shadow-md"
          >
            {isStreaming ? (
              <Loader2 className="w-4 h-4 text-white animate-spin" />
            ) : (
              <Send className="w-4 h-4 text-white" />
            )}
          </button>
        </div>
        <p className="text-[10px] text-white/20 mt-2 text-center select-none">
          Press Enter to send · Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}

