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
  Code,
  CheckSquare,
  FileText,
  Briefcase,
  Terminal,
  Zap,
  Flame,
  ChevronRight,
  Layers,
  Check
} from "lucide-react";
import { GlowCard } from "@/components/GlowCard";
import { api } from "@/lib/api";
import { Quiz, QuizResult, QuizAttemptHistory, DocumentItem, Subject, Topic, Question } from "@/lib/types";

const QUESTION_TYPES = [
  { id: "mcq", label: "Multiple Choice (MCQ)", desc: "Standard 4-option single correct answer", icon: CheckCircle2 },
  { id: "multiple_select", label: "Multiple Select (MSQ)", desc: "Select all correct statements", icon: CheckSquare },
  { id: "short_answer", label: "Short Answer", desc: "Concise technical definitions & formulas", icon: FileText },
  { id: "long_answer", label: "Long Answer", desc: "In-depth architectural breakdowns", icon: Layers },
  { id: "technical_interview", label: "Technical Interview", desc: "Real FAANG/system design interview questions", icon: Briefcase },
  { id: "programming", label: "Programming Problem", desc: "Coding challenge with starter code & test cases", icon: Terminal },
  { id: "scenario_based", label: "Scenario-Based", desc: "Production incidents & engineering dilemmas", icon: AlertCircle },
  { id: "application_oriented", label: "Application-Oriented", desc: "Real-world cloud & enterprise case studies", icon: Zap },
];

const DIFFICULTY_LEVELS = [
  { id: "beginner", label: "Beginner", desc: "Foundational concepts & syntax", color: "text-emerald-400 border-emerald-500/30 bg-emerald-500/10" },
  { id: "intermediate", label: "Intermediate", desc: "Architectural & problem-solving depth", color: "text-purple-400 border-purple-500/30 bg-purple-500/10" },
  { id: "advanced", label: "Advanced", desc: "Edge cases, scale & optimization", color: "text-rose-400 border-rose-500/30 bg-rose-500/10" },
];

