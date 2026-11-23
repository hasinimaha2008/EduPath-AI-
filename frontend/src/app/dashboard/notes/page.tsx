"use client";

import React, { useState, useEffect, useMemo } from "react";
import {
  FileText,
  Sparkles,
  Pin,
  Trash2,
  Edit3,
  Check,
  Plus,
  BookOpen,
  Filter,
  Save,
  X,
  Copy,
  Download,
  Search,
  Languages,
  Sliders,
  Layers,
  CheckCircle2,
  FileCode,
  FileDown
} from "lucide-react";
import { GlowCard } from "@/components/GlowCard";
import { AssistantMarkdown } from "@/components/AssistantMarkdown";
import { api } from "@/lib/api";
import { Note, DocumentItem, Subject } from "@/lib/types";

const NOTE_TYPES = [
  { id: "detailed", label: "Detailed Notes", desc: "Comprehensive theory and derivations" },
  { id: "short", label: "Short Notes", desc: "Concise high-yield takeaway summary" },
  { id: "chapter_wise", label: "Chapter-wise Notes", desc: "Organized by hierarchical sub-modules" },
  { id: "exam_oriented", label: "Exam-oriented Notes", desc: "High-probability exam scoring focus" },
  { id: "revision", label: "Revision Notes", desc: "Quick-review cheat sheet bullet points" },
  { id: "definitions", label: "Definitions & Formulas", desc: "Key academic terms and formulas" },
  { id: "key_points", label: "Key Points", desc: "Essential system invariants & takeaways" },
  { id: "questions", label: "Important Questions", desc: "Practice questions with model answers" },
  { id: "comparison", label: "Comparison Tables", desc: "Structured trade-off & feature tables" },
  { id: "last_minute", label: "Last-Minute Revision", desc: "High-yield emergency exam revision" },
];

const EXPLANATION_STYLES = [
  { id: "standard", label: "Standard Academic", desc: "Balanced academic rigor and clarity" },
  { id: "beginner", label: "Beginner-Friendly", desc: "Intuitive analogies and simple phrasing" },
  { id: "technical", label: "Technical & Mathematical", desc: "In-depth formal proofs, equations & code" },
  { id: "point_wise", label: "Point-wise Digest", desc: "High-density bullet points and checklists" },
];

const LANGUAGES = [
  { code: "en", name: "English" },
  { code: "te", name: "Telugu (తెలుగు)" },
  { code: "hi", name: "Hindi (हिन्दी)" },
  { code: "es", name: "Spanish (Español)" },
];

