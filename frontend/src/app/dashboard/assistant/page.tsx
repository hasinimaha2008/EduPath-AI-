"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  Bot,
  Send,
  Sparkles,
  BookOpen,
  FileText,
  Bookmark,
  CheckCircle2,
  AlertCircle,
  HelpCircle
} from "lucide-react";
import { GlowCard } from "@/components/GlowCard";
import { api } from "@/lib/api";
import { ChatMessage, DocumentItem, Subject } from "@/lib/types";

export default function StudyAssistantPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputQuestion, setInputQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [selectedDocId, setSelectedDocId] = useState<string>("");
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    async function loadDocs() {
      try {
        const docs = await api.listDocuments();
        setDocuments(docs.filter((d) => d.status === "ready"));
      } catch (e) {
        console.error("Failed to load documents:", e);
      }
    }
    loadDocs();
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputQuestion.trim() || loading) return;

    const question = inputQuestion.trim();
    setInputQuestion("");
    setError(null);
    setLoading(true);

    // Optimistically add user message
    const tempUserMsg: ChatMessage = {
      id: "temp-" + Date.now(),
      conversation_id: conversationId || "new",
      sender_role: "user",
      content: question,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      const response = await api.askAssistant({
        question,
        conversation_id: conversationId || undefined,
        document_id: selectedDocId || undefined,
      });

      setConversationId(response.conversation_id);
      setMessages((prev) => [
        ...prev.filter((m) => m.id !== tempUserMsg.id),
        response.user_message,
        response.assistant_message,
      ]);
    } catch (err: any) {
      setError(err.message || "Failed to receive response from Study Assistant.");
    } finally {
      setLoading(false);
    }
  };

  const sampleQuestions = [
    "Explain 3NF database normalization and functional dependencies with an example.",
    "What is the difference between TCP and UDP at the transport layer?",
    "Explain time complexity bounds for QuickSort vs MergeSort.",
    "How do ACID transactions guarantee data integrity in distributed databases?",
  ];

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      {/* Header bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#30203F] mb-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Bot className="w-5 h-5 text-[#C084FC]" /> AI Study Assistant
          </h1>
          <p className="text-xs text-[#A1A1AA] mt-0.5">
            Academic consultation with grounded RAG document citations and intuitive conceptual breakdowns.
          </p>
        </div>

        {/* Document Context Selector */}
        <div className="flex items-center gap-2">
          <BookOpen className="w-4 h-4 text-[#A1A1AA] shrink-0" />
          <select
            value={selectedDocId}
            onChange={(e) => setSelectedDocId(e.target.value)}
            className="px-3 py-1.5 rounded-lg bg-[#191225] border border-[#30203F] text-xs text-white focus:outline-none focus:border-[#A855F7] transition-all"
          >
            <option value="">All Academic Knowledge (General RAG)</option>
            {documents.map((d) => (
              <option key={d.id} value={d.id}>
                Ground in: {d.title} ({d.file_type.toUpperCase()})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Chat Messages Container */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-2">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-6 max-w-lg mx-auto">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-[#8B5CF6]/20 to-[#A855F7]/30 border border-[#A855F7]/40 flex items-center justify-center mb-4 shadow-[0_0_20px_rgba(168,85,247,0.3)]">
              <Sparkles className="w-7 h-7 text-[#C084FC]" />
            </div>
            <h2 className="text-base font-bold text-white mb-2">
              How can I assist your learning today?
            </h2>
            <p className="text-xs text-[#A1A1AA] mb-6">
              Ask any academic concept question or upload documents to get grounded step-by-step explanations with page citations.
            </p>

            <div className="w-full space-y-2 text-left">
              <div className="text-[11px] font-semibold text-[#A1A1AA] uppercase tracking-wider mb-2">
                Suggested Academic Questions:
              </div>
              {sampleQuestions.map((q, idx) => (
                <button
                  key={idx}
                  onClick={() => setInputQuestion(q)}
                  className="w-full p-2.5 rounded-lg bg-[#191225] border border-[#30203F] hover:border-purple-500/50 text-xs text-[#D8B4FE] text-left transition-all hover:bg-[#191225]/80"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((m) => {
            const isUser = m.sender_role === "user";
            return (
              <div
                key={m.id}
                className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}
              >
                {!isUser && (
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#8B5CF6] to-[#A855F7] flex items-center justify-center shrink-0 shadow-[0_0_10px_rgba(168,85,247,0.4)]">
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                )}

                <div
                  className={`max-w-[80%] rounded-2xl p-4 text-sm leading-relaxed ${
                    isUser
                      ? "bg-gradient-to-r from-purple-800 to-purple-700 text-white shadow-[0_0_15px_rgba(168,85,247,0.25)] rounded-tr-none"
                      : "bg-[#191225] border border-[#30203F] text-white rounded-tl-none shadow-sm"
                  }`}
                >
                  <div className="whitespace-pre-wrap">{m.content}</div>

                  {/* Document citations */}
                  {m.citations && m.citations.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-[#30203F]/80">
                      <div className="text-[10px] font-bold uppercase tracking-wider text-[#C084FC] mb-1.5 flex items-center gap-1">
                        <Bookmark className="w-3 h-3" /> Grounded Document Citations:
                      </div>
                      <div className="space-y-1.5">
                        {m.citations.map((c, i) => (
                          <div
                            key={i}
                            className="p-2 rounded bg-[#100B18] border border-[#30203F] text-[11px] text-[#A1A1AA]"
                          >
                            <span className="font-semibold text-white">
                              {c.doc_title}
                            </span>{" "}
                            <span className="text-[#A855F7]">
                              (Page {c.page_number})
                            </span>
                            <p className="mt-0.5 text-[10px] italic line-clamp-2">
                              &ldquo;{c.snippet}&rdquo;
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Error notification */}
      {error && (
        <div className="my-2 p-2.5 rounded-lg bg-red-500/10 border border-red-500/30 text-xs text-red-400 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Input bar */}
      <form onSubmit={handleSend} className="mt-3 flex gap-2">
        <input
          type="text"
          value={inputQuestion}
          onChange={(e) => setInputQuestion(e.target.value)}
          placeholder="Ask any academic concept question (e.g. explain indexing or normalization)..."
          className="flex-1 px-4 py-3 rounded-xl bg-[#191225] border border-[#30203F] text-sm text-white placeholder-[#A1A1AA]/50 focus:outline-none focus:border-[#A855F7] focus:ring-1 focus:ring-[#A855F7] transition-all"
        />
        <button
          type="submit"
          disabled={loading || !inputQuestion.trim()}
          className="px-5 py-3 rounded-xl font-bold bg-gradient-to-r from-[#8B5CF6] to-[#A855F7] text-white shadow-[0_0_15px_rgba(168,85,247,0.35)] hover:shadow-[0_0_20px_rgba(168,85,247,0.6)] disabled:opacity-50 transition-all flex items-center gap-2"
        >
          {loading ? "Thinking..." : <Send className="w-4 h-4" />}
        </button>
      </form>
    </div>
  );
}
