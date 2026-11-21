"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  AlertTriangle,
  Lightbulb,
  CheckCircle2,
  TrendingUp,
  RotateCcw,
  BookOpen,
  Filter,
  ArrowRight,
  ShieldAlert,
  HelpCircle,
  Code,
  Zap,
  Info
} from "lucide-react";
import { api } from "@/lib/api";
import { MistakeInsights, QuizMistakeItem } from "@/lib/types";

export default function LearningInsightsPage() {
  const [insights, setInsights] = useState<MistakeInsights | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>("all");

  useEffect(() => {
    fetchInsights();
  }, []);

  const fetchInsights = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getMistakes();
      setInsights(data);
    } catch (err: any) {
      setError(err.message || "Failed to load learning insights.");
    } finally {
      setLoading(false);
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case "conceptual_misunderstanding":
        return "text-purple-400 bg-purple-500/10 border-purple-500/30";
      case "incorrect_application":
        return "text-amber-400 bg-amber-500/10 border-amber-500/30";
      case "calculation_error":
        return "text-cyan-400 bg-cyan-500/10 border-cyan-500/30";
      case "misinterpretation":
        return "text-rose-400 bg-rose-500/10 border-rose-500/30";
      case "knowledge_gap":
        return "text-orange-400 bg-orange-500/10 border-orange-500/30";
      default:
        return "text-zinc-400 bg-zinc-500/10 border-zinc-500/30";
    }
  };

  const filteredMistakes = insights?.recent_mistakes.filter(m =>
    selectedCategory === "all" || m.error_category === selectedCategory
  ) || [];

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#30203F] pb-6">
        <div>
          <div className="flex items-center gap-2.5">
            <div className="p-2.5 rounded-xl bg-purple-500/10 border border-purple-500/30 text-purple-400 shadow-[0_0_15px_rgba(168,85,247,0.25)]">
              <Lightbulb className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
                AI Learning Insights & Mistake Analysis
                <span className="px-2 py-0.5 rounded-full bg-purple-500/20 text-[#C084FC] text-xs font-semibold">
                  Cognitive Profiler
                </span>
              </h1>
              <p className="text-sm text-[#A1A1AA] mt-0.5">
                Analyzes student error patterns, detects repeated misconceptions, and guides evidence-backed recovery.
              </p>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={fetchInsights}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-[#191225] border border-[#30203F] text-xs font-semibold text-white hover:border-[#8B5CF6] transition-all"
          >
            <RotateCcw className="w-3.5 h-3.5 text-[#C084FC]" />
            Refresh Analysis
          </button>
          <Link
            href="/dashboard/workspace"
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-[#8B5CF6] to-[#A855F7] text-xs font-bold text-white shadow-[0_0_15px_rgba(168,85,247,0.35)] hover:shadow-[0_0_22px_rgba(168,85,247,0.6)] transition-all"
          >
            <span>Open Learning Workspace</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 animate-pulse">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-28 bg-[#160F23] rounded-2xl border border-[#30203F]" />
          ))}
        </div>
      ) : error ? (
        <div className="p-6 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300">
          <p className="font-semibold text-sm">Failed to load insights</p>
          <p className="text-xs mt-1 text-rose-400">{error}</p>
        </div>
      ) : (
        <>
          {/* Top KPI Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            <div className="p-5 rounded-2xl bg-[#160F23] border border-[#30203F] hover:border-purple-500/50 transition-all">
              <span className="text-xs font-medium text-[#A1A1AA] uppercase tracking-wider block">Total Mistakes Evaluated</span>
              <p className="text-3xl font-extrabold text-white mt-2">{insights?.total_mistakes || 0}</p>
              <span className="text-[11px] text-[#71717A] mt-1 block">Indexed across quizzes</span>
            </div>

            <div className="p-5 rounded-2xl bg-[#160F23] border border-[#30203F] hover:border-amber-500/50 transition-all">
              <span className="text-xs font-medium text-[#A1A1AA] uppercase tracking-wider block">Repeated Mistakes</span>
              <div className="flex items-center gap-2 mt-2">
                <p className={`text-3xl font-extrabold ${insights?.repeated_mistakes_count ? "text-amber-400" : "text-emerald-400"}`}>
                  {insights?.repeated_mistakes_count || 0}
                </p>
                {insights && insights.repeated_mistakes_count > 0 && (
                  <span className="px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 text-[10px] font-bold">
                    Action Needed
                  </span>
                )}
              </div>
              <span className="text-[11px] text-[#71717A] mt-1 block">Misconceptions recurring &gt; 1 time</span>
            </div>

            <div className="p-5 rounded-2xl bg-[#160F23] border border-[#30203F] hover:border-emerald-500/50 transition-all">
              <span className="text-xs font-medium text-[#A1A1AA] uppercase tracking-wider block">Improvement Trend</span>
              <div className="flex items-center gap-2 mt-2">
                <TrendingUp className="w-5 h-5 text-emerald-400" />
                <p className="text-3xl font-extrabold text-emerald-400">
                  {insights?.improvement_rate ? `${insights.improvement_rate > 0 ? "+" : ""}${insights.improvement_rate}%` : "0%"}
                </p>
              </div>
              <span className="text-[11px] text-[#71717A] mt-1 block">Score delta across quiz attempts</span>
            </div>

            <div className="p-5 rounded-2xl bg-[#160F23] border border-[#30203F] hover:border-[#8B5CF6]/50 transition-all">
              <span className="text-xs font-medium text-[#A1A1AA] uppercase tracking-wider block">Primary Remediation Area</span>
              <p className="text-sm font-bold text-white mt-2 truncate">
                {insights?.category_distribution?.[0]?.label || "General Mastery"}
              </p>
              <span className="text-[11px] text-[#A855F7] mt-1 block">Auto-targeted in next practice</span>
            </div>
          </div>

          {/* Actionable Pedagogical Advice Banner */}
          {insights?.actionable_advice && (
            <div className="p-5 rounded-2xl bg-gradient-to-r from-purple-950/40 via-[#1C142D] to-purple-950/40 border border-purple-500/40 shadow-[0_0_25px_rgba(168,85,247,0.15)] flex items-start gap-4">
              <div className="p-2.5 rounded-xl bg-purple-500/20 text-purple-300">
                <Zap className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">AI Pedagogical Guidance</h3>
                <p className="text-xs text-[#D4D4D8] mt-1 leading-relaxed">{insights.actionable_advice}</p>
              </div>
            </div>
          )}

          {/* Error Category Distribution */}
          <div className="p-6 rounded-2xl bg-[#160F23] border border-[#30203F]">
            <h2 className="text-base font-bold text-white mb-4 flex items-center justify-between">
              <span>Cognitive Error Category Breakdown</span>
              <span className="text-xs font-normal text-[#A1A1AA]">6 Standardized Classifications</span>
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {insights?.category_distribution.map((cat) => {
                const total = insights.total_mistakes || 1;
                const pct = Math.round((cat.count / total) * 100);
                return (
                  <div
                    key={cat.category}
                    onClick={() => setSelectedCategory(selectedCategory === cat.category ? "all" : cat.category)}
                    className={`p-4 rounded-xl border transition-all cursor-pointer ${
                      selectedCategory === cat.category
                        ? "bg-[#251A38] border-[#A855F7] shadow-[0_0_15px_rgba(168,85,247,0.3)]"
                        : "bg-[#1B1328] border-[#30203F] hover:border-[#8B5CF6]/40"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-white">{cat.label}</span>
                      <span className="text-xs font-extrabold text-[#C084FC]">{cat.count} error{cat.count !== 1 ? "s" : ""}</span>
                    </div>
                    <div className="w-full bg-[#100B18] h-2 rounded-full mt-3 overflow-hidden">
                      <div
                        className="bg-gradient-to-r from-[#8B5CF6] to-[#C084FC] h-full rounded-full transition-all"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                    <div className="flex items-center justify-between mt-2 text-[10px] text-[#A1A1AA]">
                      <span>{pct}% of evaluated mistakes</span>
                      <span className="text-[#A855F7]">Filter by type →</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Repeated Mistakes Priority Alert */}
          {insights && insights.repeated_mistakes.length > 0 && (
            <div className="p-6 rounded-2xl bg-amber-500/5 border border-amber-500/30">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <ShieldAlert className="w-5 h-5 text-amber-400" />
                  <h2 className="text-base font-bold text-white">
                    Priority Alert: Repeated Misconceptions ({insights.repeated_mistakes.length})
                  </h2>
                </div>
                <span className="text-xs text-amber-400 font-medium">Multiple occurrences detected</span>
              </div>

              <div className="space-y-3">
                {insights.repeated_mistakes.map((rm) => (
                  <div key={rm.id} className="p-4 rounded-xl bg-[#191225] border border-amber-500/20 flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-white">{rm.topic_name}</span>
                        <span className="px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 text-[10px] font-bold">
                          Occurred {rm.repeated_count} times
                        </span>
                      </div>
                      <p className="text-xs text-[#A1A1AA] line-clamp-1">{rm.question_text}</p>
                      <p className="text-xs text-amber-300/90 font-medium mt-1">Suggested fix: {rm.suggested_fix}</p>
                    </div>
                    <Link
                      href="/dashboard/workspace"
                      className="shrink-0 px-3 py-1.5 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-300 hover:bg-amber-500/20 text-xs font-semibold transition-all text-center"
                    >
                      Remediate in Workspace →
                    </Link>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Detailed Mistake Log */}
          <div className="p-6 rounded-2xl bg-[#160F23] border border-[#30203F] space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#30203F]">
              <div>
                <h2 className="text-base font-bold text-white">Recent Mistake Log & Explanations</h2>
                <p className="text-xs text-[#A1A1AA]">Examine your exact submissions against reference answers and grading feedback.</p>
              </div>

              {/* Filter */}
              <div className="flex items-center gap-2">
                <Filter className="w-3.5 h-3.5 text-[#A1A1AA]" />
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="px-3 py-1.5 rounded-lg bg-[#191225] border border-[#30203F] text-xs text-white focus:outline-none focus:border-[#8B5CF6]"
                >
                  <option value="all">All Error Types</option>
                  <option value="conceptual_misunderstanding">Conceptual Misunderstanding</option>
                  <option value="incorrect_application">Incorrect Application</option>
                  <option value="calculation_error">Calculation Error</option>
                  <option value="misinterpretation">Misinterpretation</option>
                  <option value="knowledge_gap">Knowledge Gap</option>
                </select>
              </div>
            </div>

            {filteredMistakes.length === 0 ? (
              <div className="text-center py-12 text-[#71717A] text-xs">
                No mistakes recorded for this filter. Great work!
              </div>
            ) : (
              <div className="space-y-4">
                {filteredMistakes.map((m) => (
                  <div key={m.id} className="p-5 rounded-xl bg-[#1B1328] border border-[#30203F] space-y-3">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-white">{m.topic_name}</span>
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${getCategoryColor(m.error_category)}`}>
                          {m.error_category.replace('_', ' ').toUpperCase()}
                        </span>
                        {m.repeated_count > 1 && (
                          <span className="px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 text-[10px] font-bold">
                            {m.repeated_count}x Repeated
                          </span>
                        )}
                      </div>
                      <span className="text-[10px] text-[#71717A]">
                        {new Date(m.created_at).toLocaleDateString()}
                      </span>
                    </div>

                    <p className="text-xs font-medium text-white">{m.question_text}</p>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                      <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-300">
                        <span className="text-[10px] uppercase font-bold text-rose-400 block mb-1">Your Submission:</span>
                        <p className="font-mono text-[11px] break-words">{m.user_response || "(No answer submitted)"}</p>
                      </div>

                      <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-300">
                        <span className="text-[10px] uppercase font-bold text-emerald-400 block mb-1">Correct Model Answer:</span>
                        <p className="font-mono text-[11px] break-words">{m.correct_answer}</p>
                      </div>
                    </div>

                    {m.suggested_fix && (
                      <div className="p-3 rounded-lg bg-[#251A38] border border-[#382650] text-xs text-[#D4D4D8]">
                        <span className="font-bold text-[#C084FC]">Actionable Remediation: </span>
                        <span>{m.suggested_fix}</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
