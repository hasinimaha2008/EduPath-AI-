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
  ArrowRight
} from "lucide-react";
import { GlowCard } from "@/components/GlowCard";
import { api } from "@/lib/api";
import { Quiz, QuizResult, QuizAttemptHistory, DocumentItem, Subject } from "@/lib/types";

export default function AIQuizGeneratorPage() {
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [history, setHistory] = useState<QuizAttemptHistory[]>([]);

  // Generation settings
  const [selectedTopicId, setSelectedTopicId] = useState("");
  const [selectedDocId, setSelectedDocId] = useState("");
  const [difficulty, setDifficulty] = useState("medium");
  const [questionCount, setQuestionCount] = useState(5);
  const [generating, setGenerating] = useState(false);

  // Active Quiz State
  const [activeQuiz, setActiveQuiz] = useState<Quiz | null>(null);
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
    } catch (e) {
      console.error("Error loading prerequisites:", e);
    }
  }

  const handleGenerateQuiz = async (e: React.FormEvent) => {
    e.preventDefault();
    setGenerating(true);
    setQuizResult(null);
    setUserAnswers({});
    setElapsedSeconds(0);

    try {
      const quiz = await api.generateQuiz({
        topic_id: selectedTopicId || undefined,
        document_id: selectedDocId || undefined,
        difficulty,
        question_count: questionCount,
      });
      setActiveQuiz(quiz);
    } catch (err) {
      console.error("Quiz generation error:", err);
    } finally {
      setGenerating(false);
    }
  };

  const handleSelectOption = (questionId: string, optionText: string) => {
    setUserAnswers((prev) => ({ ...prev, [questionId]: optionText }));
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
      // Reload history
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
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <CheckCircle2 className="w-5 h-5 text-[#C084FC]" /> AI Quiz Generator & Knowledge Evaluation
        </h1>
        <p className="text-xs text-[#A1A1AA] mt-0.5">
          Generate rigorous MCQ assessments from syllabus topics or uploaded documents. Answers strictly hidden until submission.
        </p>
      </div>

      {!activeQuiz ? (
        /* Setup / Generator Card */
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <GlowCard glow className="p-6 lg:col-span-2">
            <h2 className="text-base font-bold text-white mb-4 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-[#A855F7]" /> Configure Knowledge Assessment
            </h2>

            <form onSubmit={handleGenerateQuiz} className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-[11px] font-semibold text-[#A1A1AA] uppercase tracking-wider mb-1.5">
                    Select Subject & Topic
                  </label>
                  <select
                    value={selectedTopicId}
                    onChange={(e) => {
                      setSelectedTopicId(e.target.value);
                      setSelectedDocId("");
                    }}
                    className="w-full px-3 py-2 rounded-lg bg-[#100B18] border border-[#30203F] text-xs text-white focus:outline-none focus:border-[#A855F7]"
                  >
                    <option value="">Choose Curriculum Topic...</option>
                    {subjects.map((s) => (
                      <optgroup key={s.id} label={s.name}>
                        {s.topics.map((t) => (
                          <option key={t.id} value={t.id}>
                            {t.name}
                          </option>
                        ))}
                      </optgroup>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-[11px] font-semibold text-[#A1A1AA] uppercase tracking-wider mb-1.5">
                    Or Uploaded Document
                  </label>
                  <select
                    value={selectedDocId}
                    onChange={(e) => {
                      setSelectedDocId(e.target.value);
                      setSelectedTopicId("");
                    }}
                    className="w-full px-3 py-2 rounded-lg bg-[#100B18] border border-[#30203F] text-xs text-white focus:outline-none focus:border-[#A855F7]"
                  >
                    <option value="">Choose Document Source...</option>
                    {documents.map((d) => (
                      <option key={d.id} value={d.id}>
                        {d.title} ({d.file_type.toUpperCase()})
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
                <div>
                  <label className="block text-[11px] font-semibold text-[#A1A1AA] uppercase tracking-wider mb-1.5">
                    Difficulty Level
                  </label>
                  <div className="grid grid-cols-3 gap-2">
                    {["easy", "medium", "hard"].map((diff) => (
                      <button
                        key={diff}
                        type="button"
                        onClick={() => setDifficulty(diff)}
                        className={`py-2 rounded-lg text-xs font-semibold uppercase tracking-wider border transition-all ${
                          difficulty === diff
                            ? "bg-purple-900/60 border-[#A855F7] text-white shadow-[0_0_10px_rgba(168,85,247,0.4)]"
                            : "bg-[#100B18] border-[#30203F] text-[#A1A1AA] hover:text-white"
                        }`}
                      >
                        {diff}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-[11px] font-semibold text-[#A1A1AA] uppercase tracking-wider mb-1.5">
                    Question Count
                  </label>
                  <select
                    value={questionCount}
                    onChange={(e) => setQuestionCount(Number(e.target.value))}
                    className="w-full px-3 py-2 rounded-lg bg-[#100B18] border border-[#30203F] text-xs text-white focus:outline-none focus:border-[#A855F7]"
                  >
                    <option value={3}>3 Questions (Quick Check)</option>
                    <option value={5}>5 Questions (Standard Practice)</option>
                    <option value={10}>10 Questions (Comprehensive Test)</option>
                  </select>
                </div>
              </div>

              <div className="pt-4 flex justify-end">
                <button
                  type="submit"
                  disabled={generating || (!selectedTopicId && !selectedDocId)}
                  className="px-6 py-3 rounded-xl text-xs font-bold bg-gradient-to-r from-[#8B5CF6] to-[#A855F7] text-white shadow-[0_0_20px_rgba(168,85,247,0.4)] hover:shadow-[0_0_25px_rgba(168,85,247,0.7)] disabled:opacity-50 transition-all flex items-center gap-2"
                >
                  <Sparkles className="w-4 h-4" />
                  {generating ? "Generating Assessment..." : "Start AI Quiz"}
                </button>
              </div>
            </form>
          </GlowCard>

          {/* Assessment Criteria Note */}
          <GlowCard className="p-6 flex flex-col justify-between">
            <div>
              <h3 className="text-sm font-bold text-white mb-2 flex items-center gap-2">
                <Award className="w-4 h-4 text-[#C084FC]" /> Repeated Evidence Standard
              </h3>
              <p className="text-xs text-[#A1A1AA] leading-relaxed mb-4">
                The EduPath Intelligence Engine requires repeated assessment consistency before marking any academic topic as mastered:
              </p>
              <ul className="space-y-2 text-xs text-[#A1A1AA]">
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-emerald-400" />
                  <span><strong>Mastered</strong>: ≥ 90% accuracy & ≥ 3 attempts</span>
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-blue-400" />
                  <span><strong>Proficient</strong>: ≥ 75% accuracy & ≥ 2 attempts</span>
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-amber-400" />
                  <span><strong>Developing</strong>: 50% - 74% accuracy</span>
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-red-400" />
                  <span><strong>Needs Practice</strong>: &lt; 50% accuracy</span>
                </li>
              </ul>
            </div>

            <div className="pt-4 border-t border-[#30203F] text-[11px] text-[#C084FC]">
              Every submitted quiz dynamically updates your Career Intelligence and Study Schedule.
            </div>
          </GlowCard>
        </div>
      ) : !quizResult ? (
        /* Active Quiz Taking Screen */
        <div className="space-y-6 max-w-4xl mx-auto">
          {/* Status Header */}
          <div className="p-4 rounded-xl bg-[#191225] border border-[#30203F] flex items-center justify-between">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-[#A855F7] px-2 py-0.5 rounded bg-purple-500/10 border border-purple-500/30">
                {activeQuiz.difficulty} Difficulty
              </span>
              <h2 className="text-base font-bold text-white mt-1">{activeQuiz.title}</h2>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-1.5 text-xs font-mono font-bold text-[#C084FC] px-3 py-1.5 rounded-lg bg-[#100B18] border border-[#30203F]">
                <Clock className="w-3.5 h-3.5" /> {formatTime(elapsedSeconds)}
              </div>
              <button
                onClick={resetQuiz}
                className="text-xs text-[#A1A1AA] hover:text-white transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>

          {/* Question List */}
          <div className="space-y-5">
            {activeQuiz.questions.map((q, qIdx) => (
              <GlowCard key={q.id} className="p-6">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-bold text-[#A855F7]">
                    Question {qIdx + 1} of {activeQuiz.questions.length}
                  </span>
                  <span className="text-xs text-[#A1A1AA]">{q.points} pt</span>
                </div>
                <h3 className="text-sm sm:text-base font-semibold text-white mb-4">
                  {q.question_text}
                </h3>

                {/* 4 Options */}
                {q.options && q.options.length > 0 ? (
                  <div className="space-y-2">
                    {q.options.map((opt, optIdx) => {
                      const isSelected = userAnswers[q.id] === opt;
                      return (
                        <div
                          key={optIdx}
                          onClick={() => handleSelectOption(q.id, opt)}
                          className={`p-3.5 rounded-xl border text-xs sm:text-sm font-medium cursor-pointer transition-all flex items-center gap-3 ${
                            isSelected
                              ? "bg-purple-900/40 border-[#A855F7] text-white shadow-[0_0_12px_rgba(168,85,247,0.3)]"
                              : "bg-[#100B18] border-[#30203F] text-[#A1A1AA] hover:text-white hover:border-purple-500/40"
                          }`}
                        >
                          <div
                            className={`w-5 h-5 rounded-full border flex items-center justify-center text-[10px] shrink-0 ${
                              isSelected
                                ? "border-[#A855F7] bg-[#A855F7] text-white font-bold"
                                : "border-[#30203F]"
                            }`}
                          >
                            {String.fromCharCode(65 + optIdx)}
                          </div>
                          <span>{opt}</span>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <input
                    type="text"
                    value={userAnswers[q.id] || ""}
                    onChange={(e) => handleSelectOption(q.id, e.target.value)}
                    placeholder="Type your answer..."
                    className="w-full px-4 py-3 rounded-lg bg-[#100B18] border border-[#30203F] text-sm text-white focus:outline-none focus:border-[#A855F7]"
                  />
                )}
              </GlowCard>
            ))}
          </div>

          <div className="flex justify-end pt-4">
            <button
              onClick={handleSubmitQuiz}
              disabled={submitting}
              className="px-8 py-3.5 rounded-xl text-sm font-bold bg-gradient-to-r from-[#8B5CF6] to-[#A855F7] text-white shadow-[0_0_20px_rgba(168,85,247,0.4)] hover:shadow-[0_0_25px_rgba(168,85,247,0.7)] transition-all flex items-center gap-2"
            >
              <CheckCircle2 className="w-4 h-4" />
              {submitting ? "Evaluating Assessment..." : "Submit Assessment"}
            </button>
          </div>
        </div>
      ) : (
        /* Evaluation Results Screen */
        <div className="space-y-6 max-w-4xl mx-auto">
          <GlowCard glow className="p-8 text-center relative overflow-hidden">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 text-xs font-semibold mb-3 border border-emerald-500/30">
              <CheckCircle2 className="w-3.5 h-3.5" /> Assessment Evaluated & Profile Synchronized
            </div>
            <h2 className="text-3xl font-extrabold text-white mb-2">
              Score: {quizResult.score} / {quizResult.max_score} ({quizResult.percentage}%)
            </h2>
            <p className="text-xs text-[#A1A1AA] max-w-md mx-auto mb-6">
              Time Taken: {formatTime(quizResult.time_taken_seconds)}. Results have been automatically recorded into Topic Performance and Career Intelligence.
            </p>

            <button
              onClick={resetQuiz}
              className="px-6 py-2.5 rounded-xl text-xs font-bold bg-[#100B18] border border-[#30203F] hover:border-purple-500/50 text-white transition-all inline-flex items-center gap-2"
            >
              <RotateCcw className="w-3.5 h-3.5 text-[#C084FC]" /> Take Another Quiz
            </button>
          </GlowCard>

          {/* Question Breakdown with Explanations */}
          <div className="space-y-4">
            <h3 className="text-base font-bold text-white">Answer Breakdown & Explanations</h3>
            {quizResult.answers.map((ans, idx) => (
              <GlowCard key={idx} className="p-5">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-[#A855F7]">
                    Question {idx + 1}
                  </span>
                  <span
                    className={`text-xs font-bold px-2 py-0.5 rounded ${
                      ans.is_correct
                        ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                        : "bg-red-500/20 text-red-300 border border-red-500/30"
                    }`}
                  >
                    {ans.is_correct ? "Correct (+1 pt)" : "Incorrect (0 pt)"}
                  </span>
                </div>
                <h4 className="text-sm font-semibold text-white mb-3">
                  {ans.question_text}
                </h4>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs mb-3">
                  <div className="p-2.5 rounded bg-[#100B18] border border-[#30203F]">
                    <span className="text-[#A1A1AA] block text-[10px] uppercase font-semibold">
                      Your Response:
                    </span>
                    <span
                      className={`font-semibold ${
                        ans.is_correct ? "text-emerald-400" : "text-red-400"
                      }`}
                    >
                      {ans.user_response || "(No answer selected)"}
                    </span>
                  </div>

                  <div className="p-2.5 rounded bg-[#100B18] border border-[#30203F]">
                    <span className="text-[#A1A1AA] block text-[10px] uppercase font-semibold">
                      Correct Answer:
                    </span>
                    <span className="font-semibold text-white">
                      {ans.correct_answer}
                    </span>
                  </div>
                </div>

                {ans.explanation && (
                  <div className="p-3 rounded-lg bg-[#191225] border border-[#30203F] text-xs text-[#D8B4FE]">
                    <strong>Pedagogical Explanation:</strong> {ans.explanation}
                  </div>
                )}
              </GlowCard>
            ))}
          </div>
        </div>
      )}

      {/* Attempt History Table */}
      <div className="pt-6 border-t border-[#30203F]">
        <h2 className="text-base font-bold text-white mb-3 flex items-center gap-2">
          <History className="w-4 h-4 text-[#A855F7]" /> Recent Assessment History
        </h2>
        <GlowCard className="overflow-hidden">
          {history.length === 0 ? (
            <div className="p-6 text-center text-xs text-[#A1A1AA]">
              No past assessment history yet. Complete a quiz to track your progress!
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-[#100B18] text-[#A1A1AA] uppercase text-[10px] font-semibold border-b border-[#30203F]">
                  <tr>
                    <th className="px-4 py-3">Quiz Title</th>
                    <th className="px-4 py-3">Score</th>
                    <th className="px-4 py-3">Accuracy</th>
                    <th className="px-4 py-3">Time</th>
                    <th className="px-4 py-3">Completed Date</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#30203F]/60">
                  {history.map((h) => (
                    <tr key={h.id} className="hover:bg-[#100B18]/40 transition-colors">
                      <td className="px-4 py-3 font-semibold text-white">{h.quiz_title}</td>
                      <td className="px-4 py-3 text-white">
                        {h.score} / {h.max_score}
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className={`font-bold ${
                            h.percentage >= 75
                              ? "text-emerald-400"
                              : h.percentage >= 50
                              ? "text-amber-400"
                              : "text-red-400"
                          }`}
                        >
                          {h.percentage}%
                        </span>
                      </td>
                      <td className="px-4 py-3 text-[#A1A1AA]">{formatTime(h.time_taken_seconds)}</td>
                      <td className="px-4 py-3 text-[#A1A1AA]">
                        {new Date(h.completed_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </GlowCard>
      </div>
    </div>
  );
}
