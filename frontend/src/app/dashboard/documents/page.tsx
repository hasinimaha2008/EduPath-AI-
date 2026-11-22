"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  UploadCloud,
  FileText,
  Trash2,
  CheckCircle2,
  AlertCircle,
  Clock,
  Layers,
  BookOpen,
  ArrowRight,
  Sparkles,
  Eye,
  X,
  Send,
  Brain,
  HelpCircle,
  FileCheck,
  Award,
  ListFilter,
  Bookmark,
  Search,
  RotateCw,
  ChevronRight,
  FileSpreadsheet,
  FileCode,
  Check,
  Copy
} from "lucide-react";
import { GlowCard } from "@/components/GlowCard";
import { api } from "@/lib/api";
import { DocumentItem, Subject } from "@/lib/types";
import { AssistantMarkdown } from "@/components/AssistantMarkdown";

export default function DocumentManagementPage() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [loading, setLoading] = useState(true);

  // Upload Form State
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [selectedSubjectId, setSelectedSubjectId] = useState("");
  const [uploading, setUploading] = useState(false);
  const [uploadStep, setUploadStep] = useState<string>("");
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  // Document Preview Modal State
  const [previewDoc, setPreviewDoc] = useState<any | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);

  // AI Document Intelligence Suite Modal State
  const [activeIntelDoc, setActiveIntelDoc] = useState<DocumentItem | null>(null);
  const [activeTab, setActiveTab] = useState<
    "summary" | "notes" | "exam" | "qa" | "quiz" | "formulas" | "topics" | "revision" | "explain"
  >("summary");
  const [intelLoading, setIntelLoading] = useState(false);
  const [intelData, setIntelData] = useState<any>(null);

  // Interactive Document Q&A Sub-State
  const [qaInput, setQaInput] = useState("");
  const [qaLoading, setQaLoading] = useState(false);
  const [qaHistory, setQaHistory] = useState<
    Array<{
      question: string;
      answer: string;
      found_in_document: boolean;
      citations: Array<{ doc_title: string; page_number: number; snippet: string }>;
    }>
  >([]);

  // Explain Difficult Topic Sub-State
  const [topicToExplain, setTopicToExplain] = useState("");
  const [explainLoading, setExplainLoading] = useState(false);
  const [explainResult, setExplainResult] = useState<any>(null);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    setLoading(true);
    try {
      const [docs, subs] = await Promise.all([
        api.listDocuments().catch(() => []),
        api.getSubjects().catch(() => []),
      ]);
      setDocuments(docs);
      setSubjects(subs);
    } catch (e) {
      console.error("Error loading documents:", e);
    } finally {
      setLoading(false);
    }
  }

  // File Selection & Drag-and-Drop Handler with Strict Validation
  const validateAndSelectFile = (selected: File) => {
    setUploadError(null);
    setUploadSuccess(null);

    const allowedExtensions = [".pdf", ".docx", ".pptx", ".txt"];
    const ext = "." + selected.name.split(".").pop()?.toLowerCase();

    if (!allowedExtensions.includes(ext)) {
      setUploadError(
        `Unsupported file format '${ext}'. Please upload a PDF (.pdf), Word (.docx), PowerPoint (.pptx), or Text (.txt) file.`
      );
      return;
    }

    if (selected.size > 25 * 1024 * 1024) {
      setUploadError("File exceeds the maximum allowed size of 25MB.");
      return;
    }

    setFile(selected);
    if (!title) {
      setTitle(selected.name.replace(/\.[^/.]+$/, ""));
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSelectFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSelectFile(e.target.files[0]);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    setUploadError(null);
    setUploadSuccess(null);
    setUploadStep("Uploading file to secure storage...");

    const stepTimer1 = setTimeout(() => {
      setUploadStep("Extracting text pages & structural headings...");
    }, 800);
    const stepTimer2 = setTimeout(() => {
      setUploadStep("Generating vector embeddings & indexing for RAG...");
    }, 1800);

    try {
      const newDoc = await api.uploadDocument(
        file,
        title.trim() || undefined,
        selectedSubjectId || undefined
      );

      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);

      setDocuments((prev) => [newDoc, ...prev]);
      setUploadSuccess(`"${newDoc.title}" successfully processed and indexed (${newDoc.chunk_count} RAG chunks)!`);
      setFile(null);
      setTitle("");
      setSelectedSubjectId("");
      setUploadStep("");
    } catch (err: any) {
      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);
      setUploadError(err.message || "Failed to process document.");
      setUploadStep("");
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (docId: string) => {
    if (!confirm("Are you sure you want to delete this document? Extracted knowledge will be removed from RAG search.")) {
      return;
    }
    try {
      await api.deleteDocument(docId);
      setDocuments((prev) => prev.filter((d) => d.id !== docId));
      if (activeIntelDoc?.id === docId) setActiveIntelDoc(null);
      if (previewDoc?.id === docId) setPreviewDoc(null);
    } catch (e) {
      console.error("Error deleting document:", e);
    }
  };

  // Open Document Preview Modal
  const handleOpenPreview = async (doc: DocumentItem) => {
    setPreviewLoading(true);
    try {
      const data = await api.previewDocument(doc.id);
      setPreviewDoc(data);
    } catch (err) {
      console.error("Preview failed:", err);
      setPreviewDoc({
        id: doc.id,
        title: doc.title,
        file_name: doc.file_name,
        file_type: doc.file_type,
        file_size: doc.file_size,
        status: doc.status,
        total_pages: 1,
        total_chunks: doc.chunk_count,
        total_words: "N/A",
        sample_chunks: [],
      });
    } finally {
      setPreviewLoading(false);
    }
  };

  // Open AI Document Intelligence Suite
  const handleOpenIntel = async (
    doc: DocumentItem,
    tab: "summary" | "notes" | "exam" | "qa" | "quiz" | "formulas" | "topics" | "revision" | "explain" = "summary"
  ) => {
    setActiveIntelDoc(doc);
    setActiveTab(tab);
    setIntelData(null);
    setQaHistory([]);
    setExplainResult(null);
    loadTabContent(doc.id, tab);
  };

  // Load Content for Selected Tab
  const loadTabContent = async (docId: string, tab: string) => {
    setIntelLoading(true);
    setIntelData(null);
    try {
      if (tab === "summary") {
        const res = await api.getDocumentSummary(docId);
        setIntelData(res);
      } else if (tab === "notes") {
        const res = await api.getDocumentNotes(docId);
        setIntelData(res);
      } else if (tab === "exam") {
        const res = await api.getDocumentExamPrep(docId);
        setIntelData(res);
      } else if (tab === "formulas") {
        const res = await api.getDocumentDefinitionsAndFormulas(docId);
        setIntelData(res);
      } else if (tab === "topics") {
        const res = await api.getDocumentImportantTopics(docId);
        setIntelData(res);
      } else if (tab === "revision") {
        const res = await api.getDocumentRevisionKit(docId);
        setIntelData(res);
      } else if (tab === "quiz") {
        const res = await api.generateDocumentQuestions(docId, 5);
        setIntelData(res);
      }
    } catch (e: any) {
      console.error(`Error loading ${tab}:`, e);
      setIntelData({ error: e.message || "Failed to load analysis for this section." });
    } finally {
      setIntelLoading(false);
    }
  };

  // Document Q&A Submission Handler
  const handleSendQa = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!qaInput.trim() || !activeIntelDoc || qaLoading) return;

    const question = qaInput.trim();
    setQaInput("");
    setQaLoading(true);

    try {
      const res = await api.askDocument(activeIntelDoc.id, question);
      setQaHistory((prev) => [
        ...prev,
        {
          question,
          answer: res.answer,
          found_in_document: res.found_in_document,
          citations: res.citations || [],
        },
      ]);
    } catch (err: any) {
      setQaHistory((prev) => [
        ...prev,
        {
          question,
          answer: err.message || "An error occurred while querying the document.",
          found_in_document: false,
          citations: [],
        },
      ]);
    } finally {
      setQaLoading(false);
    }
  };

  // Explain Difficult Topic Submission Handler
  const handleExplainTopic = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!topicToExplain.trim() || !activeIntelDoc || explainLoading) return;

    setExplainLoading(true);
    setExplainResult(null);
    try {
      const res = await api.explainDocumentTopic(activeIntelDoc.id, topicToExplain.trim());
      setExplainResult(res);
    } catch (err: any) {
      setExplainResult({
        topic: topicToExplain,
        explanation: err.message || "Failed to generate topic explanation.",
        citations: [],
      });
    } finally {
      setExplainLoading(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const getFormatBadgeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case "pdf":
        return "bg-red-500/15 text-red-400 border-red-500/30";
      case "docx":
      case "doc":
        return "bg-blue-500/15 text-blue-400 border-blue-500/30";
      case "pptx":
      case "ppt":
        return "bg-amber-500/15 text-amber-400 border-amber-500/30";
      case "txt":
      case "md":
        return "bg-emerald-500/15 text-emerald-400 border-emerald-500/30";
      default:
        return "bg-purple-500/15 text-purple-400 border-purple-500/30";
    }
  };

  return (
    <div className="space-y-6">
      {/* 1. Header */}
      <div>
        <div className="flex items-center justify-between flex-wrap gap-2">
          <div>
            <h1 className="text-xl sm:text-2xl font-bold text-white flex items-center gap-2.5">
              <UploadCloud className="w-6 h-6 text-[#C084FC]" />
              Document Upload & Intelligence 2.0
            </h1>
            <p className="text-xs sm:text-sm text-[#A1A1AA] mt-1">
              Upload course notes, slides, and textbooks in PDF, DOCX, PPTX, or TXT format. Powered by hybrid lexical-vector retrieval (RAG) and comprehensive AI document understanding.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-1 rounded-lg bg-[#181026] border border-[#30203F] text-[11px] text-[#C084FC] font-semibold">
              Supported: PDF • DOCX • PPTX • TXT
            </span>
          </div>
        </div>
      </div>

      {/* 2. Drag & Drop Upload GlowCard */}
      <GlowCard glow className="p-6">
        <h2 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-[#A855F7]" /> Upload Academic Document
        </h2>

        {uploadError && (
          <div className="mb-4 p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-xs text-red-400 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{uploadError}</span>
            </div>
            <button onClick={() => setUploadError(null)} className="text-red-400 hover:text-white">
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {uploadSuccess && (
          <div className="mb-4 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-xs text-emerald-400 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <span>{uploadSuccess}</span>
            </div>
            <button onClick={() => setUploadSuccess(null)} className="text-emerald-400 hover:text-white">
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        <form onSubmit={handleUpload} className="space-y-4">
          {/* Drag & Drop Surface */}
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-2xl p-8 text-center transition-all ${
              isDragging
                ? "border-[#A855F7] bg-[#221338]/60 shadow-[0_0_25px_rgba(168,85,247,0.35)] scale-[1.01]"
                : "border-[#30203F] hover:border-[#8B5CF6]/70 bg-[#100B18]/50"
            }`}
          >
            <input
              type="file"
              id="file-upload"
              accept=".pdf,.docx,.pptx,.txt"
              onChange={handleFileChange}
              className="hidden"
            />
            <label htmlFor="file-upload" className="cursor-pointer block">
              <UploadCloud
                className={`w-12 h-12 mx-auto mb-3 transition-colors ${
                  isDragging ? "text-[#C084FC] animate-bounce" : "text-[#8B5CF6]"
                }`}
              />
              <span className="text-sm font-bold text-white block">
                {file ? (
                  <span className="text-[#C084FC] flex items-center justify-center gap-1.5">
                    <FileText className="w-4 h-4" /> {file.name} ({formatFileSize(file.size)})
                  </span>
                ) : (
                  "Drag & drop document here, or click to browse"
                )}
              </span>
              <span className="text-xs text-[#8B7C9E] mt-1.5 block">
                Accepts PDF (.pdf), Word (.docx), PowerPoint (.pptx), Text (.txt) • Maximum 25MB
              </span>
            </label>

            {file && (
              <div className="mt-3 flex items-center justify-center gap-2">
                <button
                  type="button"
                  onClick={() => setFile(null)}
                  className="px-2.5 py-1 rounded-lg bg-red-500/15 border border-red-500/30 text-xs text-red-300 hover:bg-red-500/25 transition-colors flex items-center gap-1"
                >
                  <Trash2 className="w-3 h-3" /> Remove File
                </button>
              </div>
            )}
          </div>

          {/* Metadata Inputs: Title & Subject Association */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-[11px] font-semibold text-[#A1A1AA] uppercase tracking-wider mb-1.5">
                Document Title
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Distributed Systems & Concurrency Notes"
                className="w-full px-3.5 py-2.5 rounded-xl bg-[#100B18] border border-[#30203F] text-xs text-white placeholder-[#716485] focus:outline-none focus:border-[#A855F7]"
              />
            </div>

            <div>
              <label className="block text-[11px] font-semibold text-[#A1A1AA] uppercase tracking-wider mb-1.5">
                Associate with Subject (Optional)
              </label>
              <select
                value={selectedSubjectId}
                onChange={(e) => setSelectedSubjectId(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-[#100B18] border border-[#30203F] text-xs text-white focus:outline-none focus:border-[#A855F7] cursor-pointer"
              >
                <option value="">General Curriculum (All Subjects)</option>
                {subjects.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name} ({s.code})
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Upload Progress Status Indicator */}
          {uploading && (
            <div className="p-3.5 rounded-xl bg-[#1B112B] border border-[#3E255C] text-xs text-[#C084FC] space-y-2">
              <div className="flex items-center justify-between font-medium">
                <span className="flex items-center gap-2">
                  <RotateCw className="w-4 h-4 animate-spin text-[#A855F7]" />
                  {uploadStep || "Processing document..."}
                </span>
                <span className="text-[10px] uppercase font-mono text-[#A855F7] tracking-wider">Processing</span>
              </div>
              <div className="w-full bg-[#100B18] rounded-full h-1.5 overflow-hidden">
                <div className="bg-gradient-to-r from-[#7C3AED] to-[#C084FC] h-full w-full animate-pulse" />
              </div>
            </div>
          )}

          {/* Upload Button */}
          <div className="flex justify-end pt-1">
            <button
              type="submit"
              disabled={uploading || !file}
              className="px-6 py-2.5 rounded-xl text-xs font-bold bg-gradient-to-r from-[#8B5CF6] to-[#A855F7] hover:from-[#7C3AED] hover:to-[#9333EA] text-white shadow-[0_0_15px_rgba(168,85,247,0.35)] disabled:opacity-40 transition-all flex items-center gap-2"
            >
              <UploadCloud className="w-4 h-4" />
              {uploading ? "Extracting & Vectorizing..." : "Upload & Process Document"}
            </button>
          </div>
        </form>
      </GlowCard>

      {/* 3. Uploaded Documents Catalog */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-[#A855F7]" /> Managed Documents ({documents.length})
          </h2>
          <span className="text-xs text-[#8B7C9E]">
            Indexed for Instant Semantic Search & Self-Assessment
          </span>
        </div>

        {documents.length === 0 ? (
          <GlowCard className="p-8 text-center text-xs text-[#A1A1AA]">
            No documents uploaded yet. Upload a PDF, Word doc, PowerPoint presentation, or Text file above to enable cited RAG questioning and automated study materials.
          </GlowCard>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {documents.map((doc) => (
              <GlowCard key={doc.id} className="p-5 flex flex-col justify-between">
                <div>
                  {/* Title & Status Badge */}
                  <div className="flex items-start justify-between gap-3 mb-2">
                    <div className="flex items-start gap-3 min-w-0">
                      <div className="w-10 h-10 rounded-xl bg-purple-500/20 border border-purple-500/30 flex items-center justify-center shrink-0 shadow-sm">
                        <FileText className="w-5 h-5 text-[#C084FC]" />
                      </div>
                      <div className="min-w-0">
                        <h3 className="text-sm font-bold text-white truncate" title={doc.title}>
                          {doc.title}
                        </h3>
                        <p className="text-[11px] text-[#A1A1AA] truncate">{doc.file_name}</p>
                      </div>
                    </div>

                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider shrink-0 ${
                        doc.status === "ready"
                          ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                          : doc.status === "processing"
                          ? "bg-amber-500/20 text-amber-300 border border-amber-500/30 animate-pulse"
                          : "bg-red-500/20 text-red-300 border border-red-500/30"
                      }`}
                    >
                      {doc.status}
                    </span>
                  </div>

                  {/* Document Attributes */}
                  <div className="grid grid-cols-3 gap-2 mt-4 text-center">
                    <div className="p-2 rounded-xl bg-[#100B18] border border-[#30203F]">
                      <span className="text-[10px] text-[#8B7C9E] block uppercase font-medium">Format</span>
                      <span className={`text-xs font-bold uppercase px-1.5 py-0.5 rounded border ${getFormatBadgeColor(doc.file_type)}`}>
                        {doc.file_type}
                      </span>
                    </div>
                    <div className="p-2 rounded-xl bg-[#100B18] border border-[#30203F]">
                      <span className="text-[10px] text-[#8B7C9E] block uppercase font-medium">Size</span>
                      <span className="text-xs font-bold text-white">{formatFileSize(doc.file_size)}</span>
                    </div>
                    <div className="p-2 rounded-xl bg-[#100B18] border border-[#30203F]">
                      <span className="text-[10px] text-[#C084FC] block uppercase font-medium">RAG Chunks</span>
                      <span className="text-xs font-bold text-white">{doc.chunk_count}</span>
                    </div>
                  </div>
                </div>

                {/* Action Buttons: Preview, AI Intelligence, Delete */}
                <div className="mt-5 pt-3.5 border-t border-[#291A3E] flex items-center justify-between flex-wrap gap-2">
                  <div className="flex items-center gap-2">
                    {/* Preview Button */}
                    <button
                      onClick={() => handleOpenPreview(doc)}
                      className="px-2.5 py-1.5 rounded-lg bg-[#181026] hover:bg-[#25153D] text-[#C084FC] hover:text-white border border-[#352150] text-xs font-medium flex items-center gap-1.5 transition-all"
                      title="Preview extracted pages and text chunks"
                    >
                      <Eye className="w-3.5 h-3.5" />
                      Preview
                    </button>

                    {/* AI Document Intelligence Button */}
                    <button
                      onClick={() => handleOpenIntel(doc, "summary")}
                      className="px-3 py-1.5 rounded-lg bg-gradient-to-r from-[#7C3AED]/30 to-[#9333EA]/30 hover:from-[#7C3AED]/50 hover:to-[#9333EA]/50 text-white border border-[#A855F7]/40 text-xs font-semibold flex items-center gap-1.5 shadow-sm transition-all"
                      title="Open AI Intelligence Suite (Summary, Notes, Exam Q&A, Definitions, Formulas)"
                    >
                      <Sparkles className="w-3.5 h-3.5 text-[#C084FC]" />
                      AI Intelligence
                    </button>
                  </div>

                  {/* Delete Button */}
                  <button
                    onClick={() => handleDelete(doc.id)}
                    className="p-1.5 text-xs text-[#8B7C9E] hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
                    title="Delete document"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>

                {/* Cross-Module Ecosystem Deep Links */}
                {doc.status === "ready" && (
                  <div className="flex items-center gap-1.5 w-full mt-3 pt-2.5 border-t border-[#291A3E]/80">
                    <Link
                      href={`/dashboard/assistant?document_id=${doc.id}`}
                      className="flex-1 py-1 px-2 rounded-lg bg-[#181026] hover:bg-[#25153D] text-[#C084FC] hover:text-white border border-[#352150] text-[10px] font-semibold flex items-center justify-center gap-1 transition-all"
                      title="Ask questions with citations from this document"
                    >
                      <Sparkles className="w-3 h-3 text-[#C084FC]" /> Ask AI
                    </Link>
                    <Link
                      href={`/dashboard/quiz?document_id=${doc.id}`}
                      className="flex-1 py-1 px-2 rounded-lg bg-[#181026] hover:bg-[#25153D] text-emerald-400 hover:text-white border border-[#352150] text-[10px] font-semibold flex items-center justify-center gap-1 transition-all"
                      title="Generate dynamic assessment from this document"
                    >
                      <CheckCircle2 className="w-3 h-3 text-emerald-400" /> Quiz
                    </Link>
                    <Link
                      href={`/dashboard/notes?document_id=${doc.id}`}
                      className="flex-1 py-1 px-2 rounded-lg bg-[#181026] hover:bg-[#25153D] text-[#A855F7] hover:text-white border border-[#352150] text-[10px] font-semibold flex items-center justify-center gap-1 transition-all"
                      title="Generate structured study notes from this document"
                    >
                      <BookOpen className="w-3 h-3 text-[#A855F7]" /> Notes
                    </Link>
                  </div>
                )}
              </GlowCard>
            ))}
          </div>
        )}
      </div>

      {/* 4. Document Preview Modal */}
      {previewDoc && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#120B1F] border border-[#3B2654] rounded-2xl max-w-2xl w-full p-6 shadow-2xl relative max-h-[90vh] flex flex-col">
            <div className="flex items-center justify-between pb-4 border-b border-[#291A3E]">
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-xl bg-purple-500/20 border border-purple-500/30 flex items-center justify-center">
                  <Eye className="w-4 h-4 text-[#C084FC]" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-white truncate max-w-md">{previewDoc.title}</h3>
                  <p className="text-[11px] text-[#8B7C9E]">
                    {previewDoc.file_name} • {previewDoc.total_pages} Page(s) • {previewDoc.total_chunks} Chunks
                  </p>
                </div>
              </div>
              <button
                onClick={() => setPreviewDoc(null)}
                className="text-[#8B7C9E] hover:text-white p-1 rounded-lg hover:bg-[#201433]"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto py-4 space-y-3">
              <div className="grid grid-cols-3 gap-2 text-center text-xs">
                <div className="p-2.5 rounded-xl bg-[#0D0817] border border-[#261738]">
                  <span className="text-[10px] text-[#8B7C9E] block uppercase">Format</span>
                  <span className="font-bold text-white uppercase">{previewDoc.file_type}</span>
                </div>
                <div className="p-2.5 rounded-xl bg-[#0D0817] border border-[#261738]">
                  <span className="text-[10px] text-[#8B7C9E] block uppercase">Total Words</span>
                  <span className="font-bold text-white">{previewDoc.total_words}</span>
                </div>
                <div className="p-2.5 rounded-xl bg-[#0D0817] border border-[#261738]">
                  <span className="text-[10px] text-[#C084FC] block uppercase">Status</span>
                  <span className="font-bold text-emerald-400 uppercase">{previewDoc.status}</span>
                </div>
              </div>

              <h4 className="text-xs font-bold uppercase tracking-wider text-[#C084FC] pt-2">
                Extracted Structural Chunks ({previewDoc.sample_chunks?.length || 0}):
              </h4>

              {previewDoc.sample_chunks?.length === 0 ? (
                <div className="p-4 text-center text-xs text-[#8B7C9E]">
                  No chunk preview available. Document may still be processing.
                </div>
              ) : (
                previewDoc.sample_chunks?.map((chunk: any, idx: number) => (
                  <div
                    key={idx}
                    className="p-3.5 rounded-xl bg-[#0C0816] border border-[#2A1A3D] text-xs text-[#A79BB8] space-y-1.5"
                  >
                    <div className="flex items-center justify-between text-[11px] font-semibold text-white">
                      <span className="text-[#C084FC]">Chunk #{chunk.chunk_index + 1}</span>
                      <span className="text-[10px] bg-[#221338] px-2 py-0.5 rounded text-[#D8B4FE]">
                        Page {chunk.page_number} • {chunk.word_count} words
                      </span>
                    </div>
                    <p className="text-[11px] leading-relaxed italic text-[#CFC2DF]">
                      &ldquo;{chunk.content_preview}&rdquo;
                    </p>
                  </div>
                ))
              )}
            </div>

            <div className="pt-4 border-t border-[#291A3E] flex justify-end">
              <button
                onClick={() => setPreviewDoc(null)}
                className="px-4 py-2 rounded-xl bg-[#1B112B] hover:bg-[#281840] text-xs font-medium text-white transition-colors"
              >
                Close Preview
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 5. Comprehensive AI Document Intelligence Modal */}
      {activeIntelDoc && (
        <div className="fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-3 sm:p-6">
          <div className="bg-[#0E0A17] border border-[#3B2654] rounded-2xl max-w-4xl w-full h-[90vh] shadow-2xl relative flex flex-col overflow-hidden">
            {/* Modal Header */}
            <div className="p-4 border-b border-[#261738] bg-[#140E21] flex items-center justify-between shrink-0">
              <div className="flex items-center gap-3 min-w-0">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-[#7C3AED] to-[#A855F7] flex items-center justify-center shrink-0 shadow-[0_0_15px_rgba(168,85,247,0.35)]">
                  <Brain className="w-5 h-5 text-white" />
                </div>
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <h3 className="text-sm sm:text-base font-bold text-white truncate max-w-sm sm:max-w-md">
                      {activeIntelDoc.title}
                    </h3>
                    <span className="text-[10px] uppercase font-mono px-1.5 py-0.2 rounded border bg-[#201235] text-[#C084FC] border-[#44236B]">
                      {activeIntelDoc.file_type}
                    </span>
                  </div>
                  <p className="text-[11px] text-[#8B7C9E] truncate">
                    AI-Powered Document Intelligence • Grounded strictly in extracted excerpts
                  </p>
                </div>
              </div>

              <button
                onClick={() => setActiveIntelDoc(null)}
                className="p-1.5 rounded-lg text-[#8B7C9E] hover:text-white hover:bg-[#201433] transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Navigation Tabs (9 AI Capabilities) */}
            <div className="px-3 pt-2 bg-[#120B1F] border-b border-[#261738] flex items-center gap-1.5 overflow-x-auto shrink-0 scrollbar-thin">
              {[
                { id: "summary", label: "Summary", icon: <FileText className="w-3.5 h-3.5" /> },
                { id: "notes", label: "Study Notes", icon: <BookOpen className="w-3.5 h-3.5" /> },
                { id: "exam", label: "Exam Answers", icon: <Award className="w-3.5 h-3.5" /> },
                { id: "qa", label: "Document Q&A", icon: <HelpCircle className="w-3.5 h-3.5" /> },
                { id: "quiz", label: "Self-Assessment", icon: <FileCheck className="w-3.5 h-3.5" /> },
                { id: "formulas", label: "Definitions & Formulas", icon: <Bookmark className="w-3.5 h-3.5" /> },
                { id: "topics", label: "Important Topics", icon: <ListFilter className="w-3.5 h-3.5" /> },
                { id: "revision", label: "Revision Kit", icon: <Layers className="w-3.5 h-3.5" /> },
                { id: "explain", label: "Explain Topic", icon: <Brain className="w-3.5 h-3.5" /> },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => {
                    setActiveTab(tab.id as any);
                    if (tab.id !== "qa" && tab.id !== "explain") {
                      loadTabContent(activeIntelDoc.id, tab.id);
                    }
                  }}
                  className={`px-3 py-2 rounded-t-xl text-xs font-semibold flex items-center gap-1.5 whitespace-nowrap transition-all border-b-2 ${
                    activeTab === tab.id
                      ? "bg-[#1E142E] text-white border-[#A855F7] shadow-sm"
                      : "text-[#8B7C9E] hover:text-[#C084FC] hover:bg-[#180F26] border-transparent"
                  }`}
                >
                  {tab.icon}
                  <span>{tab.label}</span>
                </button>
              ))}
            </div>

            {/* Tab Content Body */}
            <div className="flex-1 overflow-y-auto p-4 sm:p-6 bg-[#08060D] space-y-4">
              {/* Loading Indicator */}
              {intelLoading && (
                <div className="py-16 flex flex-col items-center justify-center space-y-3">
                  <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-[#7C3AED] to-[#A855F7] flex items-center justify-center animate-spin">
                    <RotateCw className="w-5 h-5 text-white" />
                  </div>
                  <p className="text-xs text-[#C084FC] animate-pulse">
                    Synthesizing knowledge from &ldquo;{activeIntelDoc.title}&rdquo;...
                  </p>
                </div>
              )}

              {/* 1. Executive Summary Tab */}
              {!intelLoading && activeTab === "summary" && intelData && (
                <div className="space-y-4 max-w-3xl mx-auto">
                  <div className="p-5 rounded-2xl bg-[#120B1F] border border-[#2F1D45] shadow-lg">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-[#C084FC] mb-2 flex items-center gap-1.5">
                      <Sparkles className="w-4 h-4 text-[#A855F7]" /> Executive Summary
                    </h4>
                    <p className="text-xs sm:text-sm text-[#D8B4FE] leading-relaxed">
                      {intelData.executive_summary}
                    </p>
                  </div>

                  {intelData.key_takeaways && (
                    <div className="p-5 rounded-2xl bg-[#120B1F] border border-[#2F1D45] space-y-3">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-[#A855F7]">
                        Key Takeaways ({intelData.key_takeaways.length})
                      </h4>
                      <ul className="space-y-2">
                        {intelData.key_takeaways.map((point: string, i: number) => (
                          <li key={i} className="flex items-start gap-2.5 text-xs text-[#E2D4F0] leading-relaxed">
                            <span className="w-1.5 h-1.5 rounded-full bg-[#A855F7] mt-1.5 shrink-0" />
                            <span>{point}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {intelData.recommended_focus_areas && (
                    <div className="p-4 rounded-xl bg-[#170E28] border border-[#3E255C] text-xs text-[#C084FC] space-y-1.5">
                      <span className="font-bold uppercase tracking-wider text-[11px] block">
                        Recommended Focus Areas:
                      </span>
                      <div className="flex flex-wrap gap-2 pt-1">
                        {intelData.recommended_focus_areas.map((area: string, idx: number) => (
                          <span
                            key={idx}
                            className="px-2.5 py-1 rounded-lg bg-[#24133D] border border-[#4D2878] text-white text-[11px]"
                          >
                            {area}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* 2. Study Notes Tab */}
              {!intelLoading && activeTab === "notes" && intelData && (
                <div className="space-y-4 max-w-3xl mx-auto">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-[#C084FC]">
                      Module-by-Module Study Notes
                    </h4>
                    <span className="text-[11px] text-[#8B7C9E]">
                      {intelData.modules?.length || 0} Modules Extracted
                    </span>
                  </div>

                  {intelData.modules?.map((mod: any, idx: number) => (
                    <div key={idx} className="p-5 rounded-2xl bg-[#120B1F] border border-[#2F1D45] space-y-3">
                      <div className="flex items-center justify-between">
                        <h5 className="text-sm font-bold text-white flex items-center gap-2">
                          <span className="w-6 h-6 rounded-lg bg-[#7C3AED]/30 text-[#C084FC] flex items-center justify-center text-xs">
                            {idx + 1}
                          </span>
                          {mod.module_title}
                        </h5>
                        {mod.page_reference && (
                          <span className="text-[10px] font-mono bg-[#221338] px-2 py-0.5 rounded text-[#D8B4FE]">
                            {mod.page_reference}
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-[#9D8EB0] italic">{mod.summary}</p>
                      <ul className="space-y-1.5 pt-1">
                        {mod.key_points?.map((pt: string, pIdx: number) => (
                          <li key={pIdx} className="flex items-start gap-2 text-xs text-[#E2D4F0]">
                            <ChevronRight className="w-3.5 h-3.5 text-[#A855F7] shrink-0 mt-0.5" />
                            <span>{pt}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}

                  {intelData.core_definitions?.length > 0 && (
                    <div className="p-5 rounded-2xl bg-[#120B1F] border border-[#2F1D45] space-y-3">
                      <h5 className="text-xs font-bold uppercase tracking-wider text-[#A855F7]">
                        Core Module Definitions
                      </h5>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        {intelData.core_definitions.map((def: any, dIdx: number) => (
                          <div key={dIdx} className="p-3 rounded-xl bg-[#0D0818] border border-[#29173E] text-xs">
                            <div className="font-bold text-white mb-1 flex items-center justify-between">
                              <span>{def.term}</span>
                              <span className="text-[10px] text-[#A855F7]">{def.page}</span>
                            </div>
                            <p className="text-[11px] text-[#9D8EB0]">{def.definition}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* 3. Exam Answers Tab */}
              {!intelLoading && activeTab === "exam" && intelData && (
                <div className="space-y-4 max-w-3xl mx-auto">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-[#C084FC]">
                      Exam-Oriented Questions & Model Answers
                    </h4>
                    <span className="text-[11px] text-[#8B7C9E]">High-Yield Semester Preparation</span>
                  </div>

                  {intelData.exam_questions?.map((q: any, idx: number) => (
                    <div key={idx} className="p-5 rounded-2xl bg-[#120B1F] border border-[#2F1D45] space-y-3">
                      <div className="flex items-start justify-between gap-3">
                        <h5 className="text-xs sm:text-sm font-bold text-white flex items-start gap-2">
                          <span className="text-[#C084FC] shrink-0">Q{idx + 1}.</span>
                          <span>{q.question}</span>
                        </h5>
                        <div className="flex items-center gap-1.5 shrink-0">
                          <span className="text-[10px] font-bold bg-[#2C1645] border border-[#522982] text-[#E9D5FF] px-2 py-0.5 rounded">
                            {q.marks} Marks
                          </span>
                          {q.page_reference && (
                            <span className="text-[10px] font-mono bg-[#1E1130] text-[#A79BB8] px-1.5 py-0.5 rounded">
                              {q.page_reference}
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Scoring Criteria */}
                      {q.scoring_criteria && (
                        <div className="p-3 rounded-xl bg-[#160D25] border border-[#301B4B] text-[11px] space-y-1">
                          <span className="font-semibold text-[#A855F7] block text-[10px] uppercase">
                            Scoring Rubric:
                          </span>
                          <ul className="space-y-0.5 text-[#C8BCDA]">
                            {q.scoring_criteria.map((sc: string, scIdx: number) => (
                              <li key={scIdx}>• {sc}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Model Answer */}
                      <div className="pt-2">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-400 block mb-1">
                          Model Answer:
                        </span>
                        <div className="text-xs text-[#E9DCF8] leading-relaxed bg-[#0D0717] p-3.5 rounded-xl border border-[#26153B]">
                          <AssistantMarkdown content={q.model_answer} />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* 4. Interactive Document Q&A Tab */}
              {activeTab === "qa" && (
                <div className="space-y-4 max-w-3xl mx-auto flex flex-col h-full">
                  <div className="p-4 rounded-xl bg-[#120B1F] border border-[#2F1D45] flex items-center justify-between text-xs text-[#A79BB8]">
                    <div className="flex items-center gap-2">
                      <Sparkles className="w-4 h-4 text-[#A855F7]" />
                      <span>
                        Ask any question about <strong>{activeIntelDoc.title}</strong>. Answers are grounded in document excerpts with page citations.
                      </span>
                    </div>
                  </div>

                  {/* Q&A Feed */}
                  <div className="space-y-4 min-h-[220px]">
                    {qaHistory.length === 0 ? (
                      <div className="p-10 text-center text-xs text-[#8B7C9E] space-y-2">
                        <HelpCircle className="w-8 h-8 text-[#A855F7]/40 mx-auto" />
                        <p>No questions asked yet for this document.</p>
                        <p className="text-[11px] text-[#716485]">
                          Try asking: &ldquo;What are the main findings?&rdquo; or &ldquo;Explain the formula on page 2.&rdquo;
                        </p>
                      </div>
                    ) : (
                      qaHistory.map((item, idx) => (
                        <div key={idx} className="space-y-2.5">
                          {/* User Question */}
                          <div className="flex justify-end">
                            <div className="max-w-[80%] rounded-2xl rounded-tr-sm bg-gradient-to-r from-[#7C3AED] to-[#9333EA] text-white p-3 text-xs">
                              {item.question}
                            </div>
                          </div>

                          {/* Grounded Assistant Answer */}
                          <div className="flex justify-start">
                            <div className="max-w-[90%] rounded-2xl rounded-tl-sm bg-[#120B1F] border border-[#2F1D45] p-4 text-xs text-white space-y-2.5">
                              <AssistantMarkdown content={item.answer} />

                              {/* Grounding Notice if not in document */}
                              {!item.found_in_document && (
                                <div className="text-[11px] text-amber-400 bg-amber-500/10 p-2 rounded-lg border border-amber-500/20">
                                  Notice: This question could not be verified in the uploaded document.
                                </div>
                              )}

                              {/* Document Citations */}
                              {item.citations && item.citations.length > 0 && (
                                <div className="pt-2 border-t border-[#25153D]">
                                  <span className="text-[10px] font-bold uppercase text-[#C084FC] block mb-1.5">
                                    Document Page References:
                                  </span>
                                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
                                    {item.citations.map((c, cIdx) => (
                                      <div
                                        key={cIdx}
                                        className="p-2 rounded-lg bg-[#0D0717] border border-[#27163B] text-[10px] text-[#A79BB8]"
                                      >
                                        <div className="flex items-center justify-between text-white font-medium mb-0.5">
                                          <span className="truncate">{c.doc_title}</span>
                                          <span className="text-[#A855F7] font-mono">Page {c.page_number}</span>
                                        </div>
                                        <p className="italic line-clamp-2">&ldquo;{c.snippet}&rdquo;</p>
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      ))
                    )}

                    {qaLoading && (
                      <div className="flex items-center gap-2 p-3 text-xs text-[#C084FC]">
                        <RotateCw className="w-4 h-4 animate-spin" />
                        <span>Searching document chunks and formulating grounded answer...</span>
                      </div>
                    )}
                  </div>

                  {/* Ask Form */}
                  <form onSubmit={handleSendQa} className="pt-2 sticky bottom-0 bg-[#08060D]">
                    <div className="flex items-center gap-2 bg-[#120B1F] border border-[#362152] focus-within:border-[#A855F7] rounded-xl p-2">
                      <input
                        type="text"
                        value={qaInput}
                        onChange={(e) => setQaInput(e.target.value)}
                        placeholder="Ask a question about this document..."
                        className="flex-1 bg-transparent border-0 text-xs text-white placeholder-[#716485] focus:outline-none px-2"
                      />
                      <button
                        type="submit"
                        disabled={qaLoading || !qaInput.trim()}
                        className="p-2 rounded-lg bg-[#7C3AED] hover:bg-[#6D28D9] text-white disabled:opacity-40 transition-colors"
                      >
                        <Send className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </form>
                </div>
              )}

              {/* 5. Self-Assessment Quiz & MCQs Tab */}
              {!intelLoading && activeTab === "quiz" && intelData && (
                <div className="space-y-4 max-w-3xl mx-auto">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-[#C084FC]">
                      Document Self-Assessment & Practice Questions
                    </h4>
                    <span className="text-[11px] text-[#8B7C9E]">
                      {Array.isArray(intelData) ? intelData.length : 0} Questions Generated
                    </span>
                  </div>

                  {Array.isArray(intelData) &&
                    intelData.map((q: any, idx: number) => (
                      <div key={idx} className="p-5 rounded-2xl bg-[#120B1F] border border-[#2F1D45] space-y-3">
                        <div className="flex items-start justify-between gap-3">
                          <h5 className="text-xs sm:text-sm font-bold text-white flex items-start gap-2">
                            <span className="text-[#C084FC]">Q{idx + 1}.</span>
                            <span>{q.question_text || q.question}</span>
                          </h5>
                          <span className="text-[10px] uppercase font-mono bg-[#281540] text-[#D8B4FE] px-2 py-0.5 rounded">
                            {q.question_type || "MCQ"}
                          </span>
                        </div>

                        {/* MCQ Options (if available) */}
                        {q.options && q.options.length > 0 && (
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1">
                            {q.options.map((opt: string, optIdx: number) => (
                              <div
                                key={optIdx}
                                className={`p-2.5 rounded-xl border text-xs ${
                                  optIdx === q.correct_option_index
                                    ? "bg-emerald-500/10 border-emerald-500/40 text-emerald-300 font-medium"
                                    : "bg-[#0D0717] border-[#29173E] text-[#B8A9CC]"
                                }`}
                              >
                                <span className="font-semibold mr-1.5">{String.fromCharCode(65 + optIdx)}.</span>
                                {opt}
                              </div>
                            ))}
                          </div>
                        )}

                        {/* Explanation */}
                        <div className="p-3 rounded-xl bg-[#0D0717] border border-[#25153A] text-xs text-[#C8BCDA]">
                          <span className="text-[10px] font-bold uppercase text-[#A855F7] block mb-0.5">
                            Explanation:
                          </span>
                          {q.explanation}
                        </div>
                      </div>
                    ))}
                </div>
              )}

              {/* 6. Definitions & Formulas Tab */}
              {!intelLoading && activeTab === "formulas" && intelData && (
                <div className="space-y-4 max-w-3xl mx-auto">
                  {/* Formulas */}
                  {intelData.formulas?.length > 0 && (
                    <div className="space-y-3">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-[#C084FC] flex items-center gap-1.5">
                        <Bookmark className="w-4 h-4 text-[#A855F7]" /> Mathematical & Scientific Formulas
                      </h4>
                      <div className="grid grid-cols-1 gap-3">
                        {intelData.formulas.map((item: any, idx: number) => (
                          <div key={idx} className="p-4 rounded-2xl bg-[#120B1F] border border-[#2F1D45] space-y-2">
                            <div className="flex items-center justify-between">
                              <span className="text-[10px] font-bold text-[#A855F7] uppercase tracking-wider">
                                Formula #{idx + 1}
                              </span>
                              <span className="text-[10px] font-mono bg-[#211236] text-[#D8B4FE] px-2 py-0.5 rounded">
                                {item.page}
                              </span>
                            </div>
                            <div className="py-2 px-3 rounded-xl bg-[#0D0717] border border-[#27163B] text-center overflow-x-auto">
                              <AssistantMarkdown content={item.formula} />
                            </div>
                            <p className="text-xs text-[#A79BB8]">{item.description}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Definitions */}
                  {intelData.definitions?.length > 0 && (
                    <div className="space-y-3 pt-2">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-[#A855F7]">
                        Technical Definitions & Terminology
                      </h4>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        {intelData.definitions.map((def: any, idx: number) => (
                          <div key={idx} className="p-3.5 rounded-xl bg-[#120B1F] border border-[#2F1D45] text-xs space-y-1">
                            <div className="flex items-center justify-between font-bold text-white">
                              <span>{def.term}</span>
                              <span className="text-[10px] text-[#A855F7]">{def.page}</span>
                            </div>
                            <p className="text-[11px] text-[#A79BB8] leading-relaxed">{def.definition}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* 7. Important Topics Tab */}
              {!intelLoading && activeTab === "topics" && intelData && (
                <div className="space-y-4 max-w-3xl mx-auto">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-[#C084FC]">
                      Identified Core Topics & Exam Weightage
                    </h4>
                    <span className="text-[11px] text-[#8B7C9E]">High-Yield Syllabus Mapping</span>
                  </div>

                  <div className="grid grid-cols-1 gap-3">
                    {Array.isArray(intelData) &&
                      intelData.map((t: any, idx: number) => (
                        <div key={idx} className="p-4 rounded-2xl bg-[#120B1F] border border-[#2F1D45] space-y-2">
                          <div className="flex items-center justify-between flex-wrap gap-2">
                            <h5 className="text-xs sm:text-sm font-bold text-white flex items-center gap-2">
                              <span className="w-6 h-6 rounded-lg bg-[#7C3AED]/30 text-[#C084FC] flex items-center justify-center text-xs">
                                {idx + 1}
                              </span>
                              {t.topic}
                            </h5>
                            <div className="flex items-center gap-1.5">
                              <span
                                className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider ${
                                  t.importance === "Core"
                                    ? "bg-purple-500/20 text-purple-300 border border-purple-500/30"
                                    : "bg-blue-500/20 text-blue-300 border border-blue-500/30"
                                }`}
                              >
                                {t.importance}
                              </span>
                              <span className="text-[10px] font-mono bg-[#281540] text-[#E9D5FF] px-2 py-0.5 rounded">
                                Weightage: {t.exam_weightage}
                              </span>
                            </div>
                          </div>
                          <p className="text-xs text-[#C8BCDA] leading-relaxed">{t.summary}</p>
                          {t.pages && (
                            <div className="text-[10px] text-[#8B7C9E]">
                              Referenced Pages: {Array.isArray(t.pages) ? t.pages.join(", ") : t.pages}
                            </div>
                          )}
                        </div>
                      ))}
                  </div>
                </div>
              )}

              {/* 8. Revision Kit Tab */}
              {!intelLoading && activeTab === "revision" && intelData && (
                <div className="space-y-4 max-w-3xl mx-auto">
                  {/* Quick Cheat Sheet */}
                  {intelData.cheat_sheet?.length > 0 && (
                    <div className="p-5 rounded-2xl bg-[#120B1F] border border-[#2F1D45] space-y-3">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-[#C084FC] flex items-center gap-1.5">
                        <Layers className="w-4 h-4 text-[#A855F7]" /> 5-Minute Exam Cheat Sheet
                      </h4>
                      <ul className="space-y-2">
                        {intelData.cheat_sheet.map((pt: string, idx: number) => (
                          <li key={idx} className="flex items-start gap-2.5 text-xs text-[#E2D4F0]">
                            <Check className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                            <span>{pt}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Flashcards */}
                  {intelData.flashcards?.length > 0 && (
                    <div className="space-y-3">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-[#A855F7]">
                        Active Recall Flashcards ({intelData.flashcards.length})
                      </h4>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        {intelData.flashcards.map((fc: any, idx: number) => (
                          <div key={idx} className="p-4 rounded-xl bg-[#120B1F] border border-[#2F1D45] space-y-2 flex flex-col justify-between">
                            <div>
                              <div className="flex items-center justify-between text-[10px] text-[#A855F7] mb-1 font-semibold uppercase">
                                <span>Question</span>
                                <span>{fc.page}</span>
                              </div>
                              <p className="text-xs font-bold text-white mb-2">{fc.question}</p>
                            </div>
                            <div className="p-2.5 rounded-lg bg-[#0C0716] border border-[#25153A] text-xs text-[#C8BCDA]">
                              <span className="text-[10px] font-bold text-emerald-400 block mb-0.5">Answer:</span>
                              {fc.answer}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Pitfalls to Avoid */}
                  {intelData.pitfalls_to_avoid?.length > 0 && (
                    <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-xs text-amber-200 space-y-1.5">
                      <span className="font-bold uppercase tracking-wider text-[11px] flex items-center gap-1.5">
                        <AlertCircle className="w-3.5 h-3.5 text-amber-400" /> Common Examination Pitfalls to Avoid:
                      </span>
                      <ul className="space-y-1 text-[11px] pt-1">
                        {intelData.pitfalls_to_avoid.map((pf: string, pIdx: number) => (
                          <li key={pIdx}>• {pf}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* 9. Explain Difficult Topic Tab */}
              {activeTab === "explain" && (
                <div className="space-y-4 max-w-3xl mx-auto">
                  <div className="p-4 rounded-xl bg-[#120B1F] border border-[#2F1D45] text-xs text-[#A79BB8] space-y-2">
                    <span className="font-semibold text-white block">
                      Explain Any Difficult Concept in &ldquo;{activeIntelDoc.title}&rdquo;
                    </span>
                    <p className="text-[11px]">
                      Enter a topic or theorem mentioned in this document. The AI will provide a first-principles breakdown, step-by-step mechanism, and cited excerpts.
                    </p>
                  </div>

                  <form onSubmit={handleExplainTopic} className="flex gap-2">
                    <input
                      type="text"
                      value={topicToExplain}
                      onChange={(e) => setTopicToExplain(e.target.value)}
                      placeholder="e.g. Transaction Isolation Levels, B-Tree Balancing, Amdahl's Law..."
                      className="flex-1 px-3.5 py-2.5 rounded-xl bg-[#120B1F] border border-[#352150] text-xs text-white placeholder-[#716485] focus:outline-none focus:border-[#A855F7]"
                    />
                    <button
                      type="submit"
                      disabled={explainLoading || !topicToExplain.trim()}
                      className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-[#7C3AED] to-[#9333EA] hover:from-[#6D28D9] hover:to-[#7E22CE] text-white text-xs font-bold disabled:opacity-40 transition-all flex items-center gap-1.5"
                    >
                      <Brain className="w-3.5 h-3.5" />
                      {explainLoading ? "Deconstructing..." : "Explain"}
                    </button>
                  </form>

                  {explainLoading && (
                    <div className="py-10 text-center text-xs text-[#C084FC] flex items-center justify-center gap-2">
                      <RotateCw className="w-4 h-4 animate-spin" />
                      <span>Formulating first-principles conceptual breakdown...</span>
                    </div>
                  )}

                  {explainResult && (
                    <div className="p-5 rounded-2xl bg-[#120B1F] border border-[#2F1D45] space-y-3">
                      <div className="flex items-center justify-between border-b border-[#25153D] pb-3">
                        <h4 className="text-sm font-bold text-white flex items-center gap-2">
                          <Sparkles className="w-4 h-4 text-[#C084FC]" />
                          <span>Topic: {explainResult.topic}</span>
                        </h4>
                        <span className="text-[10px] text-[#A855F7] font-mono">Grounded Breakdown</span>
                      </div>

                      <div className="text-xs text-[#E9DCF8] leading-relaxed">
                        <AssistantMarkdown content={explainResult.explanation} />
                      </div>

                      {explainResult.citations && explainResult.citations.length > 0 && (
                        <div className="pt-3 border-t border-[#25153D]">
                          <span className="text-[10px] font-bold uppercase text-[#C084FC] block mb-1">
                            Page Citations:
                          </span>
                          <div className="flex flex-wrap gap-1.5">
                            {explainResult.citations.map((c: any, cIdx: number) => (
                              <span
                                key={cIdx}
                                className="px-2 py-0.5 rounded bg-[#201235] border border-[#3E2365] text-[10px] text-[#D8B4FE]"
                              >
                                {c.doc_title} (Page {c.page_number})
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="p-3 bg-[#120B1F] border-t border-[#261738] flex items-center justify-between text-[11px] text-[#716485] shrink-0">
              <span>Grounded in {activeIntelDoc.chunk_count} document chunks with verified citations</span>
              <button
                onClick={() => setActiveIntelDoc(null)}
                className="px-3.5 py-1.5 rounded-lg bg-[#1D132D] hover:bg-[#2B1B43] text-xs text-white transition-colors"
              >
                Close Suite
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
