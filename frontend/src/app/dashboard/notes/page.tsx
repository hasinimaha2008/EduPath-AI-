"use client";

import React, { useState, useEffect } from "react";
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
  X
} from "lucide-react";
import { GlowCard } from "@/components/GlowCard";
import { api } from "@/lib/api";
import { Note, DocumentItem, Subject } from "@/lib/types";

const NOTE_TYPES = [
  { id: "detailed", label: "Detailed Notes", desc: "Comprehensive theory and derivations" },
  { id: "short", label: "Short Notes", desc: "Concise high-yield takeaway summary" },
  { id: "chapter_wise", label: "Chapter-wise Notes", desc: "Organized by hierarchical sub-modules" },
  { id: "exam_oriented", label: "Exam-oriented Notes", desc: "High-probability exam scoring focus" },
  { id: "revision", label: "Revision Notes", desc: "Quick-review cheat sheet bullet points" },
  { id: "definitions", label: "Important Definitions", desc: "Key academic terms and formulas" },
  { id: "key_points", label: "Key Points", desc: "Essential system invariants & takeaways" },
  { id: "questions", label: "Important Questions", desc: "Practice questions with model answers" },
];

export default function SmartNotesPage() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [selectedTypeFilter, setSelectedTypeFilter] = useState<string>("all");
  
  // Generator State
  const [selectedSubjectId, setSelectedSubjectId] = useState("");
  const [topicName, setTopicName] = useState("");
  const [selectedDocId, setSelectedDocId] = useState("");
  const [selectedNoteType, setSelectedNoteType] = useState("detailed");
  const [generating, setGenerating] = useState(false);

  // Active Viewing / Editing Note
  const [activeNote, setActiveNote] = useState<Note | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState("");
  const [editContent, setEditContent] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadNotes();
    loadContextData();
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
    try {
      const newNote = await api.generateNotes({
        topic_name: topicName.trim() || undefined,
        document_id: selectedDocId || undefined,
        note_type: selectedNoteType,
      });
      setNotes((prev) => [newNote, ...prev]);
      setActiveNote(newNote);
      setTopicName("");
      setIsEditing(false);
    } catch (err) {
      console.error("Note generation error:", err);
    } finally {
      setGenerating(false);
    }
  };

  const handleTogglePin = async (note: Note) => {
    try {
      const updated = await api.updateNote(note.id, { is_pinned: !note.is_pinned });
      setNotes((prev) => prev.map((n) => (n.id === updated.id ? updated : n)));
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

  const filteredNotes =
    selectedTypeFilter === "all"
      ? notes
      : notes.filter((n) => n.note_type === selectedTypeFilter);

  return (
    <div className="space-y-6">
      {/* Top Title */}
      <div>
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <FileText className="w-5 h-5 text-[#C084FC]" /> Smart Notes Generator
        </h1>
        <p className="text-xs text-[#A1A1AA] mt-0.5">
          Generate structured notes from documents or academic topics across 8 specialized formats.
        </p>
      </div>

      {/* Generator Form Card */}
      <GlowCard className="p-5">
        <form onSubmit={handleGenerate} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-[11px] font-semibold text-[#A1A1AA] uppercase tracking-wider mb-1.5">
                Select Subject (16 Available)
              </label>
              <select
                value={selectedSubjectId}
                onChange={(e) => {
                  setSelectedSubjectId(e.target.value);
                  setTopicName("");
                }}
                className="w-full px-3 py-2 rounded-lg bg-[#100B18] border border-[#30203F] text-xs text-white focus:outline-none focus:border-[#A855F7] transition-all"
              >
                <option value="">Choose Subject...</option>
                {subjects.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name} ({s.code || "CS"})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-[11px] font-semibold text-[#A1A1AA] uppercase tracking-wider mb-1.5">
                Topic or Academic Concept
              </label>
              {selectedSubjectId && (subjects.find((s) => s.id === selectedSubjectId)?.topics.length || 0) > 0 ? (
                <select
                  value={topicName}
                  onChange={(e) => setTopicName(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-[#100B18] border border-[#30203F] text-xs text-white focus:outline-none focus:border-[#A855F7] transition-all"
                >
                  <option value="">Select Topic from Subject...</option>
                  {subjects.find((s) => s.id === selectedSubjectId)?.topics.map((t) => (
                    <option key={t.id} value={t.name}>
                      {t.is_emerging ? "⚡ [Emerging] " : ""}{t.name}
                    </option>
                  ))}
                </select>
              ) : (
                <input
                  type="text"
                  value={topicName}
                  onChange={(e) => setTopicName(e.target.value)}
                  placeholder="e.g. Asymptotic Analysis & Big-O"
                  className="w-full px-3 py-2 rounded-lg bg-[#100B18] border border-[#30203F] text-xs text-white focus:outline-none focus:border-[#A855F7] transition-all"
                />
              )}
            </div>

            <div>
              <label className="block text-[11px] font-semibold text-[#A1A1AA] uppercase tracking-wider mb-1.5">
                Or Select Uploaded Document
              </label>
              <select
                value={selectedDocId}
                onChange={(e) => setSelectedDocId(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-[#100B18] border border-[#30203F] text-xs text-white focus:outline-none focus:border-[#A855F7] transition-all"
              >
                <option value="">No document (Curriculum Knowledge)</option>
                {documents.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.title} ({d.file_type.toUpperCase()})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-[11px] font-semibold text-[#A1A1AA] uppercase tracking-wider mb-1.5">
                Note Format (8 Formats)
              </label>
              <select
                value={selectedNoteType}
                onChange={(e) => setSelectedNoteType(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-[#100B18] border border-[#30203F] text-xs text-white focus:outline-none focus:border-[#A855F7] transition-all"
              >
                {NOTE_TYPES.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={generating || (!topicName.trim() && !selectedDocId)}
              className="px-5 py-2.5 rounded-lg text-xs font-bold bg-gradient-to-r from-[#8B5CF6] to-[#A855F7] text-white shadow-[0_0_15px_rgba(168,85,247,0.35)] hover:shadow-[0_0_20px_rgba(168,85,247,0.6)] disabled:opacity-50 transition-all flex items-center gap-2"
            >
              <Sparkles className="w-3.5 h-3.5" />
              {generating ? "Synthesizing Notes..." : "Generate Smart Notes"}
            </button>
          </div>
        </form>
      </GlowCard>

      {/* Main Split: Notes List & Active Note Viewer/Editor */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[600px]">
        {/* Notes sidebar */}
        <GlowCard className="p-4 flex flex-col h-full">
          <div className="flex items-center justify-between pb-3 border-b border-[#30203F] mb-3">
            <span className="text-xs font-bold text-white uppercase tracking-wider">
              Saved Notes ({filteredNotes.length})
            </span>
            <select
              value={selectedTypeFilter}
              onChange={(e) => setSelectedTypeFilter(e.target.value)}
              className="px-2 py-1 rounded bg-[#100B18] border border-[#30203F] text-[10px] text-[#A1A1AA] focus:outline-none"
            >
              <option value="all">All Types</option>
              {NOTE_TYPES.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.label}
                </option>
              ))}
            </select>
          </div>

          <div className="flex-1 overflow-y-auto space-y-2 pr-1">
            {filteredNotes.length === 0 ? (
              <div className="text-center py-10 text-xs text-[#A1A1AA]">
                No notes found. Generate notes above to get started!
              </div>
            ) : (
              filteredNotes.map((note) => {
                const isSelected = activeNote?.id === note.id;
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
                        : "bg-[#100B18] border-[#30203F] hover:border-purple-500/30"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="text-xs font-bold text-white truncate">
                        {note.title}
                      </div>
                      {note.is_pinned && (
                        <Pin className="w-3 h-3 text-[#A855F7] shrink-0 fill-[#A855F7]" />
                      )}
                    </div>
                    <div className="flex items-center gap-2 mt-2 text-[10px] text-[#A1A1AA]">
                      <span className="px-1.5 py-0.5 rounded bg-purple-500/10 text-[#C084FC]">
                        {note.note_type.replace("_", " ")}
                      </span>
                      <span>{new Date(note.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </GlowCard>

        {/* Note Viewer / Editor (2 cols) */}
        <GlowCard className="p-6 lg:col-span-2 flex flex-col h-full overflow-hidden">
          {activeNote ? (
            <>
              {/* Header Controls */}
              <div className="flex items-center justify-between pb-4 border-b border-[#30203F] mb-4">
                <div className="flex items-center gap-2 min-w-0">
                  <span className="text-xs font-bold px-2 py-0.5 rounded bg-[#8B5CF6]/20 text-[#C084FC] border border-[#A855F7]/30 uppercase shrink-0">
                    {activeNote.note_type.replace("_", " ")}
                  </span>
                  {!isEditing ? (
                    <h2 className="text-base font-bold text-white truncate">
                      {activeNote.title}
                    </h2>
                  ) : (
                    <input
                      type="text"
                      value={editTitle}
                      onChange={(e) => setEditTitle(e.target.value)}
                      className="px-2 py-1 rounded bg-[#100B18] border border-[#30203F] text-xs font-bold text-white w-full focus:outline-none focus:border-[#A855F7]"
                    />
                  )}
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  <button
                    onClick={() => handleTogglePin(activeNote)}
                    title={activeNote.is_pinned ? "Unpin Note" : "Pin to Top"}
                    className={`p-1.5 rounded-lg border transition-all ${
                      activeNote.is_pinned
                        ? "border-[#A855F7] text-[#A855F7] bg-[#A855F7]/10"
                        : "border-[#30203F] text-[#A1A1AA] hover:text-white"
                    }`}
                  >
                    <Pin className="w-3.5 h-3.5" />
                  </button>

                  {!isEditing ? (
                    <button
                      onClick={() => startEdit(activeNote)}
                      className="p-1.5 rounded-lg border border-[#30203F] text-[#A1A1AA] hover:text-white hover:border-purple-500/40 transition-all"
                      title="Edit Note"
                    >
                      <Edit3 className="w-3.5 h-3.5" />
                    </button>
                  ) : (
                    <button
                      onClick={saveEdit}
                      disabled={saving}
                      className="px-3 py-1.5 rounded-lg bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 text-xs font-bold flex items-center gap-1 hover:bg-emerald-500/30 transition-all"
                    >
                      <Save className="w-3.5 h-3.5" /> {saving ? "Saving..." : "Save"}
                    </button>
                  )}

                  <button
                    onClick={() => handleDelete(activeNote.id)}
                    className="p-1.5 rounded-lg border border-[#30203F] text-[#A1A1AA] hover:text-red-400 hover:border-red-500/40 transition-all"
                    title="Delete Note"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              {/* Note Content */}
              <div className="flex-1 overflow-y-auto pr-2">
                {!isEditing ? (
                  <div className="prose prose-invert prose-purple max-w-none text-xs sm:text-sm text-gray-200 whitespace-pre-wrap leading-relaxed">
                    {activeNote.content_markdown}
                  </div>
                ) : (
                  <textarea
                    value={editContent}
                    onChange={(e) => setEditContent(e.target.value)}
                    className="w-full h-full p-4 rounded-lg bg-[#100B18] border border-[#30203F] text-xs font-mono text-white resize-none focus:outline-none focus:border-[#A855F7]"
                  />
                )}
              </div>
            </>
          ) : (
            <div className="h-full flex items-center justify-center text-xs text-[#A1A1AA]">
              Select or generate a note to view its contents.
            </div>
          )}
        </GlowCard>
      </div>
    </div>
  );
}