export default function AIQuizGeneratorPage() {
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [history, setHistory] = useState<QuizAttemptHistory[]>([]);
  const [loadingPrereqs, setLoadingPrereqs] = useState(true);

  // Workflow Selection State
  const [selectedSubjectId, setSelectedSubjectId] = useState<string>("");
  const [selectedTopicId, setSelectedTopicId] = useState<string>("");
  const [selectedSubtopic, setSelectedSubtopic] = useState<string>("");
  const [selectedDocId, setSelectedDocId] = useState<string>("");
  const [selectedQuestionType, setSelectedQuestionType] = useState<string>("mcq");
  const [difficulty, setDifficulty] = useState<string>("intermediate");
  const [questionCount, setQuestionCount] = useState<number>(5);
  const [generating, setGenerating] = useState(false);

  // Active Quiz State
  const [activeQuiz, setActiveQuiz] = useState<Quiz | null>(null);
  // userAnswers maps questionId -> string response (or comma-separated for MSQ)
  const [userAnswers, setUserAnswers] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [quizResult, setQuizResult] = useState<QuizResult | null>(null);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  useEffect(() => {
    loadPrerequisites();
  }, []);

  // Timer while quiz is active
  useEffect(() => {
    let interval: any;
    if (activeQuiz && !quizResult) {
      interval = setInterval(() => {
        setElapsedSeconds((prev) => prev + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [activeQuiz, quizResult]);

  async function loadPrerequisites() {
    try {
      const [subs, docs, hist] = await Promise.all([
        api.getSubjects().catch(() => []),
        api.listDocuments().catch(() => []),
        api.getQuizHistory().catch(() => []),
      ]);
      setSubjects(subs);
      setDocuments(docs.filter((d) => d.status === "ready"));
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

  // Current selected subject object
  const currentSubject = subjects.find((s) => s.id === selectedSubjectId);
  // Topics strictly belonging to the selected subject!
  const availableTopics = currentSubject?.topics || [];
  // Currently selected topic
  const currentTopic = availableTopics.find((t) => t.id === selectedTopicId);
  // Subtopics for the selected topic
  const availableSubtopics = currentTopic?.subtopics || [];

  const handleSubjectChange = (subjectId: string) => {
    setSelectedSubjectId(subjectId);
    setSelectedTopicId("");
    setSelectedSubtopic("");
    setSelectedDocId("");
  };

  const handleTopicChange = (topicId: string) => {
    setSelectedTopicId(topicId);
    setSelectedSubtopic("");
    setSelectedDocId("");
  };

  const handleGenerateQuiz = async (e: React.FormEvent) => {
    e.preventDefault();
    setGenerating(true);
    setQuizResult(null);
    setUserAnswers({});
    setElapsedSeconds(0);

    try {
      const quiz = await api.generateQuiz({
        subject_id: selectedSubjectId || undefined,
        topic_id: selectedTopicId || undefined,
        subtopic: selectedSubtopic || undefined,
        document_id: selectedDocId || undefined,
        difficulty,
        question_count: questionCount,
        question_types: [selectedQuestionType],
      });
      setActiveQuiz(quiz);
    } catch (err) {
      console.error("Quiz generation error:", err);
    } finally {
      setGenerating(false);
    }
  };

  // Multiple Choice handler
  const handleSelectOption = (questionId: string, optionText: string) => {
    setUserAnswers((prev) => ({ ...prev, [questionId]: optionText }));
  };

  // Multiple Select handler
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

  // Text response handler (Short answer, Long answer, Interview, Programming)
  const handleTextResponse = (questionId: string, text: string) => {
    setUserAnswers((prev) => ({ ...prev, [questionId]: text }));
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
        time_taken_seconds: elapsedSeconds,
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

  const resetQuiz = () => {
    setActiveQuiz(null);
    setQuizResult(null);
    setUserAnswers({});
    setElapsedSeconds(0);
  };

  const formatTime = (secs: number) => {
    const mins = Math.floor(secs / 60);
    const rem = secs % 60;
    return `${mins}:${rem < 10 ? "0" : ""}${rem}`;
  };

  return (
    <div className="space-y-8">
      {/* Page Title & Tagline */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-[#C084FC]" /> AI Question Generator & Knowledge Evaluation
          </h1>
          <p className="text-xs text-[#A1A1AA] mt-0.5">
            Select across 16 subjects, configure 8 question types, practice with real evaluation, and build verified academic mastery.
          </p>
        </div>

        {activeQuiz && !quizResult && (
          <div className="flex items-center gap-3 bg-[#191225] border border-[#30203F] px-3.5 py-1.5 rounded-xl">
            <Clock className="w-4 h-4 text-[#C084FC] animate-pulse" />
            <span className="font-mono text-sm font-bold text-white">{formatTime(elapsedSeconds)}</span>
          </div>
        )}
      </div>

      {!activeQuiz ? (
        /* Configuration Workflow */
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <GlowCard glow className="p-6 lg:col-span-2 space-y-6">
            <div className="flex items-center justify-between border-b border-[#30203F] pb-4">
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-[#A855F7]" /> Question Generation Workflow
              </h2>
              <span className="text-xs text-[#C084FC] font-semibold bg-[#8B5CF6]/20 px-2.5 py-0.5 rounded-full border border-[#A855F7]/30">
                16 Subjects Available
              </span>
            </div>

            <form onSubmit={handleGenerateQuiz} className="space-y-5">
              {/* Step 1: Subject Selection */}
              <div>
                <label className="block text-xs font-semibold text-[#A1A1AA] uppercase tracking-wider mb-2">
                  1. Select Academic Subject
                </label>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 max-h-48 overflow-y-auto pr-1">
                  {subjects.map((sub) => {
                    const isSelected = sub.id === selectedSubjectId;
                    return (
                      <button
                        key={sub.id}
                        type="button"
                        onClick={() => handleSubjectChange(sub.id)}
                        className={`text-left p-2.5 rounded-xl border text-xs transition-all ${
                          isSelected
                            ? "bg-gradient-to-r from-purple-900/60 to-purple-800/40 text-white border-[#A855F7] shadow-[0_0_15px_-3px_rgba(168,85,247,0.4)]"
                            : "bg-[#100B18] text-[#A1A1AA] border-[#30203F] hover:border-[#8B5CF6]/50 hover:text-white"
                        }`}
                      >
                        <div className="font-bold truncate text-[12px]">{sub.name}</div>
                        <div className="text-[10px] text-[#A1A1AA] mt-0.5 truncate">{sub.code || sub.category}</div>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Step 2: Topic & Subtopic Selection */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-[#A1A1AA] uppercase tracking-wider mb-1.5">
                    2. Select Topic ({currentSubject?.name || "Subject"})
                  </label>
                  <select
                    value={selectedTopicId}
                    onChange={(e) => handleTopicChange(e.target.value)}
                    required={!selectedDocId}
                    className="w-full px-3 py-2.5 rounded-xl bg-[#100B18] border border-[#30203F] text-xs text-white focus:outline-none focus:border-[#A855F7]"
                  >
                    <option value="">Choose Topic from {currentSubject?.name || "Subject"}...</option>
                    {availableTopics.map((t) => (
                      <option key={t.id} value={t.id}>
                        {t.is_emerging ? "⚡ [Emerging] " : ""}{t.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-[#A1A1AA] uppercase tracking-wider mb-1.5">
                    Subtopic (Optional Focus)
                  </label>
                  <select
                    value={selectedSubtopic}
                    onChange={(e) => setSelectedSubtopic(e.target.value)}
                    disabled={!currentTopic || availableSubtopics.length === 0}
                    className="w-full px-3 py-2.5 rounded-xl bg-[#100B18] border border-[#30203F] text-xs text-white focus:outline-none focus:border-[#A855F7] disabled:opacity-50"
                  >
                    <option value="">All Module Concepts (Comprehensive)</option>
                    {availableSubtopics.map((st, i) => (
                      <option key={i} value={st}>
                        {st}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Step 3: Question Types (8 Types) */}
              <div>
                <label className="block text-xs font-semibold text-[#A1A1AA] uppercase tracking-wider mb-2">
                  3. Question Type
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
                            : "bg-[#100B18] border-[#30203F] text-[#A1A1AA] hover:border-purple-500/40 hover:text-white"
                        }`}
                      >
                        <div className="flex items-center gap-2 mb-1">
                          <Icon className={`w-3.5 h-3.5 ${isSelected ? "text-[#C084FC]" : "text-[#A1A1AA]"}`} />
                          <span className="font-bold">{type.label}</span>
                        </div>
                        <p className="text-[10px] text-[#A1A1AA] line-clamp-1">{type.desc}</p>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Step 4 & 5: Difficulty & Question Count */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-[#A1A1AA] uppercase tracking-wider mb-2">
                    4. Difficulty Level
                  </label>
                  <div className="grid grid-cols-3 gap-2">
                    {DIFFICULTY_LEVELS.map((lvl) => {
                      const isSelected = difficulty === lvl.id;
                      return (
                        <button
                          key={lvl.id}
                          type="button"
                          onClick={() => setDifficulty(lvl.id)}
                          className={`py-2 px-3 rounded-xl text-xs font-bold border transition-all text-center ${
                            isSelected
                              ? lvl.color + " shadow-[0_0_12px_rgba(168,85,247,0.3)] ring-1 ring-[#A855F7]"
                              : "bg-[#100B18] border-[#30203F] text-[#A1A1AA] hover:text-white"
                          }`}
                        >
                          {lvl.label}
                        </button>
                      );
                    })}
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-[#A1A1AA] uppercase tracking-wider mb-2">
                    5. Question Count ({questionCount} questions)
                  </label>
                  <input
                    type="range"
                    min={1}
                    max={10}
                    value={questionCount}
                    onChange={(e) => setQuestionCount(Number(e.target.value))}
                    className="w-full accent-[#A855F7] bg-[#100B18] rounded-lg cursor-pointer h-2 mt-2"
                  />
                  <div className="flex justify-between text-[10px] text-[#A1A1AA] mt-1 font-mono">
                    <span>1</span>
                    <span>3</span>
                    <span>5 (Recommended)</span>
                    <span>10</span>
                  </div>
                </div>
              </div>

              {/* Generate Button */}
              <button
                type="submit"
                disabled={generating || (!selectedTopicId && !selectedDocId)}
                className="w-full py-3.5 rounded-xl text-sm font-bold bg-gradient-to-r from-[#8B5CF6] via-[#A855F7] to-[#C084FC] hover:shadow-[0_0_25px_rgba(168,85,247,0.6)] text-white transition-all flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {generating ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span>AI Generating Rigorous Assessment...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    <span>Generate AI Questions Now</span>
                  </>
                )}
              </button>
            </form>
          </GlowCard>

          {/* Right Column: Active Subject Syllabus Overview */}
          <div className="space-y-4">
            <GlowCard className="p-5">
              <h3 className="text-xs font-bold text-white uppercase tracking-wider mb-3 flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-[#C084FC]" /> Active Subject Syllabus
              </h3>
              {currentSubject ? (
                <div className="space-y-2.5">
                  <div className="text-sm font-bold text-white">{currentSubject.name}</div>
                  <p className="text-xs text-[#A1A1AA] leading-relaxed">{currentSubject.description}</p>
                  <div className="pt-2 border-t border-[#30203F] space-y-1.5">
                    <div className="text-[11px] font-semibold text-[#C084FC]">
                      {availableTopics.length} Academic Modules / Topics:
                    </div>
                    <ul className="text-xs space-y-1 text-[#A1A1AA] max-h-48 overflow-y-auto pr-1">
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
                <p className="text-xs text-[#A1A1AA]">Select a subject to view its syllabus breakdown.</p>
              )}
            </GlowCard>

            <GlowCard className="p-5">
              <h3 className="text-xs font-bold text-white uppercase tracking-wider mb-3 flex items-center gap-2">
                <Award className="w-4 h-4 text-emerald-400" /> Mastery Evidence Rules
              </h3>
              <p className="text-xs text-[#A1A1AA] leading-relaxed">
                EduPath Intelligence Engine evaluates evidence consistently across assessments. Scores dynamically update topic mastery and calibrate industry career recommendations.
              </p>
            </GlowCard>
          </div>
        </div>
      ) : (
        /* Active Quiz Taking Interface */
        <div className="max-w-4xl mx-auto space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-2xl bg-[#191225] border border-[#30203F]">
            <div>
              <span className="text-xs font-semibold text-[#C084FC] uppercase tracking-wider">
                Active Assessment &bull; {activeQuiz.difficulty.toUpperCase()}
              </span>
              <h2 className="text-lg font-bold text-white">{activeQuiz.title}</h2>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-xs text-[#A1A1AA]">{activeQuiz.questions.length} Questions</span>
              <button
                onClick={resetQuiz}
                className="px-3 py-1.5 rounded-lg text-xs font-bold text-[#A1A1AA] hover:text-white bg-[#100B18] border border-[#30203F] hover:border-red-500/40 transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>

          {/* Question List */}
          <div className="space-y-6">
            {activeQuiz.questions.map((q, qIndex) => {
              const qType = q.question_type || "mcq";
              const currentVal = userAnswers[q.id] || "";

              return (
                <GlowCard key={q.id} className="p-6 space-y-4">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex items-center gap-2">
                      <span className="w-7 h-7 rounded-lg bg-gradient-to-br from-[#8B5CF6] to-[#A855F7] flex items-center justify-center text-xs font-bold text-white shrink-0">
                        {qIndex + 1}
                      </span>
                      <span className="text-[11px] font-semibold uppercase px-2 py-0.5 rounded bg-purple-500/20 text-[#C084FC] border border-[#A855F7]/30">
                        {qType.replace("_", " ")} &bull; {q.points} {q.points === 1 ? "pt" : "pts"}
                      </span>
                    </div>
                  </div>

                  <p className="text-sm sm:text-base font-semibold text-white leading-relaxed">
                    {q.question_text}
                  </p>

                  {/* MCQ (Single Select) */}
                  {qType === "mcq" && q.options && (
                    <div className="space-y-2.5 pt-2">
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
                                : "bg-[#100B18] border-[#30203F] text-[#A1A1AA] hover:border-[#8B5CF6]/50 hover:text-white"
                            }`}
                          >
                            <span>{opt}</span>
                            <div className={`w-4 h-4 rounded-full border flex items-center justify-center shrink-0 ml-3 ${
                              isSelected ? "border-[#A855F7] bg-[#A855F7]" : "border-[#30203F]"
                            }`}>
                              {isSelected && <div className="w-1.5 h-1.5 rounded-full bg-white" />}
                            </div>
                          </button>
                        );
                      })}
                    </div>
                  )}

                  {/* MSQ (Multiple Select) */}
                  {qType === "multiple_select" && q.options && (
                    <div className="space-y-2.5 pt-2">
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
                                : "bg-[#100B18] border-[#30203F] text-[#A1A1AA] hover:border-[#8B5CF6]/50 hover:text-white"
                            }`}
                          >
                            <span>{opt}</span>
                            <div className={`w-4 h-4 rounded-md border flex items-center justify-center shrink-0 ml-3 ${
                              isSelected ? "border-[#A855F7] bg-[#A855F7]" : "border-[#30203F]"
                            }`}>
                              {isSelected && <Check className="w-3 h-3 text-white" />}
                            </div>
                          </button>
                        );
                      })}
                    </div>
                  )}

                  {/* Programming Question */}
                  {qType === "programming" && (
                    <div className="space-y-3 pt-2">
                      {q.test_cases && q.test_cases.length > 0 && (
                        <div className="p-3 rounded-lg bg-[#100B18] border border-[#30203F] text-xs font-mono text-[#A1A1AA]">
                          <span className="text-[#C084FC] font-bold block mb-1">Example Test Cases:</span>
                          {q.test_cases.map((tc, tcIdx) => (
                            <div key={tcIdx}>{tc}</div>
                          ))}
                        </div>
                      )}
                      <div>
                        <label className="block text-[11px] font-semibold text-[#A1A1AA] uppercase tracking-wider mb-1.5">
                          Implement Solution (Python / Code Editor)
                        </label>
                        <textarea
                          rows={8}
                          value={currentVal || q.code_snippet || ""}
                          onChange={(e) => handleTextResponse(q.id, e.target.value)}
                          placeholder="Write your algorithmic solution here..."
                          className="w-full p-3.5 rounded-xl bg-[#08060D] border border-[#30203F] font-mono text-xs sm:text-sm text-purple-200 focus:outline-none focus:border-[#A855F7] focus:ring-1 focus:ring-[#A855F7]"
                        />
                      </div>
                    </div>
                  )}

                  {/* Open-Ended / Short Answer / Long Answer / Interview / Scenario */}
                  {["short_answer", "long_answer", "technical_interview", "scenario_based", "application_oriented"].includes(qType) && (
                    <div className="space-y-2 pt-2">
                      <label className="block text-[11px] font-semibold text-[#A1A1AA] uppercase tracking-wider">
                        Your Technical Response
                      </label>
                      <textarea
                        rows={qType === "long_answer" || qType === "technical_interview" ? 6 : 3}
                        value={currentVal}
                        onChange={(e) => handleTextResponse(q.id, e.target.value)}
                        placeholder={
                          qType === "short_answer"
                            ? "Provide a clear 1-2 sentence response with technical definitions..."
                            : qType === "technical_interview"
                            ? "Structure your answer highlighting trade-offs, scalability, and system bottlenecks..."
                            : "Provide your step-by-step reasoning and solution..."
                        }
                        className="w-full p-3.5 rounded-xl bg-[#100B18] border border-[#30203F] text-xs sm:text-sm text-white focus:outline-none focus:border-[#A855F7] focus:ring-1 focus:ring-[#A855F7]"
                      />
                    </div>
                  )}
                </GlowCard>
              );
            })}
          </div>

          {/* Submit Quiz Action */}
          <div className="flex items-center justify-end gap-4 p-5 rounded-2xl bg-[#191225] border border-[#30203F]">
            <span className="text-xs text-[#A1A1AA]">
              {Object.keys(userAnswers).length} of {activeQuiz.questions.length} answered
            </span>
            <button
              onClick={handleSubmitQuiz}
              disabled={submitting}
              className="px-6 py-3 rounded-xl text-xs sm:text-sm font-bold bg-gradient-to-r from-[#8B5CF6] to-[#A855F7] hover:shadow-[0_0_20px_rgba(168,85,247,0.6)] text-white transition-all flex items-center gap-2 disabled:opacity-50"
            >
              {submitting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Evaluating Answers with Intelligence Engine...</span>
                </>
              ) : (
                <>
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Submit Assessment for Evaluation</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Quiz Results Modal / View */}
      {quizResult && (
        <div className="max-w-4xl mx-auto space-y-6">
          <GlowCard glow className="p-8 text-center space-y-4">
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-[#8B5CF6] to-[#A855F7] flex items-center justify-center mx-auto shadow-[0_0_25px_rgba(168,85,247,0.5)]">
              <Award className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-2xl font-extrabold text-white">Assessment Evaluation Completed</h2>
            <div className="flex items-center justify-center gap-6 pt-2">
              <div>
                <div className="text-3xl font-extrabold text-[#C084FC]">{quizResult.percentage}%</div>
                <div className="text-xs text-[#A1A1AA]">Overall Score</div>
              </div>
              <div className="w-px h-10 bg-[#30203F]" />
              <div>
                <div className="text-3xl font-extrabold text-white">
                  {quizResult.score} / {quizResult.max_score}
                </div>
                <div className="text-xs text-[#A1A1AA]">Points Awarded</div>
              </div>
              <div className="w-px h-10 bg-[#30203F]" />
              <div>
                <div className="text-3xl font-extrabold text-white">{formatTime(quizResult.time_taken_seconds)}</div>
                <div className="text-xs text-[#A1A1AA]">Time Taken</div>
              </div>
            </div>

            <div className="pt-4 flex justify-center gap-3">
              <button
                onClick={resetQuiz}
                className="px-5 py-2.5 rounded-xl text-xs font-bold bg-gradient-to-r from-[#8B5CF6] to-[#A855F7] text-white shadow-[0_0_15px_rgba(168,85,247,0.4)]"
              >
                Configure New Quiz
              </button>
            </div>
          </GlowCard>

          {/* Detailed Question Review */}
          <div className="space-y-4">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-[#A855F7]" /> Question-by-Question Pedagogical Review
            </h3>

            {quizResult.answers.map((ans, idx) => (
              <GlowCard
                key={ans.question_id}
                className={`p-5 space-y-3 border-l-4 ${
                  ans.is_correct ? "border-l-emerald-500" : "border-l-red-500"
                }`}
              >
                <div className="flex items-start justify-between gap-4">
                  <span className="text-sm font-bold text-white">
                    {idx + 1}. {ans.question_text}
                  </span>
                  <span
                    className={`px-2.5 py-1 rounded-full text-[11px] font-bold shrink-0 ${
                      ans.is_correct
                        ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                        : "bg-red-500/20 text-red-400 border border-red-500/30"
                    }`}
                  >
                    {ans.is_correct ? "Correct (+ " + ans.score_awarded + " pts)" : "Incorrect (0 pts)"}
                  </span>
                </div>

                <div className="text-xs space-y-1.5 p-3 rounded-lg bg-[#100B18] border border-[#30203F]">
                  <div className="text-[#A1A1AA]">
                    <span className="font-semibold text-white">Your Answer: </span>
                    {ans.user_response || <span className="italic text-red-400">None provided</span>}
                  </div>
                  <div className="text-emerald-300">
                    <span className="font-semibold text-emerald-400">Reference Key: </span>
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

      {/* Attempt History Section */}
      {!activeQuiz && history.length > 0 && (
        <div className="space-y-4 pt-6 border-t border-[#30203F]">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <History className="w-4 h-4 text-[#A855F7]" /> Previous Assessment Attempts
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {history.slice(0, 6).map((h) => (
              <GlowCard key={h.id} className="p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-white truncate max-w-[200px]" title={h.quiz_title}>
                    {h.quiz_title}
                  </span>
                  <span
                    className={`text-xs font-extrabold px-2 py-0.5 rounded-full ${
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
                <div className="text-[11px] text-[#A1A1AA] flex items-center justify-between">
                  <span>Score: {h.score} / {h.max_score}</span>
                  <span>{new Date(h.completed_at).toLocaleDateString()}</span>
                </div>
              </GlowCard>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
