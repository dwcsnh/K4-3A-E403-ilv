"use client";

import { useEffect, useRef } from "react";
import Link from "next/link";
import type { Message } from "@/lib/types";
import { useToast } from "@/components/ui/ToastProvider";

interface ChatStreamProps {
  messages: Message[];
  typingLabel: string | null;
  onPreviewArtifacts?: () => void;
  dayId?: string;
  currentSlide?: number;
  onInitiateReply?: (message: Message) => void;
}

function roleBadgeClass(senderType: Message["senderType"]): string {
  if (senderType === "student") return "role-student";
  if (senderType === "generator") return "role-gen";
  return "role-teacher";
}

export function ChatStream({
  messages,
  typingLabel,
  dayId = "day1",
  currentSlide = 1,
  onInitiateReply,
}: ChatStreamProps) {
  const streamRef = useRef<HTMLDivElement>(null);
  const { showToast } = useToast();

  useEffect(() => {
    const el = streamRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages, typingLabel]);

  function scrollToMessage(targetId: string | number | undefined) {
    if (!targetId) return;
    const element = document.getElementById(`msg-${targetId}`);
    if (!element) return;
    element.scrollIntoView({ behavior: "smooth", block: "center" });
    element.classList.remove("msg-highlight");
    void element.offsetWidth;
    element.classList.add("msg-highlight");
    setTimeout(() => {
      element.classList.remove("msg-highlight");
    }, 2000);
  }

  return (
    <>
      <div className="chat-stream" ref={streamRef}>
        {messages.map((msg) => {
          const isUser = msg.senderType === "user";
          return (
            <div
              key={msg.id}
              id={`msg-${msg.id}`}
              className={`msg-row${isUser ? " user" : ""}`}
            >
              <div
                className={`msg-avatar${isUser ? " user-av" : " avatar-" + msg.senderType}`}
              >
                {isUser ? "HV" : msg.avatar}
              </div>
              <div className="msg-content-block">
                <div className="msg-author-tag">
                  <span className="msg-author-name">{msg.senderName}</span>
                  {!isUser && (
                    <span
                      className={`msg-role-badge ${roleBadgeClass(msg.senderType)}`}
                    >
                      {msg.role}
                    </span>
                  )}
                  <span className="msg-time">{msg.time}</span>
                  <button
                    type="button"
                    className="btn-reply-msg"
                    onClick={() => onInitiateReply?.(msg)}
                    title="Trả lời tin nhắn này"
                  >
                    <svg
                      width="12"
                      height="12"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2.5"
                    >
                      <polyline points="9 17 4 12 9 7"></polyline>
                      <path d="M20 18v-2a4 4 0 0 0-4-4H4"></path>
                    </svg>
                    <span>Trả lời</span>
                  </button>
                </div>
                <div className={`msg-bubble ${msg.senderType}`}>
                  {msg.replyTo && (
                    <div
                      className="msg-quote-block"
                      onClick={() => scrollToMessage(msg.replyTo?.id)}
                      role="button"
                      tabIndex={0}
                      title="Nhấn để cuộn đến tin nhắn gốc"
                    >
                      <div className="msg-quote-bar" />
                      <div className="msg-quote-body">
                        <span className="msg-quote-author">
                          {msg.replyTo.senderName}
                        </span>
                        <p className="msg-quote-text truncate">
                          {msg.replyTo.text}
                        </p>
                      </div>
                    </div>
                  )}
                  <span dangerouslySetInnerHTML={{ __html: msg.text }} />

                  {msg.citation && (
                    <div className="mt-2 inline-flex items-center gap-1.5 px-2.5 py-1 bg-white/70 text-text-secondary text-xs rounded-full border border-border-focus/30 shadow-sm">
                      <svg
                        width="12"
                        height="12"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                      >
                        <circle cx="12" cy="12" r="10"></circle>
                        <polyline points="12 6 12 12 16 14"></polyline>
                      </svg>
                      {msg.citation}
                    </div>
                  )}

                  {msg.activeRecallPrompt && (
                    <div className="active-recall-box">
                      🎯 <strong>Thử thách Active Recall:</strong> Bạn hãy thử
                      tự trả lời câu hỏi của bạn Nam xem sao! Nhớ lại kiến thức
                      mà không nhìn sách là cách ghi nhớ tốt nhất.
                    </div>
                  )}

                  {msg.hasArtifactNotice && (
                    <div className="artifact-notification-card">
                      <span
                        style={{
                          fontSize: 12,
                          color: "var(--generator-color)",
                        }}
                      >
                        ✨ Đã tự động tạo học liệu ôn tập cho bài giảng
                      </span>
                      <Link
                        href={`/materials?day=${dayId}&slide=${currentSlide}`}
                        className="artifact-btn-preview"
                        onClick={() => {
                          showToast("Đang mở trang Kho học liệu...");
                        }}
                      >
                        Xem ngay ➔
                      </Link>
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className={`typing-row${typingLabel ? " show" : ""}`}>
        <div className="typing-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
        <span>{typingLabel ?? "AI đang trả lời..."}</span>
      </div>
    </>
  );
}
