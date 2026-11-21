"use client";

import React, { Suspense, useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  Layers,
  BookOpen,
  FileText,
  CheckCircle2,
  Calendar,
  Sparkles,
  ArrowRight,
  Brain,
  HelpCircle,
  Clock,
  Award,
  Zap,
  RotateCcw,
  UploadCloud,
  ChevronRight,
  Target
} from "lucide-react";
import { api } from "@/lib/api";
import { Subject, Topic, TopicWorkspaceData, ExplanationModeResponse } from "@/lib/types";

const EXPLANATION_MODES = [
  { id: "step_by_step", label: "Step-by-Step", desc: "Procedural breakdown & execution traces" },
  { id: "beginner", label: "Beginner", desc: "Everyday intuition & simple analogies" },
  { id: "intermediate", label: "Intermediate", desc: "Undergraduate curriculum standard" },
  { id: "advanced", label: "Advanced", desc: "System engineering, invariants & low-level trade-offs" },
  { id: "real_world", label: "Real-World", desc: "Enterprise production architecture & incidents" },
  { id: "exam_oriented", label: "Exam-Oriented", desc: "High-yield scoring rubrics & common pitfalls" }
];

function WorkspaceContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const topicIdParam = searchParams.get("topic_id");

  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [selectedSubjectId, setSelectedSubjectId] = useState<string>("");
  const [selectedTopicId, setSelectedTopicId] = useState<string>("");
  const [workspaceData, setWorkspaceData] = useState<TopicWorkspaceData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [activeTab, setActiveTab] = useState<"explainer" | "notes" | "documents" | "quizzes">("explainer");

  // Explainer State
  const [explanationMode, setExplanationMode] = useState<string>("step_by_step");
  const [conceptQuery, setConceptQuery] = useState<string>("");
  const [explaining, setExplaining] = useState<boolean>(false);
  const [explanationResult, setExplanationResult] = useState<ExplanationModeResponse | null>(null);

  // Initial Load: Fetch Subjects & Topics
  useEffect(() => {
    async function init() {
      try {
        setLoading(true);
        const subList = await api.getSubjects();
        setSubjects(subList);

        if (subList.length > 0) {
          // If topicId in URL, locate its subject
          let matchedSubId = subList[0].id;
          let matchedTopicId = subList[0].topics?.[0]?.id || "";

          if (topicIdParam) {
            for (const s of subList) {
              const foundTopic = s.topics?.find((t) => t.id === topicIdParam);
              if (foundTopic) {
                matchedSubId = s.id;
                matchedTopicId = foundTopic.id;
                break;
              }
            }
          }

          setSelectedSubjectId(matchedSubId);
          setSelectedTopicId(matchedTopicId);
          if (matchedTopicId) {
            await loadWorkspace(matchedTopicId);
          }
        }
      } catch (err) {
        console.error("Workspace init error", err);
      } finally {
        setLoading(false);
      }
    }
    init();
  }, [topicIdParam]);

  const loadWorkspace = async (topicId: string) => {
    try {
      const data = await api.getTopicWorkspace(topicId);
      setWorkspaceData(data);
      setConceptQuery(data.topic.name);
      setExplanationResult(null);
    } catch (err) {
      console.error("Failed to load workspace data", err);
    }
  };

  const handleSubjectChange = (newSubId: string) => {
    setSelectedSubjectId(newSubId);
    const sub = subjects.find((s) => s.id === newSubId);
    if (sub && sub.topics && sub.topics.length > 0) {
      const newTopicId = sub.topics[0].id;
      setSelectedTopicId(newTopicId);
      loadWorkspace(newTopicId);
    }
  };

  const handleTopicChange = (newTopicId: string) => {
    setSelectedTopicId(newTopicId);
    loadWorkspace(newTopicId);
  };

  const handleGenerateExplanation = async () => {
    if (!workspaceData) return;
    try {
      setExplaining(true);
      const res = await api.explainConcept({
        topic_name: workspaceData.topic.name,
        concept_name: conceptQuery.trim() || workspaceData.topic.name,
        mode: explanationMode,
        subject_name: workspaceData.topic.subject_name
      });
      setExplanationResult(res);
    } catch (err) {
      console.error("Explanation error", err);
    } finally {
      setExplaining(false);
    }
  };

  const currentSubject = subjects.find((s) => s.id === selectedSubjectId);
  const currentTopic = currentSubject?.topics?.find((t) => t.id === selectedTopicId);

  const getMasteryBadge = (status: string) => {
    switch (status) {
      case "mastered":
        return <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">Mastered (90%+)</span>;
      case "proficient":
        return <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-blue-500/20 text-blue-400 border border-blue-500/30">Proficient (75%+)</span>;
      case "developing":
        return <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-amber-500/20 text-amber-400 border border-amber-500/30">Developing (50-74%)</span>;
      default:
        return <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30">Needs Practice (&lt;50%)</span>;
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Header & Topic Selector */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-[#30203F] pb-6">
        <div>
          <div className="flex items-center gap-2.5">
            <div className="p-2.5 rounded-xl bg-purple-500/10 border border-purple-500/30 text-purple-400 shadow-[0_0_15px_rgba(168,85,247,0.25)]">
              <Layers className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
                Interactive Learning Workspace
                <span className="px-2 py-0.5 rounded-full bg-purple-500/20 text-[#C084FC] text-xs font-semibold">
                  Unified 2.0
                </span>
              </h1>
              <p className="text-sm text-[#A1A1AA] mt-0.5">
                Multi-subject exploration, 6-mode concept explanations, notes, quizzes, and spaced review.
              </p>
            </div>
          </div>
        </div>

        {/* Dynamic Selectors */}
        <div className="flex flex-wrap items-center gap-3">
          <select
            value={selectedSubjectId}
            onChange={(e) => handleSubjectChange(e.target.value)}
            className="px-3.5 py-2 rounded-xl bg-[#160F23] border border-[#30203F] text-xs font-semibold text-white focus:outline-none focus:border-[#8B5CF6]"
          >
            {subjects.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name} ({s.topics?.length || 0} topics)
              </option>
            ))}
          </select>

          <select
            value={selectedTopicId}
            onChange={(e) => handleTopicChange(e.target.value)}
            className="px-3.5 py-2 rounded-xl bg-[#160F23] border border-[#30203F] text-xs font-semibold text-white focus:outline-none focus:border-[#8B5CF6] max-w-[260px]"
          >
            {currentSubject?.topics?.map((t) => (
              <option key={t.id} value={t.id}>
                {t.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Main Workspace Layout */}
      {workspaceData && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left 2 Cols: Main Content Area */}
          <div className="lg:col-span-2 space-y-6">
            {/* Topic Overview Card */}
            <div className="p-6 rounded-2xl bg-[#160F23] border border-[#30203F] space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-semibold text-[#A855F7]">
                    {workspaceData.topic.subject_name} • {workspaceData.topic.module_name}
                  </span>
                  {workspaceData.topic.is_emerging && (
                    <span className="px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 text-[10px] font-bold border border-cyan-500/30">
                      Emerging Industry Tech
                    </span>
                  )}
                </div>
                {getMasteryBadge(workspaceData.performance.mastery_status)}
              </div>

              <h2 className="text-xl font-bold text-white tracking-tight">{workspaceData.topic.name}</h2>
              <p className="text-xs text-[#A1A1AA] leading-relaxed">{workspaceData.topic.description}</p>

              {/* Subtopics chips */}
              {workspaceData.topic.subtopics && workspaceData.topic.subtopics.length > 0 && (
                <div className="pt-2 border-t border-[#30203F]/60">
                  <span className="text-[11px] font-bold text-[#71717A] uppercase tracking-wider block mb-2">
                    Curriculum Subtopics
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {workspaceData.topic.subtopics.map((st, i) => (
                      <span
                        key={i}
                        onClick={() => {
                          setConceptQuery(st);
                          setActiveTab("explainer");
                        }}
                        className="px-2.5 py-1 rounded-lg bg-[#1F1533] hover:bg-[#2A1D45] text-white text-[11px] font-medium border border-[#382650] cursor-pointer transition-colors"
                      >
                        {st}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Tab Navigation */}
            <div className="flex items-center gap-2 border-b border-[#30203F] pb-1">
              <button
                onClick={() => setActiveTab("explainer")}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition-all ${
                  activeTab === "explainer"
                    ? "bg-[#8B5CF6]/20 text-[#C084FC] border border-[#8B5CF6]/40 shadow-[0_0_12px_rgba(168,85,247,0.3)]"
                    : "text-[#A1A1AA] hover:text-white"
                }`}
              >
                <Brain className="w-4 h-4" />
                <span>AI Concept Explainer (6 Modes)</span>
              </button>

              <button
                onClick={() => setActiveTab("quizzes")}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition-all ${
                  activeTab === "quizzes"
                    ? "bg-[#8B5CF6]/20 text-[#C084FC] border border-[#8B5CF6]/40 shadow-[0_0_12px_rgba(168,85,247,0.3)]"
                    : "text-[#A1A1AA] hover:text-white"
                }`}
              >
                <CheckCircle2 className="w-4 h-4" />
                <span>Practice & Adaptive Quizzes</span>
              </button>

              <button
                onClick={() => setActiveTab("notes")}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition-all ${
                  activeTab === "notes"
                    ? "bg-[#8B5CF6]/20 text-[#C084FC] border border-[#8B5CF6]/40 shadow-[0_0_12px_rgba(168,85,247,0.3)]"
                    : "text-[#A1A1AA] hover:text-white"
                }`}
              >
                <FileText className="w-4 h-4" />
                <span>Study Notes ({workspaceData.notes.length})</span>
              </button>

              <button
                onClick={() => setActiveTab("documents")}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition-all ${
                  activeTab === "documents"
                    ? "bg-[#8B5CF6]/20 text-[#C084FC] border border-[#8B5CF6]/40 shadow-[0_0_12px_rgba(168,85,247,0.3)]"
                    : "text-[#A1A1AA] hover:text-white"
                }`}
              >
                <UploadCloud className="w-4 h-4" />
                <span>Documents ({workspaceData.documents.length})</span>
              </button>
            </div>

            {/* TAB 1: AI Concept Explainer */}
            {activeTab === "explainer" && (
              <div className="p-6 rounded-2xl bg-[#160F23] border border-[#30203F] space-y-6">
                <div>
                  <h3 className="text-base font-bold text-white mb-1">Tailored Concept Explainer</h3>
                  <p className="text-xs text-[#A1A1AA]">
                    Choose from 6 pedagogical depths. The AI dynamically adapts tone, analogies, complexity, and examples.
                  </p>
                </div>

                {/* 6 Modes Selector */}
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
                  {EXPLANATION_MODES.map((mode) => (
                    <button
                      key={mode.id}
                      onClick={() => setExplanationMode(mode.id)}
                      className={`p-3 rounded-xl border text-left transition-all ${
                        explanationMode === mode.id
                          ? "bg-[#251A38] border-[#A855F7] shadow-[0_0_15px_rgba(168,85,247,0.25)]"
                          : "bg-[#191225] border-[#30203F] hover:border-[#8B5CF6]/40"
                      }`}
                    >
                      <span className={`text-xs font-bold block ${explanationMode === mode.id ? "text-[#C084FC]" : "text-white"}`}>
                        {mode.label}
                      </span>
                      <span className="text-[10px] text-[#A1A1AA] mt-1 line-clamp-2 block leading-tight">
                        {mode.desc}
                      </span>
                    </button>
                  ))}
                </div>

                {/* Query Input & Action */}
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={conceptQuery}
                    onChange={(e) => setConceptQuery(e.target.value)}
                    placeholder={`e.g. ${workspaceData.topic.name} or specific subtopic...`}
                    className="flex-1 px-4 py-2.5 rounded-xl bg-[#191225] border border-[#30203F] text-xs text-white focus:outline-none focus:border-[#8B5CF6]"
                  />
                  <button
                    onClick={handleGenerateExplanation}
                    disabled={explaining}
                    className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-[#8B5CF6] to-[#A855F7] text-xs font-bold text-white shadow-[0_0_15px_rgba(168,85,247,0.35)] hover:shadow-[0_0_22px_rgba(168,85,247,0.6)] disabled:opacity-50 transition-all"
                  >
                    {explaining ? (
                      <>
                        <RotateCcw className="w-3.5 h-3.5 animate-spin" />
                        <span>Generating...</span>
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-3.5 h-3.5" />
                        <span>Explain Mode</span>
                      </>
                    )}
                  </button>
                </div>

                {/* Output */}
                {explanationResult && (
                  <div className="p-6 rounded-xl bg-[#110B1A] border border-[#30203F] space-y-4">
                    <div className="flex items-center justify-between pb-3 border-b border-[#30203F]">
                      <div className="flex items-center gap-2">
                        <span className="px-2.5 py-0.5 rounded-full bg-purple-500/20 text-[#C084FC] text-[10px] font-bold border border-purple-500/30">
                          {explanationResult.mode_title}
                        </span>
                        <span className="text-xs font-bold text-white">{explanationResult.concept}</span>
                      </div>
                    </div>
                    <div className="prose prose-invert max-w-none text-xs text-[#D4D4D8] leading-relaxed whitespace-pre-line">
                      {explanationResult.content}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* TAB 2: Quizzes & Practice */}
            {activeTab === "quizzes" && (
              <div className="p-6 rounded-2xl bg-[#160F23] border border-[#30203F] space-y-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-base font-bold text-white">Targeted Knowledge Evaluation</h3>
                    <p className="text-xs text-[#A1A1AA]">
                      Generate adaptive quizzes tuned directly to your demonstrated error history.
                    </p>
                  </div>
                  <Link
                    href={`/dashboard/quiz?topic_id=${workspaceData.topic.id}`}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-[#8B5CF6] to-[#A855F7] text-xs font-bold text-white shadow-[0_0_15px_rgba(168,85,247,0.35)] hover:shadow-[0_0_20px_rgba(168,85,247,0.6)] transition-all"
                  >
                    <Zap className="w-3.5 h-3.5" />
                    <span>Start Adaptive Quiz</span>
                  </Link>
                </div>

                <div className="space-y-3">
                  <span className="text-xs font-bold text-[#A1A1AA] uppercase tracking-wider block">
                    Recent Attempts on this Topic
                  </span>
                  {workspaceData.quiz_attempts.length === 0 ? (
                    <div className="p-8 text-center text-xs text-[#71717A] bg-[#191225] rounded-xl border border-[#30203F]">
                      No quiz attempts yet for {workspaceData.topic.name}. Take a quiz to establish your baseline!
                    </div>
                  ) : (
                    workspaceData.quiz_attempts.map((att) => (
                      <div
                        key={att.attempt_id}
                        className="p-4 rounded-xl bg-[#191225] border border-[#30203F] flex items-center justify-between"
                      >
                        <div>
                          <p className="text-xs font-bold text-white">{att.quiz_title}</p>
                          <span className="text-[10px] text-[#71717A]">
                            {new Date(att.completed_at).toLocaleDateString()}
                          </span>
                        </div>
                        <div className="flex items-center gap-3">
                          <span className={`text-xs font-extrabold ${att.percentage >= 75 ? "text-emerald-400" : "text-amber-400"}`}>
                            {att.percentage}%
                          </span>
                          <span className="text-[11px] text-[#A1A1AA]">
                            ({att.score}/{att.max_score} pts)
                          </span>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}

            {/* TAB 3: Notes */}
            {activeTab === "notes" && (
              <div className="p-6 rounded-2xl bg-[#160F23] border border-[#30203F] space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-base font-bold text-white">Study Notes for {workspaceData.topic.name}</h3>
                    <p className="text-xs text-[#A1A1AA]">Organized notes, definitions, and cheat sheets.</p>
                  </div>
                  <Link
                    href={`/dashboard/notes?topic_id=${workspaceData.topic.id}`}
                    className="px-3.5 py-1.5 rounded-xl bg-[#191225] border border-[#30203F] text-xs font-semibold text-white hover:border-[#8B5CF6] transition-all"
                  >
                    Generate New Notes →
                  </Link>
                </div>

                {workspaceData.notes.length === 0 ? (
                  <div className="p-8 text-center text-xs text-[#71717A] bg-[#191225] rounded-xl border border-[#30203F]">
                    No notes saved for this topic yet. Generate your first structured study note!
                  </div>
                ) : (
                  <div className="grid grid-cols-1 gap-3">
                    {workspaceData.notes.map((n) => (
                      <div key={n.id} className="p-4 rounded-xl bg-[#191225] border border-[#30203F] space-y-1">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-bold text-white">{n.title}</span>
                          <span className="px-2 py-0.5 rounded-full bg-purple-500/10 text-[#C084FC] text-[10px] font-semibold">
                            {n.note_type}
                          </span>
                        </div>
                        <p className="text-xs text-[#A1A1AA] line-clamp-2">{n.content_preview}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* TAB 4: Documents */}
            {activeTab === "documents" && (
              <div className="p-6 rounded-2xl bg-[#160F23] border border-[#30203F] space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-base font-bold text-white">Subject Reference Documents</h3>
                    <p className="text-xs text-[#A1A1AA]">Uploaded textbooks, lecture slides, and notes.</p>
                  </div>
                  <Link
                    href="/dashboard/documents"
                    className="px-3.5 py-1.5 rounded-xl bg-[#191225] border border-[#30203F] text-xs font-semibold text-white hover:border-[#8B5CF6] transition-all"
                  >
                    Upload Document →
                  </Link>
                </div>

                {workspaceData.documents.length === 0 ? (
                  <div className="p-8 text-center text-xs text-[#71717A] bg-[#191225] rounded-xl border border-[#30203F]">
                    No documents uploaded for this subject yet.
                  </div>
                ) : (
                  <div className="grid grid-cols-1 gap-3">
                    {workspaceData.documents.map((d) => (
                      <div key={d.id} className="p-4 rounded-xl bg-[#191225] border border-[#30203F] flex items-center justify-between">
                        <div>
                          <p className="text-xs font-bold text-white">{d.title}</p>
                          <span className="text-[10px] text-[#71717A] uppercase">{d.file_type} • Status: {d.status}</span>
                        </div>
                        <Link
                          href="/dashboard/documents"
                          className="text-xs text-[#A855F7] hover:text-[#C084FC] font-medium"
                        >
                          View Citations →
                        </Link>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Right Col: Topic Performance & Spaced Repetition */}
          <div className="space-y-6">
            {/* Topic Metrics */}
            <div className="p-5 rounded-2xl bg-[#160F23] border border-[#30203F] space-y-4">
              <h3 className="text-xs font-bold text-white uppercase tracking-wider">Demonstrated Topic Metrics</h3>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-3.5 rounded-xl bg-[#191225] border border-[#30203F]">
                  <span className="text-[10px] text-[#A1A1AA] uppercase">Accuracy</span>
                  <p className="text-2xl font-black text-white mt-1">
                    {workspaceData.performance.accuracy_percentage}%
                  </p>
                </div>
                <div className="p-3.5 rounded-xl bg-[#191225] border border-[#30203F]">
                  <span className="text-[10px] text-[#A1A1AA] uppercase">Attempts</span>
                  <p className="text-2xl font-black text-white mt-1">
                    {workspaceData.performance.total_attempts}
                  </p>
                </div>
              </div>

              <div className="p-3.5 rounded-xl bg-[#191225] border border-[#30203F] space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-[#A1A1AA]">Correct Solutions</span>
                  <span className="font-bold text-emerald-400">{workspaceData.performance.correct_answers}</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-[#A1A1AA]">Incorrect Solutions</span>
                  <span className="font-bold text-rose-400">{workspaceData.performance.incorrect_answers}</span>
                </div>
              </div>
            </div>

            {/* Spaced Repetition Due Tasks */}
            <div className="p-5 rounded-2xl bg-[#160F23] border border-[#30203F] space-y-4">
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-[#C084FC]" />
                <h3 className="text-xs font-bold text-white uppercase tracking-wider">Spaced Repetition Schedule</h3>
              </div>

              {workspaceData.revision_tasks.length === 0 ? (
                <div className="p-4 rounded-xl bg-[#191225] border border-[#30203F] text-center text-xs text-[#71717A]">
                  No pending revision tasks for this topic.
                </div>
              ) : (
                <div className="space-y-2.5">
                  {workspaceData.revision_tasks.map((task) => (
                    <div
                      key={task.id}
                      className={`p-3.5 rounded-xl border transition-all ${
                        task.is_due
                          ? "bg-purple-950/20 border-purple-500/40"
                          : "bg-[#191225] border-[#30203F]"
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-white">{task.title}</span>
                        {task.is_due && (
                          <span className="px-1.5 py-0.5 rounded-full bg-purple-500/30 text-[#C084FC] text-[9px] font-extrabold uppercase">
                            Due Today
                          </span>
                        )}
                      </div>
                      <p className="text-[11px] text-[#A1A1AA] mt-1 line-clamp-2">{task.description}</p>
                      <div className="flex items-center justify-between mt-2 pt-2 border-t border-[#30203F]/50 text-[10px] text-[#71717A]">
                        <span>Target: {task.scheduled_date}</span>
                        <span className="text-[#C084FC] font-semibold">{task.priority} Priority</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function InteractiveWorkspacePage() {
  return (
    <Suspense fallback={<div className="p-12 text-center text-xs text-[#A1A1AA] animate-pulse">Loading Interactive Learning Workspace...</div>}>
      <WorkspaceContent />
    </Suspense>
  );
}