export default function SmartNotesPage() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);

  // Search & Filter State
  const [selectedTypeFilter, setSelectedTypeFilter] = useState<string>("all");
  const [selectedSubjectFilter, setSelectedSubjectFilter] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState("");

  // Generator State
  const [selectedSubjectId, setSelectedSubjectId] = useState("");
  const [unitName, setUnitName] = useState("");
  const [topicName, setTopicName] = useState("");
  const [selectedDocId, setSelectedDocId] = useState("");
  const [selectedNoteType, setSelectedNoteType] = useState("detailed");
  const [explanationStyle, setExplanationStyle] = useState("standard");
  const [language, setLanguage] = useState("en");
  const [generating, setGenerating] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Active Viewing / Editing Note
  const [activeNote, setActiveNote] = useState<Note | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState("");
  const [editContent, setEditContent] = useState("");
  const [saving, setSaving] = useState(false);
  const [copied, setCopied] = useState(false);
  const [showExportMenu, setShowExportMenu] = useState(false);

  useEffect(() => {
    loadNotes();
    loadContextData();

    // Cross-module ecosystem deep-linking: prefill topic, mode, document_id
    if (typeof window !== "undefined") {
      const urlParams = new URLSearchParams(window.location.search);
      const topParam = urlParams.get("topic");
      const docParam = urlParams.get("document_id");
      const modeParam = urlParams.get("mode");
      const subParam = urlParams.get("subject_id");

      if (topParam) setTopicName(topParam);
      if (docParam) setSelectedDocId(docParam);
      if (modeParam) setSelectedNoteType(modeParam);
      if (subParam) setSelectedSubjectId(subParam);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function loadNotes() {
    try {
      const data = await api.listNotes();
      setNotes(data);
      if (data.length > 0 && !activeNote) {
        setActiveNote(data[0]);
      }
    } catch (e) {
      console.error("Error loading notes:", e);
    }
  }

  async function loadContextData() {
    try {
      const [docs, subs] = await Promise.all([
        api.listDocuments().catch(() => []),
        api.getSubjects().catch(() => []),
      ]);
      setDocuments(docs.filter((d) => d.status === "ready"));
      setSubjects(subs);
    } catch (e) {
      console.error("Error loading context:", e);
    }
  }

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topicName.trim() && !selectedDocId) return;

    setGenerating(true);
    setErrorMsg(null);
    try {
      const newNote = await api.generateNotes({
        topic_name: topicName.trim() || undefined,
        document_id: selectedDocId || undefined,
        subject_id: selectedSubjectId || undefined,
        unit_name: unitName.trim() || undefined,
        note_type: selectedNoteType,
        explanation_style: explanationStyle,
        language: language,
      });
      setNotes((prev) => [newNote, ...prev]);
      setActiveNote(newNote);
      setTopicName("");
      setUnitName("");
      setIsEditing(false);
    } catch (err: any) {
      console.error("Note generation error:", err);
      setErrorMsg(err.message || "Failed to generate notes. Please try again.");
    } finally {
      setGenerating(false);
    }
  };

  const handleTogglePin = async (note: Note) => {
    try {
      const updated = await api.updateNote(note.id, { is_pinned: !note.is_pinned });
      setNotes((prev) =>
        prev
          .map((n) => (n.id === updated.id ? updated : n))
          .sort((a, b) => (b.is_pinned ? 1 : 0) - (a.is_pinned ? 1 : 0))
      );
      if (activeNote?.id === updated.id) setActiveNote(updated);
    } catch (e) {
      console.error("Error toggling pin:", e);
    }
  };

  const handleDelete = async (noteId: string) => {
    try {
      await api.deleteNote(noteId);
      setNotes((prev) => prev.filter((n) => n.id !== noteId));
      if (activeNote?.id === noteId) {
        const remaining = notes.filter((n) => n.id !== noteId);
        setActiveNote(remaining.length > 0 ? remaining[0] : null);
      }
    } catch (e) {
      console.error("Error deleting note:", e);
    }
  };

  const startEdit = (note: Note) => {
    setEditTitle(note.title);
    setEditContent(note.content_markdown);
    setIsEditing(true);
  };

  const saveEdit = async () => {
    if (!activeNote) return;
    setSaving(true);
    try {
      const updated = await api.updateNote(activeNote.id, {
        title: editTitle,
        content_markdown: editContent,
      });
      setNotes((prev) => prev.map((n) => (n.id === updated.id ? updated : n)));
      setActiveNote(updated);
      setIsEditing(false);
    } catch (e) {
      console.error("Error saving note:", e);
    } finally {
      setSaving(false);
    }
  };

  const handleCopyNote = async () => {
    if (!activeNote) return;
    try {
      await navigator.clipboard.writeText(
        `# ${activeNote.title}\n\n${activeNote.content_markdown}`
      );
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  };

  const handleExport = (format: "md" | "txt") => {
    if (!activeNote) return;
    const sanitizedTitle = activeNote.title.replace(/[^a-zA-Z0-9_-]/g, "_");
    const content =
      format === "md"
        ? `# ${activeNote.title}\n\n${activeNote.content_markdown}`
        : `${activeNote.title}\n\n${activeNote.content_markdown}`;
    const blob = new Blob([content], {
      type: format === "md" ? "text/markdown;charset=utf-8" : "text/plain;charset=utf-8",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${sanitizedTitle}.${format}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    setShowExportMenu(false);
  };

  // Filter notes based on type, subject, and search query
  const filteredNotes = useMemo(() => {
    return notes
      .filter((n) => {
        if (selectedTypeFilter !== "all" && n.note_type !== selectedTypeFilter) return false;
        if (selectedSubjectFilter !== "all" && n.subject_id !== selectedSubjectFilter) return false;
        if (searchQuery.trim()) {
          const q = searchQuery.toLowerCase();
          const matchesTitle = n.title.toLowerCase().includes(q);
          const matchesContent = n.content_markdown.toLowerCase().includes(q);
          if (!matchesTitle && !matchesContent) return false;
        }
        return true;
      })
      .sort((a, b) => (b.is_pinned ? 1 : 0) - (a.is_pinned ? 1 : 0));
  }, [notes, selectedTypeFilter, selectedSubjectFilter, searchQuery]);

  return (
    <div className="space-y-6">
      {/* Top Title & Branding */}
      <div>
        <div className="flex items-center gap-2">
          <FileText className="w-6 h-6 text-[#A855F7]" />
          <h1 className="text-xl font-bold text-white tracking-tight">Smart Notes Generator</h1>
          <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-purple-500/10 border border-purple-500/30 text-[#C084FC]">
            Phase 3 Engine
          </span>
        </div>
        <p className="text-xs text-[#A1A1AA] mt-1">
          Intelligent study-material generation system — topic-wise, unit-wise, multi-lingual, and exam-focused.
        </p>
      </div>

      {/* Generator Form Card */}
      <GlowCard className="p-5 border border-[#30203F] bg-[#100B18]/80 backdrop-blur-md">
        <form onSubmit={handleGenerate} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Subject Selector */}
            <div>
              <label className="block text-[11px] font-semibold text-[#A1A1AA] uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                <BookOpen className="w-3.5 h-3.5 text-[#A855F7]" />
                1. Subject Curriculum
              </label>
              <select
                value={selectedSubjectId}
                onChange={(e) => {
                  setSelectedSubjectId(e.target.value);
                  setTopicName("");
                }}
                className="w-full px-3 py-2 rounded-lg bg-[#08060D] border border-[#30203F] text-xs text-white focus:outline-none focus:border-[#A855F7] transition-all"
              >
                <option value="">General / Any Subject...</option>
                {subjects.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name} ({s.code || "CS"})
                  </option>
                ))}
              </select>
            </div>

            {/* Topic or Unit Input */}
            <div>
              <label className="block text-[11px] font-semibold text-[#A1A1AA] uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5 text-[#C084FC]" />
                2. Topic or Concept
              </label>
              {selectedSubjectId && (subjects.find((s) => s.id === selectedSubjectId)?.topics.length || 0) > 0 ? (
                <select
                  value={topicName}
                  onChange={(e) => setTopicName(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-[#08060D] border border-[#30203F] text-xs text-white focus:outline-none focus:border-[#A855F7] transition-all"
                >
                  <option value="">Select Topic from Subject...</option>
                  {subjects.find((s) => s.id === selectedSubjectId)?.topics.map((t) => (
                    <option key={t.id} value={t.name}>
                      {t.is_emerging ? "⚡ " : ""}{t.name}
                    </option>
                  ))}
                </select>
              ) : (
                <input
                  type="text"
                  value={topicName}
                  onChange={(e) => setTopicName(e.target.value)}
                  placeholder="e.g. Asymptotic Notation & Big-O"
                  className="w-full px-3 py-2 rounded-lg bg-[#08060D] border border-[#30203F] text-xs text-white focus:outline-none focus:border-[#A855F7] transition-all"
                />
              )}
            </div>

            {/* Optional Unit / Module Name */}
            <div>
              <label className="block text-[11px] font-semibold text-[#A1A1AA] uppercase tracking-wider mb-1.5">
                Unit / Module (Optional)
              </label>
              <input
                type="text"
                value={unitName}
                onChange={(e) => setUnitName(e.target.value)}
                placeholder="e.g. Unit 2: Sorting & Search"
                className="w-full px-3 py-2 rounded-lg bg-[#08060D] border border-[#30203F] text-xs text-white focus:outline-none focus:border-[#A855F7] transition-all"
              />
            </div>

            {/* Uploaded Document Selector */}
            <div>
              <label className="block text-[11px] font-semibold text-[#A1A1AA] uppercase tracking-wider mb-1.5">
                Or From Uploaded Document
              </label>
              <select
                value={selectedDocId}
                onChange={(e) => setSelectedDocId(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-[#08060D] border border-[#30203F] text-xs text-white focus:outline-none focus:border-[#A855F7] transition-all"
              >
                <option value="">No document (Curriculum Knowledge)</option>
                {documents.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.title} ({d.file_type.toUpperCase()})
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Row 2: Note Format, Style, Language */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2 border-t border-[#30203F]/60">
            {/* Note Format */}
            <div>
              <label className="block text-[11px] font-semibold text-[#A1A1AA] uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                <FileCode className="w-3.5 h-3.5 text-[#A855F7]" />
                Note Format (10 Modes)
              </label>
              <select
                value={selectedNoteType}
                onChange={(e) => setSelectedNoteType(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-[#08060D] border border-[#30203F] text-xs text-white focus:outline-none focus:border-[#A855F7] transition-all"
              >
                {NOTE_TYPES.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.label} — {t.desc}
                  </option>
                ))}
              </select>
            </div>

            {/* Explanation Style */}
            <div>
              <label className="block text-[11px] font-semibold text-[#A1A1AA] uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                <Sliders className="w-3.5 h-3.5 text-[#C084FC]" />
                Explanation Style
              </label>
              <select
                value={explanationStyle}
                onChange={(e) => setExplanationStyle(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-[#08060D] border border-[#30203F] text-xs text-white focus:outline-none focus:border-[#A855F7] transition-all"
              >
                {EXPLANATION_STYLES.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.label} ({s.desc})
                  </option>
                ))}
              </select>
            </div>

            {/* Language */}
            <div>
              <label className="block text-[11px] font-semibold text-[#A1A1AA] uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                <Languages className="w-3.5 h-3.5 text-[#A855F7]" />
                Language
              </label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-[#08060D] border border-[#30203F] text-xs text-white focus:outline-none focus:border-[#A855F7] transition-all"
              >
                {LANGUAGES.map((l) => (
                  <option key={l.code} value={l.code}>
                    {l.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {errorMsg && (
            <div className="p-2.5 rounded-lg bg-red-500/10 border border-red-500/30 text-xs text-red-300">
              {errorMsg}
            </div>
          )}

          <div className="flex items-center justify-between pt-2">
            <span className="text-[11px] text-[#71717A]">
              ✨ Formatted with KaTeX math rendering, syntax highlighting, and responsive tables.
            </span>
            <button
              type="submit"
              disabled={generating || (!topicName.trim() && !selectedDocId)}
              className="px-6 py-2.5 rounded-lg text-xs font-bold bg-gradient-to-r from-[#8B5CF6] via-[#A855F7] to-[#C084FC] text-white shadow-[0_0_18px_rgba(168,85,247,0.35)] hover:shadow-[0_0_24px_rgba(168,85,247,0.6)] disabled:opacity-50 transition-all flex items-center gap-2"
            >
              <Sparkles className={`w-4 h-4 ${generating ? "animate-spin" : ""}`} />
              {generating ? "Synthesizing Intelligent Notes..." : "Generate Smart Notes"}
            </button>
          </div>
        </form>
      </GlowCard>

      {/* Main Split: Notes List & Active Note Viewer/Editor */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 min-h-[640px]">
        {/* Notes Sidebar */}
        <GlowCard className="p-4 flex flex-col h-full border border-[#30203F] bg-[#100B18]/70">
          {/* Search bar */}
          <div className="relative mb-3">
            <Search className="w-3.5 h-3.5 text-[#71717A] absolute left-2.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search saved notes..."
              className="w-full pl-8 pr-3 py-1.5 rounded-lg bg-[#08060D] border border-[#30203F] text-xs text-white placeholder-[#71717A] focus:outline-none focus:border-[#A855F7] transition-all"
            />
          </div>

          {/* Filters Bar */}
          <div className="grid grid-cols-2 gap-2 pb-3 border-b border-[#30203F] mb-3">
            <select
              value={selectedTypeFilter}
              onChange={(e) => setSelectedTypeFilter(e.target.value)}
              className="px-2 py-1 rounded bg-[#08060D] border border-[#30203F] text-[10px] text-[#A1A1AA] focus:outline-none focus:border-[#A855F7]"
            >
              <option value="all">All Formats</option>
              {NOTE_TYPES.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.label}
                </option>
              ))}
            </select>

            <select
              value={selectedSubjectFilter}
              onChange={(e) => setSelectedSubjectFilter(e.target.value)}
              className="px-2 py-1 rounded bg-[#08060D] border border-[#30203F] text-[10px] text-[#A1A1AA] focus:outline-none focus:border-[#A855F7]"
            >
              <option value="all">All Subjects</option>
              {subjects.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </div>

          {/* Count Info */}
          <div className="flex items-center justify-between text-[10px] text-[#71717A] px-1 mb-2 font-mono">
            <span>SHOWING {filteredNotes.length} OF {notes.length} NOTES</span>
            {filteredNotes.some((n) => n.is_pinned) && (
              <span className="text-[#C084FC] flex items-center gap-1">
                <Pin className="w-2.5 h-2.5 fill-[#C084FC]" /> PINNED FIRST
              </span>
            )}
          </div>

          {/* Notes list */}
          <div className="flex-1 overflow-y-auto space-y-2 pr-1 max-h-[520px]">
            {filteredNotes.length === 0 ? (
              <div className="text-center py-12 text-xs text-[#71717A]">
                {searchQuery || selectedTypeFilter !== "all" || selectedSubjectFilter !== "all"
                  ? "No notes matching your filter criteria."
                  : "No notes generated yet. Generate your first smart note above!"}
              </div>
            ) : (
              filteredNotes.map((note) => {
                const isSelected = activeNote?.id === note.id;
                const noteSubject = subjects.find((s) => s.id === note.subject_id);

                return (
                  <div
                    key={note.id}
                    onClick={() => {
                      setActiveNote(note);
                      setIsEditing(false);
                    }}
                    className={`p-3 rounded-lg border text-left cursor-pointer transition-all ${
                      isSelected
                        ? "bg-[#191225] border-purple-500/60 shadow-[0_0_12px_rgba(168,85,247,0.25)]"
                        : "bg-[#08060D] border-[#30203F] hover:border-purple-500/30 hover:bg-[#120B1C]"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="text-xs font-bold text-white truncate flex-1">
                        {note.title}
                      </div>
                      {note.is_pinned && (
                        <Pin className="w-3 h-3 text-[#A855F7] shrink-0 fill-[#A855F7]" />
                      )}
                    </div>

                    <div className="flex items-center flex-wrap gap-1.5 mt-2 text-[10px]">
                      <span className="px-1.5 py-0.5 rounded bg-purple-500/10 border border-purple-500/20 text-[#C084FC]">
                        {note.note_type.replace(/_/g, " ")}
                      </span>
                      {noteSubject && (
                        <span className="px-1.5 py-0.5 rounded bg-[#30203F]/40 text-[#A1A1AA] truncate max-w-[110px]">
                          {noteSubject.name}
                        </span>
                      )}
                      <span className="text-[#71717A] ml-auto">
                        {new Date(note.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </GlowCard>

        {/* Note Viewer / Editor (2 cols) */}
        <GlowCard className="p-6 lg:col-span-2 flex flex-col h-full border border-[#30203F] bg-[#100B18]/70 overflow-hidden">
          {activeNote ? (
            <>
              {/* Header Controls */}
              <div className="flex items-center justify-between pb-4 border-b border-[#30203F] mb-4 gap-3">
                <div className="flex items-center gap-2 min-w-0 flex-1">
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-[#8B5CF6]/20 text-[#C084FC] border border-[#A855F7]/30 uppercase shrink-0">
                    {activeNote.note_type.replace(/_/g, " ")}
                  </span>
                  {!isEditing ? (
                    <h2 className="text-base font-bold text-white truncate" title={activeNote.title}>
                      {activeNote.title}
                    </h2>
                  ) : (
                    <input
                      type="text"
                      value={editTitle}
                      onChange={(e) => setEditTitle(e.target.value)}
                      className="px-2.5 py-1 rounded bg-[#08060D] border border-[#30203F] text-xs font-bold text-white w-full focus:outline-none focus:border-[#A855F7]"
                      placeholder="Note Title"
                    />
                  )}
                </div>

                {/* Toolbar Buttons */}
                <div className="flex items-center gap-2 shrink-0">
                  {/* Copy Button */}
                  <button
                    onClick={handleCopyNote}
                    title="Copy Note to Clipboard"
                    className="p-1.5 rounded-lg border border-[#30203F] bg-[#08060D] text-[#A1A1AA] hover:text-white hover:border-purple-500/40 transition-all flex items-center gap-1 text-xs"
                  >
                    {copied ? (
                      <>
                        <Check className="w-3.5 h-3.5 text-emerald-400" />
                        <span className="text-[10px] text-emerald-400 font-semibold pr-1">Copied</span>
                      </>
                    ) : (
                      <Copy className="w-3.5 h-3.5" />
                    )}
                  </button>

                  {/* Export Dropdown */}
                  <div className="relative">
                    <button
                      onClick={() => setShowExportMenu(!showExportMenu)}
                      title="Export Note"
                      className="p-1.5 rounded-lg border border-[#30203F] bg-[#08060D] text-[#A1A1AA] hover:text-white hover:border-purple-500/40 transition-all flex items-center gap-1 text-xs"
                    >
                      <Download className="w-3.5 h-3.5" />
                      <span className="text-[10px] hidden sm:inline">Export</span>
                    </button>
                    {showExportMenu && (
                      <div className="absolute right-0 mt-1 w-36 rounded-lg bg-[#140D20] border border-[#30203F] shadow-xl z-20 py-1 text-xs">
                        <button
                          onClick={() => handleExport("md")}
                          className="w-full px-3 py-1.5 text-left text-gray-200 hover:bg-purple-500/20 hover:text-white flex items-center gap-2"
                        >
                          <FileCode className="w-3.5 h-3.5 text-[#C084FC]" /> Markdown (.md)
                        </button>
                        <button
                          onClick={() => handleExport("txt")}
                          className="w-full px-3 py-1.5 text-left text-gray-200 hover:bg-purple-500/20 hover:text-white flex items-center gap-2"
                        >
                          <FileDown className="w-3.5 h-3.5 text-[#A855F7]" /> Plain Text (.txt)
                        </button>
                      </div>
                    )}
                  </div>

                  {/* Pin Button */}
                  <button
                    onClick={() => handleTogglePin(activeNote)}
                    title={activeNote.is_pinned ? "Unpin Note" : "Pin to Top"}
                    className={`p-1.5 rounded-lg border transition-all ${
                      activeNote.is_pinned
                        ? "border-[#A855F7] text-[#A855F7] bg-[#A855F7]/10"
                        : "border-[#30203F] bg-[#08060D] text-[#A1A1AA] hover:text-white"
                    }`}
                  >
                    <Pin className="w-3.5 h-3.5" />
                  </button>

                  {/* Edit Toggle */}
                  {!isEditing ? (
                    <button
                      onClick={() => startEdit(activeNote)}
                      className="p-1.5 rounded-lg border border-[#30203F] bg-[#08060D] text-[#A1A1AA] hover:text-white hover:border-purple-500/40 transition-all"
                      title="Edit Note"
                    >
                      <Edit3 className="w-3.5 h-3.5" />
                    </button>
                  ) : (
                    <div className="flex items-center gap-1.5">
                      <button
                        onClick={() => setIsEditing(false)}
                        className="p-1.5 rounded-lg border border-[#30203F] bg-[#08060D] text-[#A1A1AA] hover:text-white transition-all"
                        title="Cancel"
                      >
                        <X className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={saveEdit}
                        disabled={saving}
                        className="px-3 py-1 rounded-lg bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 text-xs font-bold flex items-center gap-1 hover:bg-emerald-500/30 transition-all"
                      >
                        <Save className="w-3.5 h-3.5" /> {saving ? "Saving..." : "Save"}
                      </button>
                    </div>
                  )}

                  {/* Delete Button */}
                  <button
                    onClick={() => handleDelete(activeNote.id)}
                    className="p-1.5 rounded-lg border border-[#30203F] bg-[#08060D] text-[#A1A1AA] hover:text-red-400 hover:border-red-500/40 transition-all"
                    title="Delete Note"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              {/* Note Content Area */}
              <div className="flex-1 overflow-y-auto pr-2">
                {!isEditing ? (
                  <div className="py-2">
                    <AssistantMarkdown content={activeNote.content_markdown} />
                  </div>
                ) : (
                  <textarea
                    value={editContent}
                    onChange={(e) => setEditContent(e.target.value)}
                    placeholder="Enter markdown note content here..."
                    className="w-full h-full min-h-[460px] p-4 rounded-lg bg-[#08060D] border border-[#30203F] text-xs font-mono text-gray-200 resize-none focus:outline-none focus:border-[#A855F7] leading-relaxed"
                  />
                )}
              </div>
            </>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-center p-8 text-xs text-[#71717A]">
              <FileText className="w-12 h-12 text-[#30203F] mb-3" />
              <p className="text-white font-medium mb-1">No Note Selected</p>
              <p className="max-w-sm text-[#71717A]">
                Select a note from the sidebar or generate a new one using the synthesizer above.
              </p>
            </div>
          )}
        </GlowCard>
      </div>
    </div>
  );
}
