"use client";

import React, { useState, useEffect } from "react";
import {
  CheckCircle2,
  Sparkles,
  Clock,
  AlertCircle,
  HelpCircle,
  Award,
  History,
  RotateCcw,
  BookOpen,
  ArrowRight,
  ArrowLeft,
  Code,
  CheckSquare,
  FileText,
  Briefcase,
  Terminal,
  Zap,
  Layers,
  Check,
  Bookmark,
  RefreshCw,
  FileCode,
  TrendingUp,
  XCircle,
  CheckCheck
} from "lucide-react";
import { GlowCard } from "@/components/GlowCard";
import { api } from "@/lib/api";
import { Quiz, QuizResult, QuizAttemptHistory, DocumentItem, Subject, Note } from "@/lib/types";

// Primary and Advanced Question Types
const QUESTION_TYPES = [
  { id: "mcq", label: "Multiple Choice", desc: "4 choices with single correct answer", icon: CheckCircle2 },
  { id: "true_false", label: "True or False", desc: "Binary truth evaluation of concepts", icon: CheckSquare },
  { id: "fill_in_the_blank", label: "Fill in the Blanks", desc: "Key academic terms and formulas", icon: FileText },
  { id: "short_answer", label: "Short Answer", desc: "Concise technical definitions & explanations", icon: Layers },
  { id: "multiple_select", label: "Multiple Select", desc: "Select all correct statements", icon: CheckSquare },
  { id: "technical_interview", label: "Technical Interview", desc: "System design & trade-off scenarios", icon: Briefcase },
  { id: "programming", label: "Coding Problem", desc: "Algorithmic challenge with test cases", icon: Terminal },
];

const DIFFICULTY_LEVELS = [
  { id: "easy", label: "Easy", desc: "Foundational concepts & syntax", color: "text-emerald-400 border-emerald-500/30 bg-emerald-500/10" },
  { id: "medium", label: "Medium", desc: "Algorithmic reasoning & logic", color: "text-purple-400 border-purple-500/30 bg-purple-500/10" },
  { id: "hard", label: "Hard", desc: "Edge cases & architectural depth", color: "text-rose-400 border-rose-500/30 bg-rose-500/10" },
  { id: "mixed", label: "Mixed Difficulty", desc: "Balanced adaptive mix (Easy, Medium, Hard)", color: "text-amber-400 border-amber-500/30 bg-amber-500/10" },
];

