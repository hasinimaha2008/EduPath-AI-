"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  Bot,
  Send,
  Sparkles,
  BookOpen,
  Bookmark,
  Check,
  Copy,
  RotateCw,
  Plus,
  Trash2,
  Edit2,
  X,
  PanelLeftClose,
  PanelLeftOpen,
  AlertCircle,
  MessageSquare,
  ChevronRight,
  GraduationCap,
  Square,
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  Paperclip,
  Key,
  Globe,
  Cpu,
  Layers,
  Terminal,
  Brain,
  PenTool,
  HelpCircle
} from "lucide-react";
import { api } from "@/lib/api";
import { ChatMessage, Conversation, DocumentItem, Subject } from "@/lib/types";
import { AssistantMarkdown } from "@/components/AssistantMarkdown";

export default function StudyAssistantPage() {
  // State: Messages & Streaming
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputQuestion, setInputQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [regeneratingId, setRegeneratingId] = useState<string | null>(null);
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null);
  const [speakingMessageId, setSpeakingMessageId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lastFailedQuestion, setLastFailedQuestion] = useState<string | null>(null);

  // State: Speech Recognition
  const [isListening, setIsListening] = useState(false);

  // State: Prerequisites, Context & Language
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [selectedSubjectId, setSelectedSubjectId] = useState<string>("");
  const [selectedDocId, setSelectedDocId] = useState<string>("");
  const [selectedLanguage, setSelectedLanguage] = useState<string>("auto");

  // State: Model Status & Key Configuration Modal
  const [modelStatus, setModelStatus] = useState<{
    is_configured: boolean;
    model_name: string;
    provider: string;
  } | null>(null);
  const [showKeyModal, setShowKeyModal] = useState(false);
  const [inputApiKey, setInputApiKey] = useState("");
  const [keyConfigLoading, setKeyConfigLoading] = useState(false);
  const [keyConfigSuccess, setKeyConfigSuccess] = useState<string | null>(null);
  const [keyConfigError, setKeyConfigError] = useState<string | null>(null);

  // State: Conversation Management
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [editingConvId, setEditingConvId] = useState<string | null>(null);
  const [editingTitle, setEditingTitle] = useState("");

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const speechRecognitionRef = useRef<any>(null);

  // 1. Initial Load: Prerequisites, Conversations & Model Status
  useEffect(() => {
    async function initData() {
      try {
        const [docs, subs, convs, status] = await Promise.all([
          api.listDocuments().catch(() => []),
          api.getSubjects().catch(() => []),
          api.listConversations().catch(() => []),
          api.getAssistantStatus().catch(() => null),
        ]);
        setDocuments(docs.filter((d) => d.status === "ready"));
        setSubjects(subs);
        setConversations(convs);
        if (status) setModelStatus(status);

        // Load most recent conversation if available
        if (convs.length > 0) {
          loadConversation(convs[0].id);
        }

        // Support cross-module deep link from documents/ecosystem
        if (typeof window !== "undefined") {
          const urlParams = new URLSearchParams(window.location.search);
          const docParam = urlParams.get("document_id");
          const subParam = urlParams.get("subject_id");
          if (docParam) setSelectedDocId(docParam);
          if (subParam) setSelectedSubjectId(subParam);
        }
      } catch (e) {
        console.error("Failed to initialize General-Purpose AI Assistant:", e);
      }
    }
    initData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // 2. Auto-scroll on new message or stream token
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading, isStreaming]);

  // 3. Auto-resize input textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 180)}px`;
    }
  }, [inputQuestion]);

  // 4. Load Conversation
  const loadConversation = async (convId: string) => {
    try {
      if (isStreaming) handleStopGeneration();
      setActiveConversationId(convId);
      setError(null);
      setLastFailedQuestion(null);
      const conv = await api.getConversation(convId);
      setMessages(conv.messages || []);
      if (conv.subject_id) setSelectedSubjectId(conv.subject_id);
      if (conv.document_id) setSelectedDocId(conv.document_id);
    } catch (err: any) {
      console.error("Failed to load conversation:", err);
      setError("Unable to load selected conversation.");
    }
  };

  // 5. New Conversation
  const handleNewChat = () => {
    if (isStreaming) handleStopGeneration();
    setActiveConversationId(null);
    setMessages([]);
    setInputQuestion("");
    setError(null);
    setLastFailedQuestion(null);
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };

  // 6. Real-time Streaming Send Question Logic
  const sendQuestion = async (questionText: string) => {
    const question = questionText.trim();
    if (!question || loading || isStreaming) return;

    setError(null);
    setLoading(true);
    setIsStreaming(true);

    // Optimistically add user message
    const tempUserMsg: ChatMessage = {
      id: "temp-user-" + Date.now(),
      conversation_id: activeConversationId || "new",
      sender_role: "user",
      content: question,
      created_at: new Date().toISOString(),
    };

    // Temporary streaming assistant message
    const tempAssistantMsgId = "temp-assistant-" + Date.now();
    const tempAssistantMsg: ChatMessage = {
      id: tempAssistantMsgId,
      conversation_id: activeConversationId || "new",
      sender_role: "assistant",
      content: "",
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, tempUserMsg, tempAssistantMsg]);

    const abortCtrl = new AbortController();
    abortControllerRef.current = abortCtrl;

    try {
      let accumulatedContent = "";

      await api.chatStreamAssistant(
        {
          question,
          conversation_id: activeConversationId || undefined,
          document_id: selectedDocId || undefined,
          subject_id: selectedSubjectId || undefined,
          language: selectedLanguage,
        },
        {
          onMeta: (meta) => {
            setLoading(false);
            if (meta.conversation_id) {
              setActiveConversationId(meta.conversation_id);
            }
          },
          onToken: (token) => {
            setLoading(false);
            accumulatedContent += token;
            setMessages((prev) =>
              prev.map((m) =>
                m.id === tempAssistantMsgId ? { ...m, content: accumulatedContent } : m
              )
            );
          },
          onDone: (doneData) => {
            setIsStreaming(false);
            setLoading(false);
            setLastFailedQuestion(null);
            setMessages((prev) =>
              prev.map((m) =>
                m.id === tempAssistantMsgId ? doneData.assistant_message : m
              )
            );
            // Refresh conversation list to capture smart auto-title
            api.listConversations().then(setConversations).catch(() => {});
          },
          onError: (errMsg) => {
            setIsStreaming(false);
            setLoading(false);
            setError(errMsg || "Streaming connection interrupted.");
            setLastFailedQuestion(question);
          },
        },
        abortCtrl.signal
      );
    } catch (err: any) {
      if (err.name !== "AbortError") {
        setError(err.message || "Failed to receive response from AI Assistant.");
        setLastFailedQuestion(question);
      }
    } finally {
      setIsStreaming(false);
      setLoading(false);
      abortControllerRef.current = null;
    }
  };

  const handleSend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!inputQuestion.trim() || loading || isStreaming) return;

    const question = inputQuestion.trim();
    setInputQuestion("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
    await sendQuestion(question);
  };

  // 7. Retry Failed Message
  const handleRetry = async () => {
    if (!lastFailedQuestion || loading || isStreaming) return;
    const retryQuestion = lastFailedQuestion;
    setLastFailedQuestion(null);
    setError(null);
    // Remove any empty dangling temp message
    setMessages((prev) =>
      prev.filter((m) => !m.id.startsWith("temp-assistant-") || m.content.trim().length > 0)
    );
    await sendQuestion(retryQuestion);
  };

  // 7. Stop Generation
  const handleStopGeneration = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsStreaming(false);
    setLoading(false);
  };

  // 8. Key Down Handler (Enter sends, Shift+Enter newline)
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // 9. Speech-to-Text (Microphone Input)
  const toggleSpeechRecognition = () => {
    if (isListening) {
      if (speechRecognitionRef.current) {
        speechRecognitionRef.current.stop();
      }
      setIsListening(false);
      return;
    }

    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert("Speech recognition is not supported in this browser. Please use Chrome or Edge.");
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.lang =
        selectedLanguage === "te"
          ? "te-IN"
          : selectedLanguage === "hi"
          ? "hi-IN"
          : "en-US";
      recognition.interimResults = true;
      recognition.continuous = false;

      recognition.onstart = () => setIsListening(true);
      recognition.onresult = (event: any) => {
        const transcript = Array.from(event.results)
          .map((result: any) => result[0].transcript)
          .join("");
        setInputQuestion(transcript);
      };
      recognition.onerror = () => setIsListening(false);
      recognition.onend = () => setIsListening(false);

      speechRecognitionRef.current = recognition;
      recognition.start();
    } catch (err) {
      console.error("Speech recognition error:", err);
      setIsListening(false);
    }
  };

  // 10. Text-to-Speech (Read Aloud)
  const toggleSpeechSynthesis = (text: string, msgId: string) => {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) return;

    if (speakingMessageId === msgId) {
      window.speechSynthesis.cancel();
      setSpeakingMessageId(null);
      return;
    }

    window.speechSynthesis.cancel();
    // Clean markdown symbols for natural reading
    const clean = text.replace(/[*#`_~>|\-]/g, " ").replace(/\s+/g, " ").slice(0, 600);
    const utterance = new SpeechSynthesisUtterance(clean);
    if (selectedLanguage === "te") utterance.lang = "te-IN";
    else if (selectedLanguage === "hi") utterance.lang = "hi-IN";
    else utterance.lang = "en-US";

    utterance.onend = () => setSpeakingMessageId(null);
    utterance.onerror = () => setSpeakingMessageId(null);

    setSpeakingMessageId(msgId);
    window.speechSynthesis.speak(utterance);
  };

  // 11. Copy Message
  const handleCopyMessage = async (msgId: string, content: string) => {
    try {
      await navigator.clipboard.writeText(content);
      setCopiedMessageId(msgId);
      setTimeout(() => setCopiedMessageId(null), 2000);
    } catch (err) {
      console.error("Failed to copy message:", err);
    }
  };

  // 12. Regenerate Response
  const handleRegenerate = async (msgId: string) => {
    if (!activeConversationId || loading || isStreaming || regeneratingId) return;

    setRegeneratingId(msgId);
    setError(null);

    try {
      const result = await api.regenerateAssistant(activeConversationId);
      setMessages((prev) => {
        const next = [...prev];
        const lastAssIdx = next.map((m) => m.sender_role).lastIndexOf("assistant");
        if (lastAssIdx !== -1) {
          next[lastAssIdx] = result.assistant_message;
        } else {
          next.push(result.assistant_message);
        }
        return next;
      });
    } catch (err: any) {
      setError(err.message || "Failed to regenerate response.");
    } finally {
      setRegeneratingId(null);
    }
  };

  // 13. Rename Conversation
  const handleStartRename = (conv: Conversation, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingConvId(conv.id);
    setEditingTitle(conv.title);
  };

  const handleSaveRename = async (convId: string, e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!editingTitle.trim()) return;

    try {
      await api.renameConversation(convId, editingTitle.trim());
      setConversations((prev) =>
        prev.map((c) => (c.id === convId ? { ...c, title: editingTitle.trim() } : c))
      );
      setEditingConvId(null);
    } catch (err: any) {
      console.error("Failed to rename conversation:", err);
    }
  };

  // 14. Delete Conversation
  const handleDeleteConversation = async (convId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm("Are you sure you want to delete this conversation?")) return;

    try {
      await api.deleteConversation(convId);
      const remaining = conversations.filter((c) => c.id !== convId);
      setConversations(remaining);

      if (activeConversationId === convId) {
        if (remaining.length > 0) {
          loadConversation(remaining[0].id);
        } else {
          handleNewChat();
        }
      }
    } catch (err: any) {
      console.error("Failed to delete conversation:", err);
    }
  };

  // 15. Configure API Key
  const handleSaveApiKey = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputApiKey.trim()) return;

    setKeyConfigLoading(true);
    setKeyConfigError(null);
    setKeyConfigSuccess(null);

    try {
      const res = await api.configureAssistantKey(inputApiKey.trim());
      setKeyConfigSuccess(res.message);
      setModelStatus({
        is_configured: true,
        model_name: res.model,
        provider: "Google Gemini (gemini-1.5-flash)",
      });
      setTimeout(() => setShowKeyModal(false), 1800);
    } catch (err: any) {
      setKeyConfigError(err.message || "Failed to verify Gemini API key.");
    } finally {
      setKeyConfigLoading(false);
    }
  };

  // General-Purpose Cross-Domain Starter Prompts
  const generalPrompts = [
    {
      title: "System Design & Architecture",
      icon: <Terminal className="w-4 h-4 text-purple-400" />,
      tag: "Software Engineering",
      prompt: "Design a fault-tolerant distributed rate limiter in Python using Redis and a Token Bucket algorithm.",
    },
    {
      title: "First-Principles Mathematics",
      icon: <Brain className="w-4 h-4 text-emerald-400" />,
      tag: "Math & Logic",
      prompt: "Explain Bayes' Theorem from first principles and solve the Monty Hall problem step-by-step with probability tables.",
    },
    {
      title: "Creative Story & Writing",
      icon: <PenTool className="w-4 h-4 text-pink-400" />,
      tag: "Creative Ideation",
      prompt: "Draft an engaging sci-fi narrative prologue exploring the discovery of a non-human signal near Saturn's rings.",
    },
    {
      title: "Multilingual Intelligence (తెలుగు)",
      icon: <Globe className="w-4 h-4 text-amber-400" />,
      tag: "Telugu Native",
      prompt: "Quantum Computing ప్రాథమిక సూత్రాలు మరియు క్లాసికల్ కంప్యూటర్లతో పోల్చితే Qubit ఎలా పనిచేస్తుందో తెలుగులో వివరించండి.",
    },
    {
      title: "Deep Scientific Concepts",
      icon: <Layers className="w-4 h-4 text-cyan-400" />,
      tag: "Astrophysics & Science",
      prompt: "How do supermassive black holes warp spacetime, and what is the exact physical mechanism of Hawking Radiation?",
    },
    {
      title: "Active Empathy & Reflection",
      icon: <Sparkles className="w-4 h-4 text-violet-400" />,
      tag: "Everyday & Empathy",
      prompt: "I've been feeling overwhelmed and burnt out with my daily routine. Can you help me reflect and reset?",
    },
  ];

  return (
    <div className="flex h-[calc(100vh-6rem)] -m-4 sm:-m-6 bg-[#08060D] text-white overflow-hidden relative">
      {/* 1. Left-Hand Collapsible Conversation Drawer */}
      <aside
        className={`${
          isSidebarOpen ? "w-72" : "w-0"
        } transition-all duration-300 ease-in-out shrink-0 bg-[#0E0A17] border-r border-[#261738] flex flex-col overflow-hidden relative z-20`}
      >
        {/* Drawer Header & New Chat Button */}
        <div className="p-3.5 border-b border-[#261738] space-y-2">
          <button
            onClick={handleNewChat}
            className="w-full py-2.5 px-3.5 rounded-xl bg-gradient-to-r from-[#7C3AED] to-[#9333EA] hover:from-[#6D28D9] hover:to-[#7E22CE] text-white font-medium text-xs flex items-center justify-center gap-2 shadow-[0_0_15px_rgba(147,51,234,0.35)] transition-all group"
          >
            <Plus className="w-4 h-4 transition-transform group-hover:rotate-90" />
            <span>New Conversation</span>
          </button>
        </div>

        {/* Conversation List */}
        <div className="flex-1 overflow-y-auto px-2 py-3 space-y-1">
          <div className="px-2 pb-1.5 text-[10px] font-semibold text-[#8B7C9E] uppercase tracking-wider flex items-center justify-between">
            <span>Conversations</span>
            <span className="text-[10px] text-[#C084FC] font-mono">{conversations.length}</span>
          </div>

          {conversations.length === 0 ? (
            <div className="p-4 text-center text-xs text-[#716485]">
              No past conversations yet. Ask any question to start!
            </div>
          ) : (
            conversations.map((c) => {
              const isActive = c.id === activeConversationId;
              const isEditing = editingConvId === c.id;

              return (
                <div
                  key={c.id}
                  onClick={() => !isEditing && loadConversation(c.id)}
                  className={`group relative flex items-center justify-between px-3 py-2 rounded-xl text-xs cursor-pointer transition-all ${
                    isActive
                      ? "bg-[#25153D] text-white border border-[#4C2875] shadow-sm font-medium"
                      : "text-[#A79BB8] hover:bg-[#181026] hover:text-white"
                  }`}
                >
                  <div className="flex items-center gap-2 overflow-hidden flex-1 mr-2">
                    <MessageSquare
                      className={`w-3.5 h-3.5 shrink-0 ${
                        isActive ? "text-[#C084FC]" : "text-[#716485]"
                      }`}
                    />
                    {isEditing ? (
                      <input
                        type="text"
                        value={editingTitle}
                        onChange={(e) => setEditingTitle(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && handleSaveRename(c.id)}
                        autoFocus
                        className="bg-[#120B1F] border border-[#A855F7] rounded px-1.5 py-0.5 text-xs text-white outline-none w-full"
                      />
                    ) : (
                      <span className="truncate">{c.title || "Conversational Session"}</span>
                    )}
                  </div>

                  {/* Actions: Rename / Delete */}
                  {isEditing ? (
                    <div className="flex items-center gap-1 shrink-0">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleSaveRename(c.id);
                        }}
                        className="p-1 hover:text-emerald-400 text-slate-400"
                        title="Save title"
                      >
                        <Check className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setEditingConvId(null);
                        }}
                        className="p-1 hover:text-red-400 text-slate-400"
                        title="Cancel"
                      >
                        <X className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  ) : (
                    <div className="opacity-0 group-hover:opacity-100 flex items-center gap-1 shrink-0 transition-opacity">
                      <button
                        onClick={(e) => handleStartRename(c, e)}
                        className="p-1 text-[#8B7C9E] hover:text-[#C084FC]"
                        title="Rename"
                      >
                        <Edit2 className="w-3 h-3" />
                      </button>
                      <button
                        onClick={(e) => handleDeleteConversation(c.id, e)}
                        className="p-1 text-[#8B7C9E] hover:text-red-400"
                        title="Delete"
                      >
                        <Trash2 className="w-3 h-3" />
                      </button>
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>

        {/* Drawer Footer with Model Status & Key Configuration */}
        <div className="p-3 border-t border-[#261738] text-[11px] text-[#716485] space-y-2">
          <div className="flex items-center justify-between">
            <span className="flex items-center gap-1.5 font-medium text-white">
              <Cpu className="w-3.5 h-3.5 text-[#A855F7]" />
              {modelStatus?.is_configured ? "Google Gemini LLM" : "EduPath AI Engine"}
            </span>
            <button
              onClick={() => setShowKeyModal(true)}
              className="p-1 rounded text-[#C084FC] hover:text-white hover:bg-[#281640] transition-colors"
              title="Configure API Key"
            >
              <Key className="w-3.5 h-3.5" />
            </button>
          </div>
          <div className="text-[10px] text-[#8B7C9E] flex items-center justify-between">
            <span>Model: {modelStatus?.model_name || "gemini-1.5-flash"}</span>
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" title="Ready" />
          </div>
        </div>
      </aside>

      {/* 2. Main Conversational Window */}
      <main className="flex-1 flex flex-col h-full bg-[#08060D] overflow-hidden relative">
        {/* Top Header Bar */}
        <header className="h-14 border-b border-[#231535] bg-[#0E0917]/90 backdrop-blur-md px-4 flex items-center justify-between shrink-0 z-10">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="p-2 rounded-lg bg-[#191126] border border-[#2F1D45] text-[#A79BB8] hover:text-white hover:border-[#8B5CF6] transition-all"
              title={isSidebarOpen ? "Collapse history" : "Expand history"}
            >
              {isSidebarOpen ? (
                <PanelLeftClose className="w-4 h-4" />
              ) : (
                <PanelLeftOpen className="w-4 h-4" />
              )}
            </button>

            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-[#7C3AED] to-[#A855F7] flex items-center justify-center shadow-[0_0_12px_rgba(168,85,247,0.4)]">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <div>
                <h1 className="text-xs sm:text-sm font-bold text-white flex items-center gap-1.5">
                  EduPath AI Assistant
                  <span className="text-[10px] font-normal text-[#C084FC] bg-[#281640] px-1.5 py-0.2 rounded border border-[#4A2675]">
                    General-Purpose LLM
                  </span>
                </h1>
                <p className="text-[10px] text-[#8B7C9E] hidden md:block">
                  Conversational intelligence across programming, math, science, creative writing & everyday life
                </p>
              </div>
            </div>
          </div>

          {/* Controls: Language Selector, Subject Scoping, RAG Attachment & API Key */}
          <div className="flex items-center gap-2">
            {/* Language Selector */}
            <div className="flex items-center gap-1 bg-[#181026] border border-[#2F1D45] rounded-lg px-2 py-1 text-xs text-white">
              <Globe className="w-3.5 h-3.5 text-[#C084FC] shrink-0" />
              <select
                value={selectedLanguage}
                onChange={(e) => setSelectedLanguage(e.target.value)}
                className="bg-transparent border-0 text-xs text-white focus:outline-none cursor-pointer"
                title="Select Language"
              >
                <option value="auto">Auto-Detect</option>
                <option value="en">English</option>
                <option value="te">తెలుగు (Telugu)</option>
                <option value="hi">हिंदी (Hindi)</option>
                <option value="es">Español</option>
                <option value="fr">Français</option>
              </select>
            </div>

            {/* Document Grounding Selector */}
            <div className="hidden sm:flex items-center gap-1">
              <select
                value={selectedDocId}
                onChange={(e) => setSelectedDocId(e.target.value)}
                className="px-2.5 py-1.5 rounded-lg bg-[#181026] border border-[#2F1D45] text-xs text-white focus:outline-none focus:border-[#A855F7] transition-all max-w-[150px] truncate"
                title="Attach Document for Grounded Q&A"
              >
                <option value="">RAG: All Notes</option>
                {documents.map((d) => (
                  <option key={d.id} value={d.id}>
                    Doc: {d.title}
                  </option>
                ))}
              </select>
            </div>

            {/* API Key Modal Button */}
            <button
              onClick={() => setShowKeyModal(true)}
              className="p-1.5 rounded-lg bg-[#191126] border border-[#2F1D45] text-[#C084FC] hover:text-white hover:bg-[#281640] transition-all"
              title="Configure LLM API Key"
            >
              <Key className="w-4 h-4" />
            </button>
          </div>
        </header>

        {/* Message Feed Area */}
        <div className="flex-1 overflow-y-auto px-4 py-6 md:px-8 space-y-6">
          {messages.length === 0 ? (
            /* Empty State: Versatile ChatGPT-like Welcome Hero */
            <div className="h-full flex flex-col items-center justify-center max-w-3xl mx-auto text-center py-6">
              <div className="w-16 h-16 rounded-3xl bg-gradient-to-tr from-[#7C3AED]/25 to-[#A855F7]/30 border border-[#A855F7]/40 flex items-center justify-center mb-4 shadow-[0_0_30px_rgba(168,85,247,0.3)]">
                <Sparkles className="w-8 h-8 text-[#C084FC]" />
              </div>
              <h2 className="text-xl sm:text-2xl font-bold text-white mb-2 tracking-tight">
                What can I help you explore or build today?
              </h2>
              <p className="text-xs sm:text-sm text-[#9C8EB2] max-w-lg mb-8 leading-relaxed">
                I am your general-purpose AI assistant. Ask about code, complex mathematics, creative storytelling, deep science, personal advice, or converse fluently in English, Telugu, and Hindi.
              </p>

              {/* Cross-Domain Suggestion Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 w-full text-left">
                {generalPrompts.map((p, idx) => (
                  <button
                    key={idx}
                    onClick={() => {
                      setInputQuestion(p.prompt);
                      if (textareaRef.current) textareaRef.current.focus();
                    }}
                    className="p-3.5 rounded-xl bg-[#140E21] border border-[#2B1B3F] hover:border-[#8B5CF6]/60 hover:bg-[#1D1330] transition-all group relative text-left shadow-sm flex flex-col justify-between"
                  >
                    <div>
                      <div className="flex items-center justify-between mb-1.5">
                        <span className="flex items-center gap-1.5 text-[10px] font-semibold text-[#A855F7] uppercase tracking-wider">
                          {p.icon}
                          {p.tag}
                        </span>
                        <ChevronRight className="w-3.5 h-3.5 text-[#716485] group-hover:text-[#C084FC] transition-transform group-hover:translate-x-0.5" />
                      </div>
                      <div className="text-xs font-semibold text-white group-hover:text-[#E9D5FF] mb-1">
                        {p.title}
                      </div>
                    </div>
                    <div className="text-[11px] text-[#8B7C9E] line-clamp-2 leading-relaxed mt-1">
                      {p.prompt}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            /* Conversational Stream */
            <div className="max-w-3xl mx-auto space-y-6">
              {messages.map((m) => {
                const isUser = m.sender_role === "user";

                return (
                  <div
                    key={m.id}
                    className={`flex gap-3.5 ${isUser ? "justify-end" : "justify-start"} group`}
                  >
                    {/* Assistant Avatar */}
                    {!isUser && (
                      <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-[#7C3AED] to-[#A855F7] flex items-center justify-center shrink-0 shadow-[0_0_12px_rgba(168,85,247,0.35)] mt-0.5">
                        <Bot className="w-4 h-4 text-white" />
                      </div>
                    )}

                    {/* Message Bubble */}
                    <div
                      className={`relative text-xs sm:text-sm leading-relaxed ${
                        isUser
                          ? "max-w-[85%] sm:max-w-[75%] rounded-2xl rounded-tr-sm bg-gradient-to-br from-[#7C3AED] to-[#6D28D9] text-white p-3.5 sm:p-4 shadow-[0_0_20px_rgba(124,58,237,0.25)] border border-[#8B5CF6]/30"
                          : "flex-1 max-w-[95%] sm:max-w-[88%] rounded-2xl rounded-tl-sm bg-[#130D21] border border-[#2B1B3F] text-white p-4 sm:p-5 shadow-md"
                      }`}
                    >
                      {isUser ? (
                        <div className="whitespace-pre-wrap text-white font-normal leading-relaxed">
                          {m.content}
                        </div>
                      ) : (
                        <div>
                          {/* Rich Markdown Rendering */}
                          <AssistantMarkdown content={m.content} />

                          {/* Grounded Document Citations (if any) */}
                          {m.citations && m.citations.length > 0 && (
                            <div className="mt-4 pt-3.5 border-t border-[#291A3E]">
                              <div className="text-[11px] font-bold uppercase tracking-wider text-[#C084FC] mb-2 flex items-center gap-1.5">
                                <Bookmark className="w-3.5 h-3.5 text-[#A855F7]" />
                                Grounded References ({m.citations.length}):
                              </div>
                              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                                {m.citations.map((c, i) => (
                                  <div
                                    key={i}
                                    className="p-2.5 rounded-lg bg-[#0C0816] border border-[#2A1A3D] text-[11px] text-[#9D8EB0] hover:border-[#8B5CF6]/50 transition-colors"
                                  >
                                    <div className="flex items-center justify-between text-white font-semibold text-[11px] mb-1">
                                      <span className="truncate">{c.doc_title}</span>
                                      <span className="text-[#C084FC] shrink-0 font-mono text-[10px] bg-[#221338] px-1.5 py-0.5 rounded">
                                        p.{c.page_number}
                                      </span>
                                    </div>
                                    <p className="text-[10px] italic text-[#8B7C9E] line-clamp-2">
                                      &ldquo;{c.snippet}&rdquo;
                                    </p>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Interaction Toolbar */}
                          <div className="mt-3.5 pt-2.5 border-t border-[#221535] flex items-center justify-between text-[11px] text-[#7E7092]">
                            <div className="flex items-center gap-2">
                              {/* Copy Response */}
                              <button
                                onClick={() => handleCopyMessage(m.id, m.content)}
                                className="flex items-center gap-1 px-2 py-1 rounded-md bg-[#1B112B] hover:bg-[#281840] hover:text-[#C084FC] text-[#9D8EB0] transition-colors"
                                title="Copy response"
                              >
                                {copiedMessageId === m.id ? (
                                  <>
                                    <Check className="w-3 h-3 text-emerald-400" />
                                    <span className="text-emerald-400">Copied!</span>
                                  </>
                                ) : (
                                  <>
                                    <Copy className="w-3 h-3" />
                                    <span>Copy</span>
                                  </>
                                )}
                              </button>

                              {/* Read Aloud (Text-to-Speech) */}
                              <button
                                onClick={() => toggleSpeechSynthesis(m.content, m.id)}
                                className="flex items-center gap-1 px-2 py-1 rounded-md bg-[#1B112B] hover:bg-[#281840] hover:text-[#C084FC] text-[#9D8EB0] transition-colors"
                                title={speakingMessageId === m.id ? "Stop speaking" : "Read aloud"}
                              >
                                {speakingMessageId === m.id ? (
                                  <>
                                    <VolumeX className="w-3 h-3 text-amber-400 animate-pulse" />
                                    <span className="text-amber-400">Stop</span>
                                  </>
                                ) : (
                                  <>
                                    <Volume2 className="w-3 h-3" />
                                    <span>Speak</span>
                                  </>
                                )}
                              </button>

                              {/* Regenerate Response */}
                              <button
                                onClick={() => handleRegenerate(m.id)}
                                disabled={regeneratingId === m.id || loading || isStreaming}
                                className="flex items-center gap-1 px-2 py-1 rounded-md bg-[#1B112B] hover:bg-[#281840] hover:text-[#C084FC] text-[#9D8EB0] disabled:opacity-50 transition-colors"
                                title="Regenerate this response"
                              >
                                <RotateCw
                                  className={`w-3 h-3 ${
                                    regeneratingId === m.id ? "animate-spin text-[#C084FC]" : ""
                                  }`}
                                />
                                <span>{regeneratingId === m.id ? "Regenerating..." : "Regenerate"}</span>
                              </button>
                            </div>

                            <span className="text-[10px] text-[#5E5170]">
                              EduPath LLM
                            </span>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}

              {/* Live Streaming Indicator */}
              {loading && !isStreaming && (
                <div className="flex gap-3.5 items-start">
                  <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-[#7C3AED] to-[#A855F7] flex items-center justify-center shrink-0 shadow-[0_0_12px_rgba(168,85,247,0.35)] mt-0.5 animate-pulse">
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                  <div className="rounded-2xl rounded-tl-sm bg-[#130D21] border border-[#2B1B3F] p-4 text-xs text-[#C084FC] flex items-center gap-2 shadow-sm">
                    <span className="w-2 h-2 rounded-full bg-[#A855F7] animate-bounce" style={{ animationDelay: "0ms" }} />
                    <span className="w-2 h-2 rounded-full bg-[#A855F7] animate-bounce" style={{ animationDelay: "150ms" }} />
                    <span className="w-2 h-2 rounded-full bg-[#A855F7] animate-bounce" style={{ animationDelay: "300ms" }} />
                    <span className="text-xs text-[#9D8EB0] ml-1">
                      EduPath AI is thinking...
                    </span>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Error Alert */}
        {error && (
          <div className="max-w-3xl mx-auto px-4 w-full">
            <div className="mb-2 p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-xs text-red-400 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{error}</span>
              </div>
              <div className="flex items-center gap-2">
                {lastFailedQuestion && (
                  <button
                    onClick={handleRetry}
                    className="px-2.5 py-1 rounded-lg bg-red-500/20 hover:bg-red-500/30 text-red-200 text-xs font-medium flex items-center gap-1.5 transition-colors"
                    title="Retry sending message"
                  >
                    <RotateCw className="w-3 h-3" />
                    Retry
                  </button>
                )}
                <button
                  onClick={() => {
                    setError(null);
                    setLastFailedQuestion(null);
                  }}
                  className="text-red-400 hover:text-white"
                  title="Dismiss error"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>
        )}

        {/* 3. Bottom Modern Floating Input Area */}
        <div className="p-4 border-t border-[#231535] bg-[#0A0712]/95 backdrop-blur-md shrink-0">
          <div className="max-w-3xl mx-auto relative">
            {/* Active Stop Generating Button */}
            {isStreaming && (
              <div className="flex justify-center mb-2">
                <button
                  onClick={handleStopGeneration}
                  className="px-3.5 py-1.5 rounded-full bg-[#201433] border border-[#A855F7]/40 hover:bg-[#2C1B47] text-white text-xs flex items-center gap-2 shadow-[0_0_15px_rgba(168,85,247,0.3)] transition-all"
                >
                  <Square className="w-3 h-3 text-red-400 fill-red-400" />
                  <span>Stop generating</span>
                </button>
              </div>
            )}

            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSend();
              }}
              className="relative flex items-end gap-2 bg-[#130D21] border border-[#352150] focus-within:border-[#A855F7] focus-within:ring-1 focus-within:ring-[#A855F7] rounded-2xl p-2.5 shadow-[0_0_25px_rgba(0,0,0,0.5)] transition-all"
            >
              {/* Voice Input Microphone Button */}
              <button
                type="button"
                onClick={toggleSpeechRecognition}
                className={`p-2 rounded-xl transition-all shrink-0 ${
                  isListening
                    ? "bg-red-500 text-white animate-pulse shadow-[0_0_15px_rgba(239,68,68,0.5)]"
                    : "text-[#8B7C9E] hover:text-[#C084FC] hover:bg-[#231538]"
                }`}
                title={isListening ? "Listening... click to stop" : "Speak question"}
              >
                {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
              </button>

              {/* Textarea Input */}
              <textarea
                ref={textareaRef}
                value={inputQuestion}
                onChange={(e) => setInputQuestion(e.target.value)}
                onKeyDown={handleKeyDown}
                rows={1}
                placeholder="Message EduPath AI... (Enter to send, Shift+Enter for newline)"
                className="flex-1 bg-transparent border-0 resize-none text-xs sm:text-sm text-white placeholder-[#716485] focus:outline-none focus:ring-0 max-h-44 py-1.5 px-2 leading-relaxed"
              />

              {/* Action Button: Send or Stop */}
              {isStreaming ? (
                <button
                  type="button"
                  onClick={handleStopGeneration}
                  className="p-2.5 rounded-xl bg-red-600 hover:bg-red-500 text-white shadow-[0_0_15px_rgba(239,68,68,0.4)] transition-all shrink-0"
                  title="Stop generating"
                >
                  <Square className="w-4 h-4 fill-white" />
                </button>
              ) : (
                <button
                  type="submit"
                  disabled={loading || !inputQuestion.trim()}
                  className="p-2.5 rounded-xl bg-gradient-to-tr from-[#7C3AED] to-[#9333EA] hover:from-[#6D28D9] hover:to-[#7E22CE] text-white shadow-[0_0_15px_rgba(147,51,234,0.4)] disabled:opacity-40 disabled:hover:from-[#7C3AED] disabled:hover:to-[#9333EA] transition-all shrink-0"
                  title="Send message"
                >
                  {loading ? (
                    <RotateCw className="w-4 h-4 animate-spin" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                </button>
              )}
            </form>

            {/* Footer Notice */}
            <div className="mt-2 text-center text-[10px] text-[#695C7C]">
              EduPath AI can make mistakes. Consider checking important information.
            </div>
          </div>
        </div>
      </main>

      {/* 4. API Key Configuration Modal */}
      {showKeyModal && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#120B1F] border border-[#3B2654] rounded-2xl max-w-md w-full p-6 shadow-2xl relative">
            <button
              onClick={() => setShowKeyModal(false)}
              className="absolute top-4 right-4 text-[#8B7C9E] hover:text-white"
            >
              <X className="w-4 h-4" />
            </button>

            <div className="flex items-center gap-3 mb-4">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-[#7C3AED] to-[#A855F7] flex items-center justify-center">
                <Key className="w-4 h-4 text-white" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">LLM Configuration</h3>
                <p className="text-[11px] text-[#8B7C9E]">
                  Connect your live Google Gemini API Key
                </p>
              </div>
            </div>

            <p className="text-xs text-[#9D8EB0] mb-4 leading-relaxed">
              EduPath AI connects genuinely to Google Gemini (<code>gemini-1.5-flash</code>). Enter your API key below for live high-speed LLM generation across all domains.
            </p>

            <form onSubmit={handleSaveApiKey} className="space-y-4">
              <div>
                <label className="block text-[11px] font-semibold text-[#C084FC] uppercase tracking-wider mb-1.5">
                  Gemini API Key
                </label>
                <input
                  type="password"
                  value={inputApiKey}
                  onChange={(e) => setInputApiKey(e.target.value)}
                  placeholder="AIzaSy..."
                  className="w-full px-3.5 py-2.5 rounded-xl bg-[#0C0816] border border-[#2F1D45] text-xs text-white placeholder-[#716485] focus:outline-none focus:border-[#A855F7]"
                />
              </div>

              {keyConfigSuccess && (
                <div className="p-2.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-xs text-emerald-400 flex items-center gap-2">
                  <Check className="w-4 h-4 shrink-0" />
                  <span>{keyConfigSuccess}</span>
                </div>
              )}

              {keyConfigError && (
                <div className="p-2.5 rounded-lg bg-red-500/10 border border-red-500/30 text-xs text-red-400 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{keyConfigError}</span>
                </div>
              )}

              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowKeyModal(false)}
                  className="px-4 py-2 rounded-xl text-xs text-[#9D8EB0] hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={keyConfigLoading || !inputApiKey.trim()}
                  className="px-4 py-2 rounded-xl bg-gradient-to-r from-[#7C3AED] to-[#9333EA] text-white text-xs font-semibold disabled:opacity-50 transition-all flex items-center gap-1.5"
                >
                  {keyConfigLoading ? (
                    <>
                      <RotateCw className="w-3.5 h-3.5 animate-spin" />
                      <span>Verifying...</span>
                    </>
                  ) : (
                    <span>Save & Verify Key</span>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
