"use client";

import { useEffect, useRef, useState } from "react";
import { Message } from "@/types";
import { chatStream } from "@/lib/api";
import Citations from "./Citations";
import { Send, Bot, User, Loader2 } from "lucide-react";

interface ChatProps {
  sessionId: string;
  disabled: boolean;
}

function TypingDots() {
  return (
    <span className="inline-flex items-center gap-1 px-1">
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          className="w-1.5 h-1.5 rounded-full bg-violet-400 animate-bounce"
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
      const msg = err instanceof Error ? err.message : "Streaming failed";
      setError(msg);
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? { ...m, content: "Sorry, something went wrong.", isStreaming: false }
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
    <div className="flex flex-col h-full min-h-0">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6 scrollbar-thin scrollbar-thumb-white/10">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center py-16">
            <div className="w-16 h-16 rounded-2xl bg-violet-500/10 border border-violet-500/20 flex items-center justify-center mb-4">
              <Bot className="w-8 h-8 text-violet-400" />
            </div>
            <h3 className="text-white/70 font-medium mb-2">
              Ask anything about the videos
            </h3>
            <p className="text-sm text-white/40 max-w-sm">
              Try: &ldquo;Who is the creator of Video B?&rdquo; or &ldquo;Which video has better engagement?&rdquo;
            </p>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-3 ${msg.role === "user" ? "flex-row-reverse" : "flex-row"}`}
          >
            {/* Avatar */}
            <div
              className={`w-8 h-8 shrink-0 rounded-full flex items-center justify-center border ${
                msg.role === "user"
                  ? "bg-violet-500/20 border-violet-500/30"
                  : "bg-cyan-500/20 border-cyan-500/30"
              }`}
            >
              {msg.role === "user" ? (
                <User className="w-4 h-4 text-violet-300" />
              ) : (
                <Bot className="w-4 h-4 text-cyan-300" />
              )}
            </div>

            {/* Bubble */}
            <div className={`flex flex-col max-w-[75%] ${msg.role === "user" ? "items-end" : "items-start"}`}>
              <div
                className={`rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
                  msg.role === "user"
                    ? "bg-violet-600/30 border border-violet-500/30 text-white rounded-tr-sm"
                    : "bg-white/5 border border-white/10 text-white/90 rounded-tl-sm"
                }`}
              >
                {msg.content || (msg.isStreaming ? <TypingDots /> : "")}
                {msg.isStreaming && msg.content && (
                  <span className="ml-1 inline-block w-0.5 h-4 bg-violet-400 animate-pulse align-middle" />
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
        <div className="mx-4 mb-2 px-4 py-2.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-sm">
          {error}
        </div>
      )}

      {/* Disabled notice */}
      {disabled && (
        <div className="mx-4 mb-2 px-4 py-2.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400 text-sm text-center">
          Ingest videos above to start chatting
        </div>
      )}

      {/* Input Row */}
      <div className="px-4 pb-4">
        <div className="flex items-end gap-3 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 focus-within:border-violet-500/50 transition-colors">
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isStreaming || disabled}
            placeholder={
              disabled ? "Ingest videos first…" : "Ask about the videos…"
            }
            className="flex-1 resize-none bg-transparent text-white/90 placeholder:text-white/30 text-sm focus:outline-none disabled:opacity-40 max-h-36 overflow-y-auto"
          />
          <button
            onClick={handleSend}
            disabled={isStreaming || disabled || !input.trim()}
            className="shrink-0 w-9 h-9 rounded-xl flex items-center justify-center bg-violet-600 hover:bg-violet-500 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            {isStreaming ? (
              <Loader2 className="w-4 h-4 text-white animate-spin" />
            ) : (
              <Send className="w-4 h-4 text-white" />
            )}
          </button>
        </div>
        <p className="text-xs text-white/20 mt-1.5 text-center">
          Press Enter to send · Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}