export default function AIQuizGeneratorPage() {
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [notes, setNotes] = useState<Note[]>([]);
  const [history, setHistory] = useState<QuizAttemptHistory[]>([]);
  const [loadingPrereqs, setLoadingPrereqs] = useState(true);

  // Generation Source Tab: "curriculum" | "document" | "note"
  const [sourceType, setSourceType] = useState<"curriculum" | "document" | "note">("curriculum");

  // Curriculum Form State
  const [selectedSubjectId, setSelectedSubjectId] = useState<string>("");
  const [selectedTopicId, setSelectedTopicId] = useState<string>("");
  const [selectedSubtopic, setSelectedSubtopic] = useState<string>("");

  // Document & Note Source State
  const [selectedDocId, setSelectedDocId] = useState<string>("");
  const [selectedNoteId, setSelectedNoteId] = useState<string>("");

  // Quiz Configuration State
  const [selectedQuestionType, setSelectedQuestionType] = useState<string>("mcq");
  const [difficulty, setDifficulty] = useState<string>("medium");
  const [questionCount, setQuestionCount] = useState<number>(5);
  const [generating, setGenerating] = useState(false);
  const [generationError, setGenerationError] = useState<string | null>(null);

  // Active Quiz Examination State
  const [activeQuiz, setActiveQuiz] = useState<Quiz | null>(null);
  const [currentQIndex, setCurrentQIndex] = useState<number>(0);
  const [userAnswers, setUserAnswers] = useState<Record<string, string>>({});
  const [flaggedQuestions, setFlaggedQuestions] = useState<Record<string, boolean>>({});
  const [viewMode, setViewMode] = useState<"single" | "all">("single");
  const [submitting, setSubmitting] = useState(false);
  const [quizResult, setQuizResult] = useState<QuizResult | null>(null);

  // Examination Countdown Timer
  const [remainingSeconds, setRemainingSeconds] = useState<number>(0);
  const [timeSpentSeconds, setTimeSpentSeconds] = useState<number>(0);

  useEffect(() => {
    loadPrerequisites();
  }, []);

  // Timer countdown hook
  useEffect(() => {
    let interval: any;
    if (activeQuiz && !quizResult) {
      interval = setInterval(() => {
        setRemainingSeconds((prev) => {
          if (prev <= 1) {
            clearInterval(interval);
            // Time expired
            return 0;
          }
          return prev - 1;
        });
        setTimeSpentSeconds((prev) => prev + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [activeQuiz, quizResult]);

  async function loadPrerequisites() {
    try {
      const [subs, docs, nts, hist] = await Promise.all([
        api.getSubjects().catch(() => []),
        api.listDocuments().catch(() => []),
        api.listNotes().catch(() => []),
        api.getQuizHistory().catch(() => []),
      ]);
      setSubjects(subs);
      setDocuments(docs.filter((d) => d.status === "ready"));
      setNotes(nts);
      setHistory(hist);
      if (subs.length > 0) {
        setSelectedSubjectId(subs[0].id);
      }
    } catch (e) {
      console.error("Error loading prerequisites:", e);
    } finally {
      setLoadingPrereqs(false);
    }
  }

  const currentSubject = subjects.find((s) => s.id === selectedSubjectId);
  const availableTopics = currentSubject?.topics || [];
  const currentTopic = availableTopics.find((t) => t.id === selectedTopicId);
  const availableSubtopics = currentTopic?.subtopics || [];

  const handleGenerateQuiz = async (e: React.FormEvent) => {
    e.preventDefault();
    setGenerating(true);
    setGenerationError(null);
    setQuizResult(null);
    setUserAnswers({});
    setFlaggedQuestions({});
    setCurrentQIndex(0);

    try {
      let payload: any = {
        difficulty,
        question_count: questionCount,
        question_types: [selectedQuestionType],
      };

      if (sourceType === "curriculum") {
        if (!selectedTopicId) {
          throw new Error("Please select a topic from the curriculum.");
        }
        payload.subject_id = selectedSubjectId || undefined;
        payload.topic_id = selectedTopicId || undefined;
        payload.subtopic = selectedSubtopic || undefined;
      } else if (sourceType === "document") {
        if (!selectedDocId) {
          throw new Error("Please choose an uploaded document.");
        }
        payload.document_id = selectedDocId;
      } else if (sourceType === "note") {
        if (!selectedNoteId) {
          throw new Error("Please select a previously generated study note.");
        }
        payload.note_id = selectedNoteId;
      }

      const quiz = await api.generateQuiz(payload);
      setActiveQuiz(quiz);
      const totalSecs = (quiz.time_limit_mins || 15) * 60;
      setRemainingSeconds(totalSecs);
      setTimeSpentSeconds(0);
    } catch (err: any) {
      console.error("Quiz generation error:", err);
      setGenerationError(err.message || "Failed to generate quiz. Please try again.");
    } finally {
      setGenerating(false);
    }
  };

  const handleSelectOption = (questionId: string, optionText: string) => {
    setUserAnswers((prev) => ({ ...prev, [questionId]: optionText }));
  };

  const handleToggleMsqOption = (questionId: string, optionText: string) => {
    const currentStr = userAnswers[questionId] || "";
    const selectedList = currentStr ? currentStr.split(", ") : [];
    let updatedList: string[];
    if (selectedList.includes(optionText)) {
      updatedList = selectedList.filter((item) => item !== optionText);
    } else {
      updatedList = [...selectedList, optionText];
    }
    setUserAnswers((prev) => ({ ...prev, [questionId]: updatedList.join(", ") }));
  };

  const handleTextResponse = (questionId: string, text: string) => {
    setUserAnswers((prev) => ({ ...prev, [questionId]: text }));
  };

  const handleToggleFlag = (questionId: string) => {
    setFlaggedQuestions((prev) => ({ ...prev, [questionId]: !prev[questionId] }));
  };

  const handleSubmitQuiz = async () => {
    if (!activeQuiz) return;
    setSubmitting(true);
    try {
      const submissionAnswers = activeQuiz.questions.map((q) => ({
        question_id: q.id,
        user_response: userAnswers[q.id] || "",
      }));

      const result = await api.submitQuiz(activeQuiz.id, {
        time_taken_seconds: timeSpentSeconds,
        answers: submissionAnswers,
      });

      setQuizResult(result);
      const updatedHist = await api.getQuizHistory();
      setHistory(updatedHist);
    } catch (err) {
      console.error("Quiz submission error:", err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleRetakeSameQuiz = () => {
    if (!activeQuiz) return;
    setUserAnswers({});
    setFlaggedQuestions({});
    setCurrentQIndex(0);
    setQuizResult(null);
    const totalSecs = (activeQuiz.time_limit_mins || 15) * 60;
    setRemainingSeconds(totalSecs);
    setTimeSpentSeconds(0);
  };

  const handleViewPastAttempt = async (attemptId: string) => {
    try {
      const res = await api.getQuizAttempt(attemptId);
      setQuizResult(res);
      setActiveQuiz({
        id: res.quiz_id,
        title: "Previous Examination Assessment",
        difficulty: "standard",
        total_questions: res.answers.length,
        time_limit_mins: 15,
        created_at: res.completed_at,
        questions: res.answers.map((a, idx) => ({
          id: a.question_id,
          quiz_id: res.quiz_id,
          question_text: a.question_text,
          question_type: "mcq",
          points: 1,
        })),
      });
    } catch (err) {
      console.error("Error viewing past attempt:", err);
    }
  };

  const resetQuiz = () => {
    setActiveQuiz(null);
    setQuizResult(null);
    setUserAnswers({});
    setFlaggedQuestions({});
    setCurrentQIndex(0);
    setRemainingSeconds(0);
    setTimeSpentSeconds(0);
  };

  const formatTimer = (secs: number) => {
    const mins = Math.floor(secs / 60);
    const rem = secs % 60;
    return `${mins < 10 ? "0" : ""}${mins}:${rem < 10 ? "0" : ""}${rem}`;
  };

  const answeredCount = activeQuiz
    ? activeQuiz.questions.filter((q) => userAnswers[q.id] && userAnswers[q.id].trim().length > 0).length
    : 0;
  const progressPercent = activeQuiz ? Math.round((answeredCount / activeQuiz.questions.length) * 100) : 0;

  return (
    <div className="space-y-6">
      {/* Top Title & Branding */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-6 h-6 text-[#A855F7]" />
            <h1 className="text-xl font-bold text-white tracking-tight">Intelligent AI Quiz Generator</h1>
            <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-purple-500/10 border border-purple-500/30 text-[#C084FC]">
              Phase 4 Examination Engine
            </span>
          </div>
          <p className="text-xs text-[#A1A1AA] mt-1">
            Generate rigorous assessments from subjects, topics, uploaded documents, or study notes with dynamic evaluation and revision recommendations.
          </p>
        </div>

        {/* Live Examination Timer */}
        {activeQuiz && !quizResult && (
          <div
            className={`flex items-center gap-2.5 px-4 py-2 rounded-xl border font-mono transition-all ${
              remainingSeconds <= 120
                ? "bg-red-500/10 border-red-500/50 text-red-300 animate-pulse shadow-[0_0_15px_rgba(239,68,68,0.3)]"
                : remainingSeconds <= 300
                ? "bg-amber-500/10 border-amber-500/40 text-amber-300"
                : "bg-[#191225] border-[#30203F] text-white"
            }`}
          >
            <Clock className={`w-4 h-4 ${remainingSeconds <= 120 ? "text-red-400" : "text-[#C084FC]"}`} />
            <div>
              <div className="text-[10px] text-[#A1A1AA] uppercase leading-none font-sans font-semibold">Time Remaining</div>
              <div className="text-sm font-bold tracking-wider">{formatTimer(remainingSeconds)}</div>
            </div>
          </div>
        )}
      </div>

      {/* 1. QUIZ CONFIGURATION WORKFLOW */}
      {!activeQuiz ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <GlowCard glow className="p-6 lg:col-span-2 space-y-5 border border-[#30203F] bg-[#100B18]/80">
            {/* Header */}
            <div className="flex items-center justify-between border-b border-[#30203F] pb-3">
              <h2 className="text-sm font-bold text-white flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-[#A855F7]" /> Configure Examination Assessment
              </h2>
              <span className="text-[10px] text-[#C084FC] font-semibold bg-[#8B5CF6]/15 px-2.5 py-0.5 rounded-full border border-[#A855F7]/30">
                AI Model Integration
              </span>
            </div>

            <form onSubmit={handleGenerateQuiz} className="space-y-5">
              {/* Step 1: Knowledge Source Tabs */}
              <div>
                <label className="block text-[11px] font-semibold text-[#A1A1AA] uppercase tracking-wider mb-2">
                  1. Select Knowledge Source (4 Sources Supported)
                </label>
                <div className="grid grid-cols-3 gap-2 p-1 rounded-xl bg-[#08060D] border border-[#30203F]">
                  <button
                    type="button"
                    onClick={() => setSourceType("curriculum")}
                    className={`py-2 px-3 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
                      sourceType === "curriculum"
                        ? "bg-[#191225] text-white border border-[#A855F7] shadow-[0_0_12px_rgba(168,85,247,0.3)]"
                        : "text-[#A1A1AA] hover:text-white"
                    }`}
                  >
                    <BookOpen className="w-3.5 h-3.5 text-[#A855F7]" />
                    <span>Curriculum Subject</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setSourceType("document")}
                    className={`py-2 px-3 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
                      sourceType === "document"
                        ? "bg-[#191225] text-white border border-[#A855F7] shadow-[0_0_12px_rgba(168,85,247,0.3)]"
                        : "text-[#A1A1AA] hover:text-white"
                    }`}
                  >
                    <FileCode className="w-3.5 h-3.5 text-[#C084FC]" />
                    <span>Uploaded Document</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setSourceType("note")}
                    className={`py-2 px-3 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
                      sourceType === "note"
                        ? "bg-[#191225] text-white border border-[#A855F7] shadow-[0_0_12px_rgba(168,85,247,0.3)]"
                        : "text-[#A1A1AA] hover:text-white"
                    }`}
                  >
                    <FileText className="w-3.5 h-3.5 text-[#A855F7]" />
                    <span>Study Note</span>
                  </button>
                </div>
              </div>

              {/* Source-specific Sub-controls */}
              {sourceType === "curriculum" && (
                <div className="space-y-3 p-3.5 rounded-xl bg-[#08060D] border border-[#30203F]/60">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                      <label className="block text-[11px] font-semibold text-[#A1A1AA] uppercase tracking-wider mb-1.5">
                        Select Subject ({subjects.length} Available)
                      </label>
                      <select
                        value={selectedSubjectId}
                        onChange={(e) => {
                          setSelectedSubjectId(e.target.value);
                          setSelectedTopicId("");
                          setSelectedSubtopic("");
                        }}
                        className="w-full px-3 py-2 rounded-lg bg-[#100B18] border border-[#30203F] text-xs text-white focus:outline-none focus:border-[#A855F7]"
                      >
                        {subjects.map((sub) => (
                          <option key={sub.id} value={sub.id}>
                            {sub.name} ({sub.code || "CS"})
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-[11px] font-semibold text-[#A1A1AA] uppercase tracking-wider mb-1.5">
                        Select Topic ({availableTopics.length} Topics)
                      </label>
                      <select
                        value={selectedTopicId}
                        onChange={(e) => {
                          setSelectedTopicId(e.target.value);
                          setSelectedSubtopic("");
                        }}
                        required
                        className="w-full px-3 py-2 rounded-lg bg-[#100B18] border border-[#30203F] text-xs text-white focus:outline-none focus:border-[#A855F7]"
                      >
                        <option value="">Choose Topic...</option>
                        {availableTopics.map((t) => (
                          <option key={t.id} value={t.id}>
                            {t.is_emerging ? "⚡ [Emerging] " : ""}{t.name}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>

                  {availableSubtopics.length > 0 && (
                    <div>
                      <label className="block text-[11px] font-semibold text-[#A1A1AA] uppercase tracking-wider mb-1.5">
                        Subtopic Focus (Optional)
                      </label>
                      <select
                        value={selectedSubtopic}
                        onChange={(e) => setSelectedSubtopic(e.target.value)}
                        className="w-full px-3 py-2 rounded-lg bg-[#100B18] border border-[#30203F] text-xs text-white focus:outline-none focus:border-[#A855F7]"
                      >
                        <option value="">All Module Concepts (Comprehensive Coverage)</option>
                        {availableSubtopics.map((st, i) => (
                          <option key={i} value={st}>
                            {st}
                          </option>
                        ))}
                      </select>
                    </div>
                  )}
                </div>
              )}

              {sourceType === "document" && (
                <div className="p-3.5 rounded-xl bg-[#08060D] border border-[#30203F]/60">
                  <label className="block text-[11px] font-semibold text-[#A1A1AA] uppercase tracking-wider mb-1.5">
                    Select Uploaded Document ({documents.length} Available)
                  </label>
                  {documents.length === 0 ? (
                    <div className="text-xs text-[#71717A] py-2">
                      No ready documents found. Upload course PDFs or DOCX files in Document Management to take document quizzes!
                    </div>
                  ) : (
                    <select
                      value={selectedDocId}
                      onChange={(e) => setSelectedDocId(e.target.value)}
                      required
                      className="w-full px-3 py-2 rounded-lg bg-[#100B18] border border-[#30203F] text-xs text-white focus:outline-none focus:border-[#A855F7]"
                    >
                      <option value="">Choose Document Source...</option>
                      {documents.map((d) => (
                        <option key={d.id} value={d.id}>
                          {d.title} ({d.file_type.toUpperCase()})
                        </option>
                      ))}
                    </select>
                  )}
                </div>
              )}

              {sourceType === "note" && (
                <div className="p-3.5 rounded-xl bg-[#08060D] border border-[#30203F]/60">
                  <label className="block text-[11px] font-semibold text-[#A1A1AA] uppercase tracking-wider mb-1.5">
                    Select Previously Generated Study Note ({notes.length} Available)
                  </label>
                  {notes.length === 0 ? (
                    <div className="text-xs text-[#71717A] py-2">
                      No study notes found. Generate notes in Smart Notes Generator first to quiz yourself on your notes!
                    </div>
                  ) : (
                    <select
                      value={selectedNoteId}
                      onChange={(e) => setSelectedNoteId(e.target.value)}
                      required
                      className="w-full px-3 py-2 rounded-lg bg-[#100B18] border border-[#30203F] text-xs text-white focus:outline-none focus:border-[#A855F7]"
                    >
                      <option value="">Choose Study Note...</option>
                      {notes.map((n) => (
                        <option key={n.id} value={n.id}>
                          {n.title} [{n.note_type.replace(/_/g, " ")}]
                        </option>
                      ))}
                    </select>
                  )}
                </div>
              )}

              {/* Step 2: Question Type (MCQ, True/False, Fill in Blanks, Short Answer, etc.) */}
              <div>
                <label className="block text-[11px] font-semibold text-[#A1A1AA] uppercase tracking-wider mb-2">
                  2. Question Format
                </label>
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2.5">
                  {QUESTION_TYPES.map((type) => {
                    const Icon = type.icon;
                    const isSelected = selectedQuestionType === type.id;
                    return (
                      <button
                        key={type.id}
                        type="button"
                        onClick={() => setSelectedQuestionType(type.id)}
                        className={`text-left p-3 rounded-xl border text-xs transition-all ${
                          isSelected
                            ? "bg-purple-900/50 border-[#A855F7] text-white shadow-[0_0_12px_rgba(168,85,247,0.35)]"
                            : "bg-[#08060D] border-[#30203F] text-[#A1A1AA] hover:border-purple-500/40 hover:text-white"
                        }`}
                      >
                        <div className="flex items-center gap-2 mb-1">
                          <Icon className={`w-3.5 h-3.5 ${isSelected ? "text-[#C084FC]" : "text-[#A1A1AA]"}`} />
                          <span className="font-bold">{type.label}</span>
                        </div>
                        <p className="text-[10px] text-[#71717A] line-clamp-1">{type.desc}</p>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Step 3: Difficulty & Question Count */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-1">
                <div>
                  <label className="block text-[11px] font-semibold text-[#A1A1AA] uppercase tracking-wider mb-2">
                    3. Difficulty Level
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    {DIFFICULTY_LEVELS.map((lvl) => {
                      const isSelected = difficulty === lvl.id;
                      return (
                        <button
                          key={lvl.id}
                          type="button"
                          onClick={() => setDifficulty(lvl.id)}
                          className={`py-2 px-2.5 rounded-xl text-xs font-bold border transition-all text-center ${
                            isSelected
                              ? lvl.color + " shadow-[0_0_12px_rgba(168,85,247,0.3)] ring-1 ring-[#A855F7]"
                              : "bg-[#08060D] border-[#30203F] text-[#A1A1AA] hover:text-white"
                          }`}
                        >
                          {lvl.label}
                        </button>
                      );
                    })}
                  </div>
                </div>

                <div>
                  <label className="block text-[11px] font-semibold text-[#A1A1AA] uppercase tracking-wider mb-2">
                    4. Question Count ({questionCount} questions)
                  </label>
                  <input
                    type="range"
                    min={1}
                    max={10}
                    value={questionCount}
                    onChange={(e) => setQuestionCount(Number(e.target.value))}
                    className="w-full accent-[#A855F7] bg-[#08060D] rounded-lg cursor-pointer h-2 mt-2"
                  />
                  <div className="flex justify-between text-[10px] text-[#71717A] mt-1 font-mono">
                    <span>1</span>
                    <span>3</span>
                    <span>5 (Standard)</span>
                    <span>10</span>
                  </div>
                </div>
              </div>

              {generationError && (
                <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-xs text-red-300">
                  {generationError}
                </div>
              )}

              {/* Submit Button */}
              <button
                type="submit"
                disabled={generating}
                className="w-full py-3.5 rounded-xl text-xs sm:text-sm font-bold bg-gradient-to-r from-[#8B5CF6] via-[#A855F7] to-[#C084FC] hover:shadow-[0_0_25px_rgba(168,85,247,0.6)] text-white transition-all flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {generating ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span>AI Model Generating Unique Questions...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    <span>Start Examination Assessment</span>
                  </>
                )}
              </button>
            </form>
          </GlowCard>

          {/* Right Column: Active Syllabus & Evidence Rules */}
          <div className="space-y-4">
            <GlowCard className="p-5 border border-[#30203F] bg-[#100B18]/70">
              <h3 className="text-xs font-bold text-white uppercase tracking-wider mb-3 flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-[#C084FC]" /> Curriculum Overview
              </h3>
              {currentSubject ? (
                <div className="space-y-2">
                  <div className="text-sm font-bold text-white">{currentSubject.name}</div>
                  <p className="text-xs text-[#A1A1AA] leading-relaxed">{currentSubject.description}</p>
                  <div className="pt-2 border-t border-[#30203F] space-y-1.5">
                    <div className="text-[11px] font-semibold text-[#C084FC]">
                      {availableTopics.length} Academic Modules:
                    </div>
                    <ul className="text-xs space-y-1 text-[#A1A1AA] max-h-44 overflow-y-auto pr-1">
                      {availableTopics.map((t) => (
                        <li key={t.id} className="flex items-center gap-1.5 truncate">
                          <div className={`w-1.5 h-1.5 rounded-full ${t.is_emerging ? "bg-amber-400" : "bg-purple-400"}`} />
                          <span className={t.is_emerging ? "text-amber-300 font-medium" : ""}>
                            {t.name}
                          </span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ) : (
                <p className="text-xs text-[#71717A]">Select a subject to view curriculum topics.</p>
              )}
            </GlowCard>

            <GlowCard className="p-5 border border-[#30203F] bg-[#100B18]/70">
              <h3 className="text-xs font-bold text-white uppercase tracking-wider mb-2 flex items-center gap-2">
                <Award className="w-4 h-4 text-emerald-400" /> Dynamic Scoring & Rubrics
              </h3>
              <p className="text-xs text-[#A1A1AA] leading-relaxed">
                Assessments are scored with instant feedback, model answer keys, pedagogical explanations, and mistake analysis that updates your mastery tracking.
              </p>
            </GlowCard>
          </div>
        </div>
      ) : null}

      {/* 2. ACTIVE EXAMINATION INTERFACE */}
      {activeQuiz && !quizResult && (
        <div className="max-w-5xl mx-auto space-y-5">
          {/* Examination Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-xl bg-[#140D20] border border-[#30203F]">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-purple-500/20 text-[#C084FC] border border-[#A855F7]/30 uppercase">
                  {activeQuiz.difficulty}
                </span>
                <span className="text-xs text-[#A1A1AA]">
                  {answeredCount} of {activeQuiz.questions.length} answered ({progressPercent}%)
                </span>
              </div>
              <h2 className="text-base font-bold text-white mt-1">{activeQuiz.title}</h2>
            </div>

            <div className="flex items-center gap-2.5">
              <div className="flex items-center rounded-lg bg-[#08060D] border border-[#30203F] p-0.5 text-xs">
                <button
                  onClick={() => setViewMode("single")}
                  className={`px-2.5 py-1 rounded text-[11px] font-bold ${
                    viewMode === "single" ? "bg-purple-600 text-white" : "text-[#A1A1AA] hover:text-white"
                  }`}
                >
                  Step-by-Step
                </button>
                <button
                  onClick={() => setViewMode("all")}
                  className={`px-2.5 py-1 rounded text-[11px] font-bold ${
                    viewMode === "all" ? "bg-purple-600 text-white" : "text-[#A1A1AA] hover:text-white"
                  }`}
                >
                  All Questions
                </button>
              </div>

              <button
                onClick={resetQuiz}
                className="px-3 py-1.5 rounded-lg text-xs font-bold text-[#A1A1AA] hover:text-white bg-[#08060D] border border-[#30203F] hover:border-red-500/40 transition-colors"
              >
                Exit Exam
              </button>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="w-full bg-[#100B18] h-1.5 rounded-full overflow-hidden border border-[#30203F]/60">
            <div
              className="bg-gradient-to-r from-[#8B5CF6] to-[#A855F7] h-full transition-all duration-300"
              style={{ width: `${progressPercent}%` }}
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Left/Main Column: Question Taking Area */}
            <div className="lg:col-span-3 space-y-5">
              {(viewMode === "single"
                ? [activeQuiz.questions[currentQIndex]]
                : activeQuiz.questions
              ).map((q, displayIdx) => {
                const actualIndex = viewMode === "single" ? currentQIndex : displayIdx;
                const qType = q.question_type || "mcq";
                const currentVal = userAnswers[q.id] || "";
                const isFlagged = flaggedQuestions[q.id] || false;

                return (
                  <GlowCard key={q.id} className="p-6 space-y-4 border border-[#30203F] bg-[#100B18]/80">
                    {/* Question Header Bar */}
                    <div className="flex items-center justify-between pb-3 border-b border-[#30203F]/60">
                      <div className="flex items-center gap-2">
                        <span className="w-6 h-6 rounded-md bg-gradient-to-br from-[#8B5CF6] to-[#A855F7] flex items-center justify-center text-xs font-bold text-white shrink-0">
                          {actualIndex + 1}
                        </span>
                        <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded bg-purple-500/10 text-[#C084FC] border border-purple-500/20">
                          {qType.replace(/_/g, " ")} &bull; {q.points} {q.points === 1 ? "point" : "points"}
                        </span>
                      </div>

                      {/* Flag for Review Button */}
                      <button
                        onClick={() => handleToggleFlag(q.id)}
                        className={`text-xs px-2.5 py-1 rounded-lg border flex items-center gap-1.5 transition-all ${
                          isFlagged
                            ? "bg-amber-500/20 border-amber-500/40 text-amber-300"
                            : "bg-[#08060D] border-[#30203F] text-[#A1A1AA] hover:text-white"
                        }`}
                      >
                        <Bookmark className={`w-3.5 h-3.5 ${isFlagged ? "fill-amber-400 text-amber-400" : ""}`} />
                        <span>{isFlagged ? "Marked for Review" : "Mark for Review"}</span>
                      </button>
                    </div>

                    {/* Question Text */}
                    <p className="text-sm sm:text-base font-semibold text-white leading-relaxed">
                      {q.question_text}
                    </p>

                    {/* 1. Multiple Choice (MCQ) */}
                    {qType === "mcq" && q.options && (
                      <div className="space-y-2 pt-2">
                        {q.options.map((opt, optIdx) => {
                          const isSelected = currentVal === opt;
                          return (
                            <button
                              key={optIdx}
                              type="button"
                              onClick={() => handleSelectOption(q.id, opt)}
                              className={`w-full text-left p-3.5 rounded-xl border text-xs sm:text-sm font-medium transition-all flex items-center justify-between ${
                                isSelected
                                  ? "bg-purple-900/60 border-[#A855F7] text-white shadow-[0_0_15px_-3px_rgba(168,85,247,0.4)]"
                                  : "bg-[#08060D] border-[#30203F] text-[#A1A1AA] hover:border-[#8B5CF6]/50 hover:text-white hover:bg-[#120B1C]"
                              }`}
                            >
                              <span>{opt}</span>
                              <div
                                className={`w-4 h-4 rounded-full border flex items-center justify-center shrink-0 ml-3 ${
                                  isSelected ? "border-[#A855F7] bg-[#A855F7]" : "border-[#30203F]"
                                }`}
                              >
                                {isSelected && <div className="w-1.5 h-1.5 rounded-full bg-white" />}
                              </div>
                            </button>
                          );
                        })}
                      </div>
                    )}

                    {/* 2. True or False */}
                    {qType === "true_false" && (
                      <div className="grid grid-cols-2 gap-3 pt-2">
                        {["True", "False"].map((tf) => {
                          const isSelected = currentVal === tf;
                          return (
                            <button
                              key={tf}
                              type="button"
                              onClick={() => handleSelectOption(q.id, tf)}
                              className={`p-4 rounded-xl border text-sm font-bold transition-all flex items-center justify-center gap-2 ${
                                isSelected
                                  ? tf === "True"
                                    ? "bg-emerald-950/40 border-emerald-500 text-emerald-300 shadow-[0_0_15px_rgba(16,185,129,0.3)] ring-1 ring-emerald-500"
                                    : "bg-red-950/40 border-red-500 text-red-300 shadow-[0_0_15px_rgba(239,68,68,0.3)] ring-1 ring-red-500"
                                  : "bg-[#08060D] border-[#30203F] text-[#A1A1AA] hover:border-purple-500/40 hover:text-white"
                              }`}
                            >
                              {tf === "True" ? <Check className="w-4 h-4" /> : <XCircle className="w-4 h-4" />}
                              <span>{tf}</span>
                            </button>
                          );
                        })}
                      </div>
                    )}

                    {/* 3. Fill in the Blanks */}
                    {qType === "fill_in_the_blank" && (
                      <div className="space-y-3 pt-2">
                        <div>
                          <label className="block text-[11px] font-semibold text-[#A1A1AA] uppercase tracking-wider mb-1.5">
                            Enter the Missing Term / Value
                          </label>
                          <input
                            type="text"
                            value={currentVal}
                            onChange={(e) => handleTextResponse(q.id, e.target.value)}
                            placeholder="Type your answer to fill in the blank..."
                            className="w-full px-3.5 py-2.5 rounded-xl bg-[#08060D] border border-[#30203F] text-xs sm:text-sm text-white focus:outline-none focus:border-[#A855F7] focus:ring-1 focus:ring-[#A855F7]"
                          />
                        </div>

                        {q.options && q.options.length > 0 && (
                          <div className="space-y-1.5">
                            <span className="text-[10px] text-[#71717A] uppercase font-bold tracking-wider">
                              Or choose from suggested options:
                            </span>
                            <div className="flex flex-wrap gap-2">
                              {q.options.map((opt, optIdx) => (
                                <button
                                  key={optIdx}
                                  type="button"
                                  onClick={() => handleSelectOption(q.id, opt)}
                                  className={`px-3 py-1.5 rounded-lg border text-xs font-medium transition-all ${
                                    currentVal === opt
                                      ? "bg-purple-900/60 border-[#A855F7] text-white shadow-[0_0_10px_rgba(168,85,247,0.3)]"
                                      : "bg-[#08060D] border-[#30203F] text-[#A1A1AA] hover:text-white hover:border-purple-500/40"
                                  }`}
                                >
                                  {opt}
                                </button>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}

                    {/* 4. Short Answer & Open-Ended */}
                    {["short_answer", "long_answer", "technical_interview", "scenario_based"].includes(qType) && (
                      <div className="space-y-2 pt-2">
                        <label className="block text-[11px] font-semibold text-[#A1A1AA] uppercase tracking-wider">
                          Your Technical Response
                        </label>
                        <textarea
                          rows={qType === "short_answer" ? 3 : 5}
                          value={currentVal}
                          onChange={(e) => handleTextResponse(q.id, e.target.value)}
                          placeholder={
                            qType === "short_answer"
                              ? "Provide a clear 1-2 sentence response with technical definitions..."
                              : "Structure your explanation with architectural concepts and step-by-step logic..."
                          }
                          className="w-full p-3.5 rounded-xl bg-[#08060D] border border-[#30203F] text-xs sm:text-sm text-white focus:outline-none focus:border-[#A855F7] focus:ring-1 focus:ring-[#A855F7] leading-relaxed"
                        />
                      </div>
                    )}

                    {/* 5. Multiple Select (MSQ) */}
                    {qType === "multiple_select" && q.options && (
                      <div className="space-y-2 pt-2">
                        <p className="text-[11px] text-[#C084FC] font-medium">Select all statements that apply:</p>
                        {q.options.map((opt, optIdx) => {
                          const selectedList = currentVal ? currentVal.split(", ") : [];
                          const isSelected = selectedList.includes(opt);
                          return (
                            <button
                              key={optIdx}
                              type="button"
                              onClick={() => handleToggleMsqOption(q.id, opt)}
                              className={`w-full text-left p-3.5 rounded-xl border text-xs sm:text-sm font-medium transition-all flex items-center justify-between ${
                                isSelected
                                  ? "bg-purple-900/60 border-[#A855F7] text-white shadow-[0_0_15px_-3px_rgba(168,85,247,0.4)]"
                                  : "bg-[#08060D] border-[#30203F] text-[#A1A1AA] hover:border-[#8B5CF6]/50 hover:text-white"
                              }`}
                            >
                              <span>{opt}</span>
                              <div
                                className={`w-4 h-4 rounded-md border flex items-center justify-center shrink-0 ml-3 ${
                                  isSelected ? "border-[#A855F7] bg-[#A855F7]" : "border-[#30203F]"
                                }`}
                              >
                                {isSelected && <Check className="w-3 h-3 text-white" />}
                              </div>
                            </button>
                          );
                        })}
                      </div>
                    )}

                    {/* 6. Programming Problem */}
                    {qType === "programming" && (
                      <div className="space-y-3 pt-2">
                        {q.test_cases && q.test_cases.length > 0 && (
                          <div className="p-3 rounded-lg bg-[#08060D] border border-[#30203F] text-xs font-mono text-[#A1A1AA]">
                            <span className="text-[#C084FC] font-bold block mb-1">Example Test Cases:</span>
                            {q.test_cases.map((tc, tcIdx) => (
                              <div key={tcIdx}>{tc}</div>
                            ))}
                          </div>
                        )}
                        <textarea
                          rows={7}
                          value={currentVal || q.code_snippet || ""}
                          onChange={(e) => handleTextResponse(q.id, e.target.value)}
                          placeholder="Write your algorithmic solution here..."
                          className="w-full p-3.5 rounded-xl bg-[#08060D] border border-[#30203F] font-mono text-xs sm:text-sm text-purple-200 focus:outline-none focus:border-[#A855F7]"
                        />
                      </div>
                    )}
                  </GlowCard>
                );
              })}

              {/* Step Navigation in Single Mode */}
              {viewMode === "single" && (
                <div className="flex items-center justify-between p-4 rounded-xl bg-[#140D20] border border-[#30203F]">
                  <button
                    onClick={() => setCurrentQIndex((prev) => Math.max(0, prev - 1))}
                    disabled={currentQIndex === 0}
                    className="px-4 py-2 rounded-lg text-xs font-bold border border-[#30203F] text-[#A1A1AA] hover:text-white disabled:opacity-40 flex items-center gap-1.5"
                  >
                    <ArrowLeft className="w-3.5 h-3.5" /> Previous
                  </button>

                  <span className="text-xs text-[#71717A] font-mono">
                    Question {currentQIndex + 1} of {activeQuiz.questions.length}
                  </span>

                  {currentQIndex < activeQuiz.questions.length - 1 ? (
                    <button
                      onClick={() => setCurrentQIndex((prev) => Math.min(activeQuiz.questions.length - 1, prev + 1))}
                      className="px-4 py-2 rounded-lg text-xs font-bold bg-[#191225] border border-[#A855F7]/40 text-white hover:bg-purple-900/40 flex items-center gap-1.5"
                    >
                      Next <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  ) : (
                    <button
                      onClick={handleSubmitQuiz}
                      disabled={submitting}
                      className="px-5 py-2 rounded-lg text-xs font-bold bg-gradient-to-r from-emerald-600 to-teal-600 text-white shadow-[0_0_15px_rgba(16,185,129,0.4)] flex items-center gap-1.5"
                    >
                      {submitting ? "Evaluating..." : "Finish & Submit"}
                    </button>
                  )}
                </div>
              )}
            </div>

            {/* Right Column: Question Navigation Palette */}
            <div className="space-y-4">
              <GlowCard className="p-4 border border-[#30203F] bg-[#100B18]/80">
                <div className="flex items-center justify-between pb-2 border-b border-[#30203F] mb-3">
                  <span className="text-xs font-bold text-white uppercase tracking-wider">
                    Question Navigation
                  </span>
                  <span className="text-[10px] text-[#A1A1AA] font-mono">
                    {answeredCount}/{activeQuiz.questions.length}
                  </span>
                </div>

                {/* Grid of Question Number Badges */}
                <div className="grid grid-cols-5 gap-2">
                  {activeQuiz.questions.map((q, idx) => {
                    const isAnswered = userAnswers[q.id] && userAnswers[q.id].trim().length > 0;
                    const isCurrent = viewMode === "single" && currentQIndex === idx;
                    const isFlagged = flaggedQuestions[q.id] || false;

                    return (
                      <button
                        key={q.id}
                        type="button"
                        onClick={() => {
                          setCurrentQIndex(idx);
                          if (viewMode === "all") setViewMode("single");
                        }}
                        className={`h-9 rounded-lg border text-xs font-bold transition-all relative flex items-center justify-center ${
                          isCurrent
                            ? "ring-2 ring-[#C084FC] border-[#A855F7] text-white bg-purple-900/60 shadow-[0_0_10px_rgba(168,85,247,0.4)]"
                            : isAnswered
                            ? "bg-purple-950/30 border-purple-500/40 text-purple-300 hover:border-purple-500"
                            : "bg-[#08060D] border-[#30203F] text-[#71717A] hover:text-white hover:border-[#30203F]"
                        }`}
                      >
                        <span>{idx + 1}</span>
                        {isFlagged && (
                          <div className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-amber-400 border border-[#08060D]" />
                        )}
                      </button>
                    );
                  })}
                </div>

                {/* Legend */}
                <div className="pt-4 border-t border-[#30203F] mt-4 space-y-1.5 text-[10px] text-[#A1A1AA]">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded bg-purple-950/40 border border-purple-500/40" />
                    <span>Answered ({answeredCount})</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded bg-[#08060D] border border-[#30203F]" />
                    <span>Unanswered ({activeQuiz.questions.length - answeredCount})</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2.5 h-2.5 rounded-full bg-amber-400" />
                    <span>Marked for Review ({Object.values(flaggedQuestions).filter(Boolean).length})</span>
                  </div>
                </div>

                {/* Submit Assessment Button */}
                <div className="pt-4 mt-2">
                  <button
                    onClick={handleSubmitQuiz}
                    disabled={submitting}
                    className="w-full py-3 rounded-xl text-xs font-bold bg-gradient-to-r from-[#8B5CF6] to-[#A855F7] hover:shadow-[0_0_20px_rgba(168,85,247,0.5)] text-white transition-all flex items-center justify-center gap-2 disabled:opacity-50"
                  >
                    {submitting ? (
                      <>
                        <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        <span>Evaluating...</span>
                      </>
                    ) : (
                      <>
                        <CheckCheck className="w-4 h-4" />
                        <span>Submit Assessment</span>
                      </>
                    )}
                  </button>
                  {answeredCount < activeQuiz.questions.length && (
                    <p className="text-[10px] text-amber-300 text-center mt-2">
                      ⚠️ {activeQuiz.questions.length - answeredCount} unanswered questions will receive 0 points.
                    </p>
                  )}
                </div>
              </GlowCard>
            </div>
          </div>
        </div>
      )}

      {/* 3. EXAMINATION RESULTS & PEDAGOGICAL REPORT CARD */}
      {quizResult && (
        <div className="max-w-4xl mx-auto space-y-6">
          {/* Main Score & Mastery Card */}
          <GlowCard glow className="p-8 text-center space-y-5 border border-[#30203F] bg-[#100B18]/80">
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-[#8B5CF6] to-[#A855F7] flex items-center justify-center mx-auto shadow-[0_0_25px_rgba(168,85,247,0.5)]">
              <Award className="w-8 h-8 text-white" />
            </div>

            <div>
              <span className="text-[10px] uppercase font-bold tracking-wider px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/30 text-[#C084FC]">
                Assessment Report Card &bull; {quizResult.mastery_status?.toUpperCase() || "EVALUATED"}
              </span>
              <h2 className="text-2xl font-extrabold text-white mt-2">Examination Evaluation Completed</h2>
            </div>

            <div className="flex items-center justify-center gap-6 pt-2">
              <div>
                <div className="text-3xl font-extrabold text-[#C084FC]">{quizResult.percentage}%</div>
                <div className="text-xs text-[#A1A1AA] mt-0.5">Final Accuracy</div>
              </div>
              <div className="w-px h-10 bg-[#30203F]" />
              <div>
                <div className="text-3xl font-extrabold text-white">
                  {quizResult.score} / {quizResult.max_score}
                </div>
                <div className="text-xs text-[#A1A1AA] mt-0.5">Points Scored</div>
              </div>
              <div className="w-px h-10 bg-[#30203F]" />
              <div>
                <div className="text-3xl font-extrabold text-white">{formatTimer(quizResult.time_taken_seconds)}</div>
                <div className="text-xs text-[#A1A1AA] mt-0.5">Time Taken</div>
              </div>
            </div>

            {/* Action Buttons: Retake, Variation, Configure */}
            <div className="pt-3 flex flex-wrap items-center justify-center gap-3">
              <button
                onClick={handleRetakeSameQuiz}
                className="px-4 py-2 rounded-xl text-xs font-bold border border-[#A855F7] bg-purple-900/30 text-white hover:bg-purple-900/50 transition-all flex items-center gap-1.5 shadow-[0_0_12px_rgba(168,85,247,0.3)]"
              >
                <RotateCcw className="w-3.5 h-3.5" /> Retake This Quiz
              </button>

              <button
                onClick={resetQuiz}
                className="px-4 py-2 rounded-xl text-xs font-bold bg-[#08060D] border border-[#30203F] text-[#A1A1AA] hover:text-white transition-all flex items-center gap-1.5"
              >
                <RefreshCw className="w-3.5 h-3.5" /> Configure New Quiz
              </button>
            </div>
          </GlowCard>

          {/* Topic Performance Breakdown (Phase 4 Requirement) */}
          {quizResult.topic_breakdown && (
            <GlowCard className="p-5 border border-[#30203F] bg-[#100B18]/70">
              <h3 className="text-xs font-bold text-white uppercase tracking-wider mb-3 flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-[#A855F7]" /> Topic-Wise Performance Breakdown
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 p-4 rounded-xl bg-[#08060D] border border-[#30203F]/60 text-xs">
                <div>
                  <div className="text-[10px] text-[#71717A] uppercase font-semibold">Evaluated Topic</div>
                  <div className="font-bold text-white mt-0.5 truncate">{quizResult.topic_breakdown.topic_name}</div>
                </div>
                <div>
                  <div className="text-[10px] text-[#71717A] uppercase font-semibold">Correct Responses</div>
                  <div className="font-bold text-emerald-400 mt-0.5">
                    {quizResult.topic_breakdown.correct_count} of {quizResult.topic_breakdown.total_questions}
                  </div>
                </div>
                <div>
                  <div className="text-[10px] text-[#71717A] uppercase font-semibold">Accuracy Rate</div>
                  <div className="font-bold text-[#C084FC] mt-0.5">{quizResult.topic_breakdown.accuracy}%</div>
                </div>
                <div>
                  <div className="text-[10px] text-[#71717A] uppercase font-semibold">Calibrated Mastery</div>
                  <div className="font-bold text-amber-300 mt-0.5 uppercase tracking-wider">
                    {quizResult.topic_breakdown.mastery_status}
                  </div>
                </div>
              </div>
            </GlowCard>
          )}

          {/* Recommended Revision Topics (Phase 4 Requirement) */}
          {quizResult.recommended_revision_topics && quizResult.recommended_revision_topics.length > 0 && (
            <GlowCard className="p-5 border border-[#30203F] bg-[#100B18]/70">
              <h3 className="text-xs font-bold text-white uppercase tracking-wider mb-3 flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-[#C084FC]" /> Recommended Revision Topics (Based on Incorrect Answers)
              </h3>
              <div className="space-y-2">
                {quizResult.recommended_revision_topics.map((rec, rIdx) => (
                  <div
                    key={rIdx}
                    className="p-3 rounded-lg bg-[#08060D] border border-[#30203F] flex items-center justify-between gap-3 text-xs"
                  >
                    <div className="flex items-center gap-2 text-gray-200">
                      <div className="w-1.5 h-1.5 rounded-full bg-amber-400 shrink-0" />
                      <span>{rec}</span>
                    </div>
                    <a
                      href={`/dashboard/notes`}
                      className="px-2.5 py-1 rounded bg-purple-500/10 border border-purple-500/30 text-[#C084FC] hover:bg-purple-500/20 text-[10px] font-bold shrink-0 transition-all"
                    >
                      Generate Notes
                    </a>
                  </div>
                ))}
              </div>
            </GlowCard>
          )}

          {/* Detailed Question-by-Question Review */}
          <div className="space-y-4">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-[#A855F7]" /> Question-by-Question Pedagogical Review
            </h3>

            {quizResult.answers.map((ans, idx) => (
              <GlowCard
                key={ans.question_id}
                className={`p-5 space-y-3 border-l-4 ${
                  ans.is_correct ? "border-l-emerald-500" : "border-l-red-500"
                } border border-[#30203F] bg-[#100B18]/80`}
              >
                <div className="flex items-start justify-between gap-4">
                  <span className="text-xs sm:text-sm font-bold text-white">
                    {idx + 1}. {ans.question_text}
                  </span>
                  <span
                    className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold shrink-0 ${
                      ans.is_correct
                        ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                        : "bg-red-500/20 text-red-400 border border-red-500/30"
                    }`}
                  >
                    {ans.is_correct ? `Correct (+${ans.score_awarded} pts)` : "Incorrect (0 pts)"}
                  </span>
                </div>

                <div className="text-xs space-y-1.5 p-3 rounded-lg bg-[#08060D] border border-[#30203F]">
                  <div className="text-[#A1A1AA]">
                    <span className="font-semibold text-white">Your Answer: </span>
                    {ans.user_response ? (
                      <span className={ans.is_correct ? "text-emerald-300" : "text-red-300"}>
                        {ans.user_response}
                      </span>
                    ) : (
                      <span className="italic text-red-400">No answer provided</span>
                    )}
                  </div>
                  <div className="text-emerald-300">
                    <span className="font-semibold text-emerald-400">Correct Answer: </span>
                    {ans.correct_answer}
                  </div>
                </div>

                {ans.explanation && (
                  <div className="text-xs text-[#A1A1AA] bg-purple-950/20 p-3 rounded-lg border border-purple-500/20">
                    <span className="font-semibold text-[#C084FC]">Explanation & Rubric: </span>
                    {ans.explanation}
                  </div>
                )}
              </GlowCard>
            ))}
          </div>
        </div>
      )}

      {/* 4. PREVIOUS ASSESSMENT ATTEMPTS (SAVED HISTORY) */}
      {!activeQuiz && history.length > 0 && (
        <div className="space-y-4 pt-6 border-t border-[#30203F]">
          <h2 className="text-sm font-bold text-white flex items-center gap-2">
            <History className="w-4 h-4 text-[#A855F7]" /> Previous Assessment Attempts ({history.length})
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {history.slice(0, 9).map((h) => (
              <div
                key={h.id}
                onClick={() => handleViewPastAttempt(h.id)}
                className="cursor-pointer group"
              >
                <GlowCard className="p-4 space-y-2 border border-[#30203F] bg-[#100B18]/70 group-hover:border-purple-500/50 transition-all group-hover:bg-[#120B1C]">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white truncate max-w-[210px]" title={h.quiz_title}>
                      {h.quiz_title}
                    </span>
                    <span
                      className={`text-[10px] font-extrabold px-2 py-0.5 rounded-full ${
                        h.percentage >= 75
                          ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                          : h.percentage >= 50
                          ? "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                          : "bg-red-500/20 text-red-400 border border-red-500/30"
                      }`}
                    >
                      {h.percentage}%
                    </span>
                  </div>
                  <div className="text-[10px] text-[#71717A] flex items-center justify-between font-mono">
                    <span>Score: {h.score} / {h.max_score}</span>
                    <span>{new Date(h.completed_at).toLocaleDateString()}</span>
                  </div>
                </GlowCard>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
