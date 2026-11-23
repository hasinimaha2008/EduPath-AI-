"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  History,
  Bot,
  MessageSquare,
  Trash2,
  Edit3,
  Check,
  ArrowRight,
  Bookmark,
  Calendar,
  X
} from "lucide-react";
import { GlowCard } from "@/components/GlowCard";
import { api } from "@/lib/api";
import { Conversation } from "@/lib/types";

export default function ChatHistoryPage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConv, setActiveConv] = useState<Conversation | null>(null);
  const [loading, setLoading] = useState(true);
  const [renamingId, setRenamingId] = useState<string | null>(null);
  const [newTitle, setNewTitle] = useState("");

  useEffect(() => {
    loadConversations();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function loadConversations() {
    setLoading(true);
    try {
      const data = await api.listConversations();
      setConversations(data);
      if (data.length > 0 && !activeConv) {
        loadConversationDetails(data[0].id);
      }
    } catch (e) {
      console.error("Error loading chat history:", e);
    } finally {
      setLoading(false);
    }
  }

  async function loadConversationDetails(id: string) {
    try {
      const details = await api.getConversation(id);
      setActiveConv(details);
    } catch (e) {
      console.error("Error loading conversation:", e);
    }
  }

  const handleDelete = async (id: string) => {
    try {
      await api.deleteConversation(id);
      const remaining = conversations.filter((c) => c.id !== id);
      setConversations(remaining);
      if (activeConv?.id === id) {
        setActiveConv(remaining.length > 0 ? remaining[0] : null);
        if (remaining.length > 0) loadConversationDetails(remaining[0].id);
      }
    } catch (e) {
      console.error("Error deleting conversation:", e);
    }
  };

  const handleRename = async (id: string) => {
    if (!newTitle.trim()) return;
    try {
      const updated = await api.renameConversation(id, newTitle.trim());
      setConversations((prev) => prev.map((c) => (c.id === id ? { ...c, title: updated.title } : c)));
      if (activeConv?.id === id) {
        setActiveConv({ ...activeConv, title: updated.title });
      }
      setRenamingId(null);
      setNewTitle("");
    } catch (e) {
      console.error("Error renaming conversation:", e);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <History className="w-5 h-5 text-[#C084FC]" /> AI Chat History & Consultations
        </h1>
        <p className="text-xs text-[#A1A1AA] mt-0.5">
          Persisted academic consultations with preserved RAG context, page citations, and conversation history.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[620px]">
        {/* Conversation Sessions List */}
        <GlowCard className="p-4 flex flex-col h-full">
          <div className="pb-3 border-b border-[#30203F] mb-3 flex items-center justify-between">
            <span className="text-xs font-bold text-white uppercase tracking-wider">
              Conversations ({conversations.length})
            </span>
            <Link
              href="/dashboard/assistant"
              className="text-[11px] font-bold text-[#C084FC] hover:underline flex items-center gap-1"
            >
              + New Session
            </Link>
          </div>

          <div className="flex-1 overflow-y-auto space-y-2 pr-1">
            {conversations.length === 0 ? (
              <div className="text-center py-12 text-xs text-[#A1A1AA]">
                No chat sessions found. Start a consultation with the AI Assistant!
              </div>
            ) : (
              conversations.map((c) => {
                const isSelected = activeConv?.id === c.id;
                return (
                  <div
                    key={c.id}
                    onClick={() => loadConversationDetails(c.id)}
                    className={`p-3 rounded-lg border text-left cursor-pointer transition-all ${
                      isSelected
                        ? "bg-[#191225] border-purple-500/60 shadow-[0_0_12px_rgba(168,85,247,0.25)]"
                        : "bg-[#100B18] border-[#30203F] hover:border-purple-500/30"
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <div className="flex items-center gap-2 min-w-0">
                        <MessageSquare className="w-3.5 h-3.5 text-[#C084FC] shrink-0" />
                        <span className="text-xs font-bold text-white truncate">{c.title}</span>
                      </div>
                    </div>
                    <div className="text-[10px] text-[#A1A1AA] mt-1.5 flex items-center justify-between">
                      <span>{new Date(c.updated_at).toLocaleDateString()}</span>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(c.id);
                        }}
                        className="text-red-400 hover:text-red-300 transition-colors"
                        title="Delete"
                      >
                        <Trash2 className="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </GlowCard>

        {/* Active Conversation Transcript */}
        <GlowCard className="p-6 lg:col-span-2 flex flex-col h-full overflow-hidden">
          {activeConv ? (
            <>
              {/* Header */}
              <div className="flex items-center justify-between pb-4 border-b border-[#30203F] mb-4">
                <div className="flex items-center gap-2 min-w-0">
                  {renamingId === activeConv.id ? (
                    <div className="flex items-center gap-1.5 w-full">
                      <input
                        type="text"
                        value={newTitle}
                        onChange={(e) => setNewTitle(e.target.value)}
                        className="px-2 py-1 rounded bg-[#100B18] border border-[#30203F] text-xs text-white"
                      />
                      <button
                        onClick={() => handleRename(activeConv.id)}
                        className="p-1 rounded bg-purple-600 text-white"
                      >
                        <Check className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => setRenamingId(null)}
                        className="p-1 text-[#A1A1AA]"
                      >
                        <X className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  ) : (
                    <>
                      <h2 className="text-base font-bold text-white truncate">
                        {activeConv.title}
                      </h2>
                      <button
                        onClick={() => {
                          setRenamingId(activeConv.id);
                          setNewTitle(activeConv.title);
                        }}
                        className="p-1 text-[#A1A1AA] hover:text-white"
                        title="Rename Chat"
                      >
                        <Edit3 className="w-3.5 h-3.5" />
                      </button>
                    </>
                  )}
                </div>

                <Link
                  href="/dashboard/assistant"
                  className="px-3 py-1.5 rounded-lg bg-gradient-to-r from-[#8B5CF6] to-[#A855F7] text-white text-xs font-bold flex items-center gap-1 shrink-0"
                >
                  <Bot className="w-3.5 h-3.5" /> Continue Chat
                </Link>
              </div>

              {/* Message transcript */}
              <div className="flex-1 overflow-y-auto space-y-4 pr-2">
                {activeConv.messages && activeConv.messages.length > 0 ? (
                  activeConv.messages.map((m) => {
                    const isUser = m.sender_role === "user";
                    return (
                      <div
                        key={m.id}
                        className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}
                      >
                        <div
                          className={`max-w-[85%] rounded-2xl p-4 text-xs sm:text-sm leading-relaxed ${
                            isUser
                              ? "bg-gradient-to-r from-purple-800 to-purple-700 text-white rounded-tr-none"
                              : "bg-[#100B18] border border-[#30203F] text-white rounded-tl-none"
                          }`}
                        >
                          <div className="whitespace-pre-wrap">{m.content}</div>

                          {m.citations && m.citations.length > 0 && (
                            <div className="mt-3 pt-3 border-t border-[#30203F]">
                              <div className="text-[10px] font-bold text-[#C084FC] uppercase mb-1">
                                Grounded Citations:
                              </div>
                              <div className="space-y-1">
                                {m.citations.map((c, i) => (
                                  <div
                                    key={i}
                                    className="p-2 rounded bg-[#191225] border border-[#30203F] text-[11px] text-[#A1A1AA]"
                                  >
                                    <strong className="text-white">{c.doc_title}</strong> (Page{" "}
                                    {c.page_number})
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })
                ) : (
                  <div className="text-center py-10 text-xs text-[#A1A1AA]">
                    No messages recorded in this conversation yet.
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="h-full flex items-center justify-center text-xs text-[#A1A1AA]">
              Select a conversation to view transcript.
            </div>
          )}
        </GlowCard>
      </div>
    </div>
  );
}
