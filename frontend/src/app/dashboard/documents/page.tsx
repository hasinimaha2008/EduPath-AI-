"use client";

import React, { useState, useEffect } from "react";
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
  Sparkles
} from "lucide-react";
import { GlowCard } from "@/components/GlowCard";
import { api } from "@/lib/api";
import { DocumentItem, Subject } from "@/lib/types";

export default function DocumentManagementPage() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [loading, setLoading] = useState(true);

  // Upload Form State
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [selectedSubjectId, setSelectedSubjectId] = useState("");
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);

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

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      setFile(selected);
      if (!title) {
        setTitle(selected.name.replace(/\.[^/.]+$/, ""));
      }
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    setUploadError(null);
    setUploadSuccess(null);

    try {
      const newDoc = await api.uploadDocument(
        file,
        title.trim() || undefined,
        selectedSubjectId || undefined
      );

      setDocuments((prev) => [newDoc, ...prev]);
      setUploadSuccess(`"${newDoc.title}" successfully processed and indexed for RAG!`);
      setFile(null);
      setTitle("");
      setSelectedSubjectId("");
    } catch (err: any) {
      setUploadError(err.message || "Failed to process document.");
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (docId: string) => {
    try {
      await api.deleteDocument(docId);
      setDocuments((prev) => prev.filter((d) => d.id !== docId));
    } catch (e) {
      console.error("Error deleting document:", e);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <UploadCloud className="w-5 h-5 text-[#C084FC]" /> Document Upload & Knowledge Extraction
        </h1>
        <p className="text-xs text-[#A1A1AA] mt-0.5">
          Securely upload PDF or Word documents. Texts are extracted, chunked, and vector-indexed for Retrieval-Augmented Generation (RAG).
        </p>
      </div>

      {/* Upload Box */}
      <GlowCard glow className="p-6">
        <h2 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-[#A855F7]" /> Upload Academic Document (PDF or DOCX)
        </h2>

        {uploadError && (
          <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-xs text-red-400 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{uploadError}</span>
          </div>
        )}

        {uploadSuccess && (
          <div className="mb-4 p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-xs text-emerald-400 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 shrink-0" />
            <span>{uploadSuccess}</span>
          </div>
        )}

        <form onSubmit={handleUpload} className="space-y-4">
          <div className="border-2 border-dashed border-[#30203F] hover:border-[#A855F7] rounded-xl p-8 text-center transition-all bg-[#100B18]/50">
            <input
              type="file"
              id="file-upload"
              accept=".pdf,.docx"
              onChange={handleFileChange}
              className="hidden"
            />
            <label htmlFor="file-upload" className="cursor-pointer block">
              <UploadCloud className="w-10 h-10 text-[#C084FC] mx-auto mb-2" />
              <span className="text-sm font-bold text-white block">
                {file ? file.name : "Click to select or drag and drop document"}
              </span>
              <span className="text-xs text-[#A1A1AA] mt-1 block">
                Supported formats: PDF (.pdf) and DOCX (.docx) • Max size: 25MB
              </span>
            </label>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-[11px] font-semibold text-[#A1A1AA] uppercase tracking-wider mb-1.5">
                Document Title
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. DBMS Lecture Notes – Normalization"
                className="w-full px-3 py-2 rounded-lg bg-[#100B18] border border-[#30203F] text-xs text-white focus:outline-none focus:border-[#A855F7]"
              />
            </div>

            <div>
              <label className="block text-[11px] font-semibold text-[#A1A1AA] uppercase tracking-wider mb-1.5">
                Associate with Subject (Optional)
              </label>
              <select
                value={selectedSubjectId}
                onChange={(e) => setSelectedSubjectId(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-[#100B18] border border-[#30203F] text-xs text-white focus:outline-none focus:border-[#A855F7]"
              >
                <option value="">General Curriculum</option>
                {subjects.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name} ({s.code})
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex justify-end pt-2">
            <button
              type="submit"
              disabled={uploading || !file}
              className="px-6 py-2.5 rounded-lg text-xs font-bold bg-gradient-to-r from-[#8B5CF6] to-[#A855F7] text-white shadow-[0_0_15px_rgba(168,85,247,0.35)] hover:shadow-[0_0_20px_rgba(168,85,247,0.6)] disabled:opacity-50 transition-all flex items-center gap-2"
            >
              <UploadCloud className="w-4 h-4" />
              {uploading ? "Extracting & Vectorizing..." : "Upload & Prepare for RAG"}
            </button>
          </div>
        </form>
      </GlowCard>

      {/* Uploaded Documents List */}
      <div className="space-y-4">
        <h2 className="text-base font-bold text-white flex items-center gap-2">
          <BookOpen className="w-4 h-4 text-[#A855F7]" /> Managed Documents ({documents.length})
        </h2>

        {documents.length === 0 ? (
          <GlowCard className="p-8 text-center text-xs text-[#A1A1AA]">
            No documents uploaded yet. Upload lecture notes or textbooks above to activate cited RAG question answering.
          </GlowCard>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {documents.map((doc) => (
              <GlowCard key={doc.id} className="p-5 flex flex-col justify-between">
                <div>
                  <div className="flex items-start justify-between gap-3 mb-2">
                    <div className="flex items-start gap-3 min-w-0">
                      <div className="w-9 h-9 rounded-lg bg-purple-500/20 border border-purple-500/30 flex items-center justify-center shrink-0">
                        <FileText className="w-5 h-5 text-[#C084FC]" />
                      </div>
                      <div className="min-w-0">
                        <h3 className="text-sm font-bold text-white truncate">{doc.title}</h3>
                        <p className="text-[11px] text-[#A1A1AA] truncate">{doc.file_name}</p>
                      </div>
                    </div>

                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider shrink-0 ${
                        doc.status === "ready"
                          ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                          : doc.status === "processing"
                          ? "bg-amber-500/20 text-amber-300 border border-amber-500/30"
                          : "bg-red-500/20 text-red-300 border border-red-500/30"
                      }`}
                    >
                      {doc.status}
                    </span>
                  </div>

                  <div className="grid grid-cols-3 gap-2 mt-4 text-center">
                    <div className="p-2 rounded bg-[#100B18] border border-[#30203F]">
                      <span className="text-[10px] text-[#A1A1AA] block uppercase">Format</span>
                      <span className="text-xs font-bold text-white uppercase">{doc.file_type}</span>
                    </div>
                    <div className="p-2 rounded bg-[#100B18] border border-[#30203F]">
                      <span className="text-[10px] text-[#A1A1AA] block uppercase">Size</span>
                      <span className="text-xs font-bold text-white">{formatFileSize(doc.file_size)}</span>
                    </div>
                    <div className="p-2 rounded bg-[#100B18] border border-[#30203F]">
                      <span className="text-[10px] text-[#C084FC] block uppercase">RAG Chunks</span>
                      <span className="text-xs font-bold text-white">{doc.chunk_count}</span>
                    </div>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-[#30203F] flex items-center justify-between">
                  <span className="text-[10px] text-[#A1A1AA]">
                    {new Date(doc.created_at).toLocaleDateString()}
                  </span>
                  <div className="flex items-center gap-3">
                    <button
                      onClick={() => handleDelete(doc.id)}
                      className="text-xs text-red-400 hover:text-red-300 flex items-center gap-1 transition-colors"
                    >
                      <Trash2 className="w-3.5 h-3.5" /> Delete
                    </button>
                  </div>
                </div>
              </GlowCard>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
