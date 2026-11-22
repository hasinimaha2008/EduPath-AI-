"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  BarChart3,
  CheckCircle2,
  Clock,
  Target,
  Flame,
  AlertTriangle,
  Award,
  ArrowRight,
  TrendingUp,
  RefreshCw,
  Sparkles,
  BookOpen,
  GraduationCap,
  HelpCircle,
  Activity,
  Layers,
  ChevronRight,
  PieChart as PieIcon,
  ShieldCheck,
  FileText
} from "lucide-react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  AreaChart,
  Area,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from "recharts";
import { GlowCard } from "@/components/GlowCard";
import { api } from "@/lib/api";
import { AnalyticsDashboard } from "@/lib/types";

// Colors for Donut / Charts
const MASTERY_COLORS: Record<string, string> = {
  Mastered: "#10B981",    // Emerald
  Proficient: "#8B5CF6",  // Purple
  Developing: "#F59E0B",  // Amber
  "Needs Practice": "#EF4444" // Rose
};

export default function LearningAnalyticsPage() {
  const [data, setData] = useState<AnalyticsDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"overview" | "subjects" | "trends">("overview");

  useEffect(() => {
    loadAnalytics();
  }, []);

  async function loadAnalytics() {
    setLoading(true);
    try {
      const res = await api.getDashboardAnalytics();
      setData(res);
    } catch (e) {
      console.error("Error loading analytics:", e);
    } finally {
      setLoading(false);
    }
  }

  // Topic mastery distribution data for Donut Chart
  const masteryData = React.useMemo(() => {
    if (!data?.topic_completion_stats) return [];
    const stats = data.topic_completion_stats;
    return [
      { name: "Mastered", value: stats.mastered_count, color: MASTERY_COLORS.Mastered },
      { name: "Proficient", value: stats.proficient_count, color: MASTERY_COLORS.Proficient },
      { name: "Developing", value: stats.developing_count, color: MASTERY_COLORS.Developing },
      { name: "Needs Practice", value: stats.needs_practice_count, color: MASTERY_COLORS["Needs Practice"] },
    ].filter(item => item.value > 0);
  }, [data]);

  const isEmpty = !loading && (!data || data.total_quizzes_attempted === 0);

  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-white flex items-center gap-2">
            <BarChart3 className="w-6 h-6 text-[#C084FC]" /> Learning Analytics Dashboard
          </h1>
          <p className="text-xs text-[#A1A1AA] mt-1">
            Real student activity and verified performance metrics computed directly from completed quizzes, notes, and topics.
          </p>
        </div>
        <div className="flex items-center gap-2 self-start sm:self-auto">
          <button
            onClick={loadAnalytics}
            className="px-3 py-1.5 rounded-lg bg-[#191225] border border-[#30203F] text-xs font-semibold text-white hover:border-[#A855F7] transition-all flex items-center gap-1.5"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} /> Refresh
          </button>
          <Link
            href="/dashboard/quiz"
            className="px-3 py-1.5 rounded-lg bg-gradient-to-r from-[#8B5CF6] to-[#A855F7] text-xs font-bold text-white hover:opacity-95 shadow-md flex items-center gap-1.5"
          >
            <Target className="w-3.5 h-3.5" /> Take a Quiz
          </Link>
        </div>
      </div>

      {/* Loading Skeleton */}
      {loading && !data && (
        <div className="p-12 text-center text-sm text-[#A1A1AA] flex flex-col items-center justify-center gap-3">
          <RefreshCw className="w-6 h-6 animate-spin text-[#A855F7]" />
          <span>Calculating verified performance metrics from student history...</span>
        </div>
      )}

      {/* Empty State when student has 0 quiz attempts */}
      {isEmpty && (
        <GlowCard className="p-8 sm:p-12 text-center relative overflow-hidden border border-[#30203F]">
          <div className="max-w-xl mx-auto space-y-5">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-[#8B5CF6]/30 to-[#C084FC]/10 border border-[#A855F7]/40 flex items-center justify-center mx-auto shadow-lg shadow-[#8B5CF6]/20">
              <GraduationCap className="w-8 h-8 text-[#C084FC]" />
            </div>
            <div>
              <h2 className="text-lg sm:text-xl font-bold text-white">
                Welcome to your Learning Analytics Dashboard
              </h2>
              <p className="text-xs sm:text-sm text-[#A1A1AA] mt-2 leading-relaxed">
                EduPath AI tracks <strong>real student activity</strong> and computes verified analytics without sample or fabricated statistics. Take your first assessment quiz, generate unit notes, or review study materials to unlock your personal performance trajectory!
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-4 text-left">
              <Link
                href="/dashboard/quiz"
                className="p-4 rounded-xl bg-[#100B18] border border-[#30203F] hover:border-[#A855F7] transition-all group flex flex-col justify-between"
              >
                <div>
                  <Target className="w-5 h-5 text-[#C084FC] mb-2" />
                  <div className="font-semibold text-white text-xs group-hover:text-[#D8B4FE]">AI Assessment Quiz</div>
                  <div className="text-[11px] text-[#A1A1AA] mt-1">Generate an adaptive quiz across topics or documents.</div>
                </div>
                <div className="text-[10px] text-[#A855F7] font-bold mt-3 flex items-center gap-1">
                  Start Quiz <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
                </div>
              </Link>

              <Link
                href="/dashboard/notes"
                className="p-4 rounded-xl bg-[#100B18] border border-[#30203F] hover:border-[#A855F7] transition-all group flex flex-col justify-between"
              >
                <div>
                  <BookOpen className="w-5 h-5 text-[#8B5CF6] mb-2" />
                  <div className="font-semibold text-white text-xs group-hover:text-[#D8B4FE]">Smart Notes</div>
                  <div className="text-[11px] text-[#A1A1AA] mt-1">Generate structured study materials & revision cards.</div>
                </div>
                <div className="text-[10px] text-[#A855F7] font-bold mt-3 flex items-center gap-1">
                  Create Notes <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
                </div>
              </Link>

              <Link
                href="/dashboard/documents"
                className="p-4 rounded-xl bg-[#100B18] border border-[#30203F] hover:border-[#A855F7] transition-all group flex flex-col justify-between"
              >
                <div>
                  <FileText className="w-5 h-5 text-emerald-400 mb-2" />
                  <div className="font-semibold text-white text-xs group-hover:text-[#D8B4FE]">Course Documents</div>
                  <div className="text-[11px] text-[#A1A1AA] mt-1">Upload syllabus PDFs, lecture slides, and notes.</div>
                </div>
                <div className="text-[10px] text-[#A855F7] font-bold mt-3 flex items-center gap-1">
                  Upload Materials <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
                </div>
              </Link>
            </div>
          </div>
        </GlowCard>
      )}

      {/* Main Content when Data Exists */}
      {!isEmpty && data && (
        <>
          {/* Personalized Intelligent Recommendation Banner */}
          {data.personalized_recommendation && (
            <div className="relative p-5 sm:p-6 rounded-2xl bg-gradient-to-r from-[#1E1136]/90 via-[#160D27]/90 to-[#100B18]/90 border border-[#8B5CF6]/40 shadow-lg shadow-[#8B5CF6]/10 backdrop-blur-sm">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div className="flex items-start gap-3.5">
                  <div className="w-9 h-9 rounded-xl bg-[#8B5CF6]/20 border border-[#A855F7]/40 flex items-center justify-center shrink-0 mt-0.5">
                    <Sparkles className="w-5 h-5 text-[#C084FC] animate-pulse" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-[11px] font-bold uppercase tracking-wider text-[#C084FC]">
                        AI Learning Engine Insight
                      </span>
                      <span className="px-2 py-0.5 rounded-full bg-[#8B5CF6]/20 border border-[#8B5CF6]/30 text-[10px] text-white font-medium">
                        Personalized Recommendation
                      </span>
                    </div>
                    <p className="text-xs sm:text-sm text-[#E9D5FF] mt-1 font-medium leading-relaxed">
                      {data.personalized_recommendation}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0 self-end sm:self-auto">
                  {data.weak_topics.length > 0 && (
                    <Link
                      href={`/dashboard/quiz?topic_id=${data.weak_topics[0].topic_id}`}
                      className="px-3 py-1.5 rounded-lg bg-[#8B5CF6]/25 border border-[#A855F7]/50 text-xs font-bold text-[#E9D5FF] hover:bg-[#8B5CF6]/40 transition-all flex items-center gap-1"
                    >
                      Targeted Retest <ArrowRight className="w-3 h-3" />
                    </Link>
                  )}
                  <Link
                    href="/dashboard/notes"
                    className="px-3 py-1.5 rounded-lg bg-[#191225] border border-[#30203F] text-xs font-medium text-white hover:border-[#A855F7] transition-all"
                  >
                    Smart Notes
                  </Link>
                </div>
              </div>
            </div>
          )}

          {/* 6 Key Stat Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
            <GlowCard className="p-4 flex flex-col justify-between">
              <div className="flex items-center justify-between text-[#A1A1AA] mb-2">
                <span className="text-[10px] font-semibold uppercase tracking-wider">Quizzes</span>
                <CheckCircle2 className="w-4 h-4 text-[#A855F7]" />
              </div>
              <div className="text-2xl font-extrabold text-white">
                {data.total_quizzes_attempted}
              </div>
              <div className="text-[10px] text-[#A1A1AA] mt-1">Completed tests</div>
            </GlowCard>

            <GlowCard className="p-4 flex flex-col justify-between">
              <div className="flex items-center justify-between text-[#A1A1AA] mb-2">
                <span className="text-[10px] font-semibold uppercase tracking-wider">Avg Accuracy</span>
                <Target className="w-4 h-4 text-[#C084FC]" />
              </div>
              <div className="text-2xl font-extrabold text-white">
                {data.average_quiz_score}%
              </div>
              <div className="text-[10px] text-emerald-400 font-medium mt-1">Verified score</div>
            </GlowCard>

            <GlowCard className="p-4 flex flex-col justify-between">
              <div className="flex items-center justify-between text-[#A1A1AA] mb-2">
                <span className="text-[10px] font-semibold uppercase tracking-wider">Highest Score</span>
                <Award className="w-4 h-4 text-emerald-400" />
              </div>
              <div className="text-2xl font-extrabold text-white">
                {data.highest_quiz_score ?? 0}%
              </div>
              <div className="text-[10px] text-[#A1A1AA] mt-1">Peak performance</div>
            </GlowCard>

            <GlowCard className="p-4 flex flex-col justify-between">
              <div className="flex items-center justify-between text-[#A1A1AA] mb-2">
                <span className="text-[10px] font-semibold uppercase tracking-wider">Consistency</span>
                <Activity className="w-4 h-4 text-cyan-400" />
              </div>
              <div className="text-2xl font-extrabold text-white">
                {data.study_consistency_percentage ?? 0}%
              </div>
              <div className="text-[10px] text-[#A1A1AA] mt-1">Last 14 days</div>
            </GlowCard>

            <GlowCard className="p-4 flex flex-col justify-between">
              <div className="flex items-center justify-between text-[#A1A1AA] mb-2">
                <span className="text-[10px] font-semibold uppercase tracking-wider">Streak</span>
                <Flame className="w-4 h-4 text-amber-400" />
              </div>
              <div className="text-2xl font-extrabold text-white">
                {data.learning_streak_days} <span className="text-xs font-normal text-[#A1A1AA]">days</span>
              </div>
              <div className="text-[10px] text-amber-400 font-medium mt-1">Active streak</div>
            </GlowCard>

            <GlowCard className="p-4 flex flex-col justify-between">
              <div className="flex items-center justify-between text-[#A1A1AA] mb-2">
                <span className="text-[10px] font-semibold uppercase tracking-wider">Study Time</span>
                <Clock className="w-4 h-4 text-[#A855F7]" />
              </div>
              <div className="text-2xl font-extrabold text-white">
                {data.total_study_hours} <span className="text-xs font-normal text-[#A1A1AA]">hrs</span>
              </div>
              <div className="text-[10px] text-[#A1A1AA] mt-1">Quiz engagement</div>
            </GlowCard>
          </div>

          {/* Interactive Navigation / Filters */}
          <div className="flex items-center justify-between border-b border-[#30203F] pb-3">
            <div className="flex items-center gap-2">
              <button
                onClick={() => setActiveTab("overview")}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  activeTab === "overview"
                    ? "bg-[#8B5CF6]/20 border border-[#A855F7] text-white"
                    : "text-[#A1A1AA] hover:text-white"
                }`}
              >
                Comprehensive Overview
              </button>
              <button
                onClick={() => setActiveTab("subjects")}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  activeTab === "subjects"
                    ? "bg-[#8B5CF6]/20 border border-[#A855F7] text-white"
                    : "text-[#A1A1AA] hover:text-white"
                }`}
              >
                Subject Performance
              </button>
              <button
                onClick={() => setActiveTab("trends")}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  activeTab === "trends"
                    ? "bg-[#8B5CF6]/20 border border-[#A855F7] text-white"
                    : "text-[#A1A1AA] hover:text-white"
                }`}
              >
                Score Trajectory
              </button>
            </div>
            <div className="text-xs text-[#A1A1AA] hidden sm:block">
              {data.topic_completion_stats?.total_practiced ?? 0} topics evaluated
            </div>
          </div>

          {/* Tab 1: Comprehensive Overview */}
          {activeTab === "overview" && (
            <div className="space-y-6">
              {/* Row 1: Quiz Score Trajectory & Subject-Wise Performance */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Score Trends Line Chart */}
                <GlowCard className="p-5 sm:p-6 flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <h2 className="text-sm font-bold text-white flex items-center gap-2">
                        <TrendingUp className="w-4 h-4 text-[#A855F7]" /> Quiz Score Trajectory
                      </h2>
                      <span className="text-[10px] text-[#A1A1AA]">Chronological attempts</span>
                    </div>
                    <p className="text-xs text-[#A1A1AA] mb-4">
                      Percentage score evolution across your most recent quiz assessments
                    </p>

                    <div className="h-64 w-full">
                      {data.quiz_score_trends && data.quiz_score_trends.length > 0 ? (
                        <ResponsiveContainer width="100%" height="100%">
                          <AreaChart data={data.quiz_score_trends}>
                            <defs>
                              <linearGradient id="scoreGlow" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.4} />
                                <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0.0} />
                              </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#251833" vertical={false} />
                            <XAxis
                              dataKey="completed_at"
                              stroke="#71717A"
                              fontSize={10}
                              tickLine={false}
                              tickFormatter={(val) => (val ? val.split(",")[0] : "")}
                            />
                            <YAxis
                              stroke="#71717A"
                              fontSize={10}
                              tickLine={false}
                              domain={[0, 100]}
                              unit="%"
                            />
                            <Tooltip
                              content={({ active, payload }) => {
                                if (active && payload && payload.length) {
                                  const item = payload[0].payload;
                                  return (
                                    <div className="p-2.5 rounded-lg bg-[#191225] border border-[#30203F] text-xs shadow-xl">
                                      <div className="font-bold text-white">{item.quiz_title}</div>
                                      <div className="text-[11px] text-[#C084FC] mt-0.5">
                                        Score: {item.percentage}% ({item.score}/{item.max_score} pts)
                                      </div>
                                      <div className="text-[10px] text-[#A1A1AA] mt-1">{item.completed_at}</div>
                                    </div>
                                  );
                                }
                                return null;
                              }}
                            />
                            <Area
                              type="monotone"
                              dataKey="percentage"
                              stroke="#A855F7"
                              strokeWidth={2.5}
                              fill="url(#scoreGlow)"
                              dot={{ fill: "#C084FC", r: 3.5, strokeWidth: 0 }}
                              activeDot={{ fill: "#FFFFFF", stroke: "#A855F7", strokeWidth: 2, r: 5 }}
                            />
                          </AreaChart>
                        </ResponsiveContainer>
                      ) : (
                        <div className="h-full flex items-center justify-center text-xs text-[#A1A1AA]">
                          No quiz trends available yet. Complete a quiz to view trajectory.
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="text-[11px] text-[#A1A1AA] pt-3 border-t border-[#30203F] flex items-center justify-between">
                    <span>Target Mastery Benchmark: 75%</span>
                    <span className="text-emerald-400 font-medium">Average: {data.average_quiz_score}%</span>
                  </div>
                </GlowCard>

                {/* Subject-Wise Performance Bar Chart */}
                <GlowCard className="p-5 sm:p-6 flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <h2 className="text-sm font-bold text-white flex items-center gap-2">
                        <Layers className="w-4 h-4 text-[#C084FC]" /> Subject-Wise Performance
                      </h2>
                      <span className="text-[10px] text-[#A1A1AA]">Curriculum Accuracy</span>
                    </div>
                    <p className="text-xs text-[#A1A1AA] mb-4">
                      Comparative average accuracy across all evaluated subject domains
                    </p>

                    <div className="h-64 w-full">
                      {data.subject_performances && data.subject_performances.length > 0 ? (
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={data.subject_performances} layout="vertical" margin={{ left: 10, right: 20 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#251833" horizontal={false} />
                            <XAxis type="number" domain={[0, 100]} stroke="#71717A" fontSize={10} unit="%" />
                            <YAxis
                              type="category"
                              dataKey="subject_name"
                              stroke="#A1A1AA"
                              fontSize={10}
                              tickLine={false}
                              width={110}
                              tickFormatter={(val) => (val.length > 15 ? val.slice(0, 15) + "..." : val)}
                            />
                            <Tooltip
                              content={({ active, payload }) => {
                                if (active && payload && payload.length) {
                                  const item = payload[0].payload;
                                  return (
                                    <div className="p-2.5 rounded-lg bg-[#191225] border border-[#30203F] text-xs shadow-xl">
                                      <div className="font-bold text-white">{item.subject_name}</div>
                                      <div className="text-[11px] text-[#A855F7] mt-0.5">
                                        Average Accuracy: {item.average_accuracy}%
                                      </div>
                                      <div className="text-[10px] text-[#A1A1AA] mt-1">
                                        {item.quizzes_count} quizzes completed • {item.topics_practiced} topics practiced
                                      </div>
                                    </div>
                                  );
                                }
                                return null;
                              }}
                            />
                            <Bar
                              dataKey="average_accuracy"
                              fill="#8B5CF6"
                              radius={[0, 4, 4, 0]}
                            />
                          </BarChart>
                        </ResponsiveContainer>
                      ) : (
                        <div className="h-full flex items-center justify-center text-xs text-[#A1A1AA]">
                          No subject assessment records yet.
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="text-[11px] text-[#A1A1AA] pt-3 border-t border-[#30203F] flex items-center justify-between">
                    <span>Subjects Evaluated: {data.subject_performances?.length ?? 0}</span>
                    <Link href="/dashboard/workspace" className="text-[#C084FC] hover:underline flex items-center gap-1">
                      Explore Taxonomy <ChevronRight className="w-3 h-3" />
                    </Link>
                  </div>
                </GlowCard>
              </div>

              {/* Row 2: Topic Mastery Distribution & Weekly Activity */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Topic Mastery Distribution Donut */}
                <GlowCard className="p-5 sm:p-6 flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <h2 className="text-sm font-bold text-white flex items-center gap-2">
                        <PieIcon className="w-4 h-4 text-emerald-400" /> Topic Mastery Distribution
                      </h2>
                      <span className="text-[10px] text-[#A1A1AA]">Mastery Levels</span>
                    </div>
                    <p className="text-xs text-[#A1A1AA] mb-4">
                      Breakdown of practiced topics across mastery tiers
                    </p>

                    <div className="grid grid-cols-1 sm:grid-cols-2 items-center gap-4 h-64">
                      {masteryData.length > 0 ? (
                        <>
                          <div className="h-full w-full">
                            <ResponsiveContainer width="100%" height="100%">
                              <PieChart>
                                <Pie
                                  data={masteryData}
                                  cx="50%"
                                  cy="50%"
                                  innerRadius={55}
                                  outerRadius={80}
                                  paddingAngle={4}
                                  dataKey="value"
                                >
                                  {masteryData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.color} stroke="#100B18" strokeWidth={2} />
                                  ))}
                                </Pie>
                                <Tooltip
                                  contentStyle={{
                                    backgroundColor: "#191225",
                                    borderColor: "#30203F",
                                    borderRadius: "8px",
                                    color: "#FFFFFF",
                                    fontSize: "12px",
                                  }}
                                />
                              </PieChart>
                            </ResponsiveContainer>
                          </div>

                          <div className="space-y-2.5">
                            <div className="flex items-center justify-between p-2 rounded-lg bg-[#100B18] border border-[#30203F] text-xs">
                              <span className="flex items-center gap-2">
                                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400" /> Mastered
                              </span>
                              <span className="font-bold text-emerald-400">
                                {data.topic_completion_stats?.mastered_count ?? 0}
                              </span>
                            </div>

                            <div className="flex items-center justify-between p-2 rounded-lg bg-[#100B18] border border-[#30203F] text-xs">
                              <span className="flex items-center gap-2">
                                <span className="w-2.5 h-2.5 rounded-full bg-[#8B5CF6]" /> Proficient
                              </span>
                              <span className="font-bold text-[#C084FC]">
                                {data.topic_completion_stats?.proficient_count ?? 0}
                              </span>
                            </div>

                            <div className="flex items-center justify-between p-2 rounded-lg bg-[#100B18] border border-[#30203F] text-xs">
                              <span className="flex items-center gap-2">
                                <span className="w-2.5 h-2.5 rounded-full bg-amber-400" /> Developing
                              </span>
                              <span className="font-bold text-amber-400">
                                {data.topic_completion_stats?.developing_count ?? 0}
                              </span>
                            </div>

                            <div className="flex items-center justify-between p-2 rounded-lg bg-[#100B18] border border-[#30203F] text-xs">
                              <span className="flex items-center gap-2">
                                <span className="w-2.5 h-2.5 rounded-full bg-rose-500" /> Needs Practice
                              </span>
                              <span className="font-bold text-rose-400">
                                {data.topic_completion_stats?.needs_practice_count ?? 0}
                              </span>
                            </div>
                          </div>
                        </>
                      ) : (
                        <div className="col-span-2 h-full flex items-center justify-center text-xs text-[#A1A1AA]">
                          Complete topic quizzes to populate your mastery distribution.
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="text-[11px] text-[#A1A1AA] pt-3 border-t border-[#30203F] flex items-center justify-between">
                    <span>Total Evaluated: {data.topic_completion_stats?.total_practiced ?? 0}</span>
                    <span className="text-[#C084FC]">
                      {masteryData.length > 0
                        ? `${Math.round(
                            (((data.topic_completion_stats?.mastered_count ?? 0) +
                              (data.topic_completion_stats?.proficient_count ?? 0)) /
                              Math.max(data.topic_completion_stats?.total_practiced ?? 1, 1)) *
                              100
                          )}% Proficient+`
                        : "0%"}
                    </span>
                  </div>
                </GlowCard>

                {/* Weekly Study Activity */}
                <GlowCard className="p-5 sm:p-6 flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <h2 className="text-sm font-bold text-white flex items-center gap-2">
                        <Flame className="w-4 h-4 text-amber-400" /> Weekly Learning Activity
                      </h2>
                      <span className="text-[10px] text-[#A1A1AA]">Last 7 days</span>
                    </div>
                    <p className="text-xs text-[#A1A1AA] mb-4">
                      Daily question volume and quiz completion frequency
                    </p>

                    <div className="h-64 w-full">
                      {data.recent_activity && data.recent_activity.length > 0 ? (
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={data.recent_activity}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#251833" vertical={false} />
                            <XAxis
                              dataKey="date"
                              stroke="#71717A"
                              fontSize={10}
                              tickLine={false}
                              tickFormatter={(val) => {
                                try {
                                  const parts = val.split("-");
                                  return `${parts[1]}/${parts[2]}`;
                                } catch {
                                  return val;
                                }
                              }}
                            />
                            <YAxis stroke="#71717A" fontSize={10} tickLine={false} allowDecimals={false} />
                            <Tooltip
                              contentStyle={{
                                backgroundColor: "#191225",
                                borderColor: "#30203F",
                                borderRadius: "8px",
                                color: "#FFFFFF",
                                fontSize: "12px",
                              }}
                            />
                            <Bar dataKey="questions_solved" fill="#8B5CF6" name="Questions Solved" radius={[4, 4, 0, 0]} />
                            <Bar dataKey="quiz_count" fill="#C084FC" name="Quizzes Completed" radius={[4, 4, 0, 0]} />
                          </BarChart>
                        </ResponsiveContainer>
                      ) : (
                        <div className="h-full flex items-center justify-center text-xs text-[#A1A1AA]">
                          No activity recorded in the past 7 days.
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="text-[11px] text-[#A1A1AA] pt-3 border-t border-[#30203F] flex items-center justify-between">
                    <span>Active Days: {data.learning_streak_days} / 7</span>
                    <span className="text-amber-400 font-medium">Streak Active</span>
                  </div>
                </GlowCard>
              </div>
            </div>
          )}

          {/* Tab 2: Subjects Focus */}
          {activeTab === "subjects" && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                {data.subject_performances && data.subject_performances.length > 0 ? (
                  data.subject_performances.map((subj, idx) => (
                    <GlowCard key={idx} className="p-5 flex flex-col justify-between">
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs font-bold text-white truncate max-w-[180px]">
                            {subj.subject_name}
                          </span>
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              subj.average_accuracy >= 75
                                ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                                : subj.average_accuracy >= 60
                                ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                                : "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                            }`}
                          >
                            {subj.average_accuracy}% Avg
                          </span>
                        </div>
                        <div className="text-xs text-[#A1A1AA] space-y-1 mt-3">
                          <div className="flex justify-between">
                            <span>Quizzes Attempted:</span>
                            <span className="text-white font-medium">{subj.quizzes_count}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Topics Evaluated:</span>
                            <span className="text-white font-medium">{subj.topics_practiced}</span>
                          </div>
                        </div>

                        {/* Progress Bar */}
                        <div className="w-full bg-[#100B18] h-2 rounded-full mt-4 overflow-hidden border border-[#30203F]">
                          <div
                            className={`h-full rounded-full ${
                              subj.average_accuracy >= 75
                                ? "bg-emerald-400"
                                : subj.average_accuracy >= 60
                                ? "bg-amber-400"
                                : "bg-rose-500"
                            }`}
                            style={{ width: `${Math.min(subj.average_accuracy, 100)}%` }}
                          />
                        </div>
                      </div>

                      <div className="pt-4 mt-4 border-t border-[#30203F] flex items-center justify-between">
                        <Link
                          href={`/dashboard/quiz?subject_id=${subj.subject_id || ""}`}
                          className="text-[11px] font-bold text-[#C084FC] hover:text-white flex items-center gap-1"
                        >
                          Generate Subject Quiz <ArrowRight className="w-3 h-3" />
                        </Link>
                      </div>
                    </GlowCard>
                  ))
                ) : (
                  <div className="col-span-3 text-center py-12 text-xs text-[#A1A1AA]">
                    No subject records available. Complete quizzes to begin tracking subject metrics.
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Tab 3: Score Trajectory & Attempt History */}
          {activeTab === "trends" && (
            <div className="space-y-6">
              <GlowCard className="p-6">
                <h2 className="text-sm font-bold text-white mb-1 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-[#C084FC]" /> Chronological Score Trajectory
                </h2>
                <p className="text-xs text-[#A1A1AA] mb-6">
                  Detailed timeline of your past 15 quiz evaluations with verified point tallies
                </p>

                <div className="h-72 w-full">
                  {data.quiz_score_trends && data.quiz_score_trends.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={data.quiz_score_trends}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#251833" vertical={false} />
                        <XAxis
                          dataKey="completed_at"
                          stroke="#71717A"
                          fontSize={10}
                          tickLine={false}
                        />
                        <YAxis stroke="#71717A" fontSize={10} tickLine={false} domain={[0, 100]} unit="%" />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: "#191225",
                            borderColor: "#30203F",
                            borderRadius: "8px",
                            color: "#FFFFFF",
                            fontSize: "12px",
                          }}
                        />
                        <Line
                          type="monotone"
                          dataKey="percentage"
                          stroke="#A855F7"
                          strokeWidth={3}
                          dot={{ fill: "#C084FC", r: 4 }}
                          activeDot={{ fill: "#FFFFFF", stroke: "#8B5CF6", strokeWidth: 2, r: 6 }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="h-full flex items-center justify-center text-xs text-[#A1A1AA]">
                      No quiz trajectory available.
                    </div>
                  )}
                </div>
              </GlowCard>

              {/* Table of Past Attempts */}
              <GlowCard className="p-5">
                <h3 className="text-xs font-bold uppercase tracking-wider text-[#A1A1AA] mb-3">
                  Recent Evaluation Records
                </h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-xs text-left">
                    <thead>
                      <tr className="border-b border-[#30203F] text-[#71717A]">
                        <th className="pb-2 font-medium">Quiz Title</th>
                        <th className="pb-2 font-medium">Completed At</th>
                        <th className="pb-2 font-medium">Score Awarded</th>
                        <th className="pb-2 font-medium">Percentage</th>
                        <th className="pb-2 font-medium text-right">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#20152B]">
                      {data.quiz_score_trends?.map((trend, i) => (
                        <tr key={trend.attempt_id || i} className="hover:bg-[#100B18]/50">
                          <td className="py-2.5 font-semibold text-white">{trend.quiz_title}</td>
                          <td className="py-2.5 text-[#A1A1AA]">{trend.completed_at}</td>
                          <td className="py-2.5 text-white">
                            {trend.score} / {trend.max_score} pts
                          </td>
                          <td className="py-2.5">
                            <span
                              className={`px-2 py-0.5 rounded font-bold ${
                                trend.percentage >= 75
                                ? "text-emerald-400 bg-emerald-500/10"
                                : trend.percentage >= 60
                                ? "text-amber-400 bg-amber-500/10"
                                : "text-rose-400 bg-rose-500/10"
                              }`}
                            >
                              {trend.percentage}%
                            </span>
                          </td>
                          <td className="py-2.5 text-right">
                            <Link
                              href={`/dashboard/quiz?review_attempt_id=${trend.attempt_id}`}
                              className="text-[11px] text-[#C084FC] hover:underline"
                            >
                              Review Answers
                            </Link>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </GlowCard>
            </div>
          )}

          {/* Intelligent Insights Panel (4 Categorized Cards) */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-[#C084FC]" />
              <h2 className="text-sm font-bold text-white">
                Intelligent Learning Insights & Diagnostics
              </h2>
            </div>
            <p className="text-xs text-[#A1A1AA]">
              Automated diagnostics derived from actual question error categories and score trends
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {data.intelligent_insights && data.intelligent_insights.length > 0 ? (
                data.intelligent_insights.map((insight, idx) => {
                  const isWarning = insight.severity === "warning";
                  const isSuccess = insight.severity === "success";

                  return (
                    <GlowCard
                      key={idx}
                      className={`p-4 flex flex-col justify-between border ${
                        isWarning
                          ? "border-amber-500/30 bg-[#140D18]"
                          : isSuccess
                          ? "border-emerald-500/30 bg-[#0C1514]"
                          : "border-[#30203F] bg-[#100B18]"
                      }`}
                    >
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <span
                            className={`text-[10px] font-bold uppercase tracking-wider ${
                              isWarning
                                ? "text-amber-400"
                                : isSuccess
                                ? "text-emerald-400"
                                : "text-[#C084FC]"
                            }`}
                          >
                            {insight.category.toUpperCase()}
                          </span>
                          {isWarning ? (
                            <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                          ) : isSuccess ? (
                            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                          ) : (
                            <HelpCircle className="w-3.5 h-3.5 text-[#C084FC]" />
                          )}
                        </div>
                        <h3 className="text-xs font-bold text-white mb-1.5">{insight.title}</h3>
                        <p className="text-[11px] text-[#A1A1AA] leading-relaxed">
                          {insight.message}
                        </p>
                      </div>
                    </GlowCard>
                  );
                })
              ) : (
                <div className="col-span-4 text-center py-4 text-xs text-[#A1A1AA]">
                  Complete additional assessments to generate automated diagnostic insights.
                </div>
              )}
            </div>
          </div>

          {/* Strong vs Weak Topics & Recommendations */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Strong Topics */}
            <GlowCard className="p-5 flex flex-col justify-between">
              <div>
                <h2 className="text-sm font-bold text-white mb-2 flex items-center gap-2">
                  <Award className="w-4 h-4 text-emerald-400" /> Strong Topics (Proficient / Mastered)
                </h2>
                <div className="space-y-2 mt-3 max-h-72 overflow-y-auto pr-1">
                  {data.strong_topics && data.strong_topics.length > 0 ? (
                    data.strong_topics.map((t) => (
                      <div
                        key={t.id}
                        className="p-2.5 rounded-lg bg-[#100B18] border border-[#30203F] text-xs flex items-center justify-between"
                      >
                        <div>
                          <div className="font-semibold text-white">{t.topic_name}</div>
                          <div className="text-[10px] text-emerald-400 font-medium mt-0.5">
                            {t.accuracy_percentage}% Accuracy • {t.total_attempts} attempts • {t.mastery_status}
                          </div>
                        </div>
                        <Link
                          href={`/dashboard/workspace?topic_id=${t.topic_id}`}
                          className="text-[10px] text-[#A1A1AA] hover:text-[#C084FC]"
                          title="View in Workspace"
                        >
                          <ChevronRight className="w-4 h-4" />
                        </Link>
                      </div>
                    ))
                  ) : (
                    <div className="text-xs text-[#A1A1AA] py-6 text-center">
                      Complete more quizzes with &ge;75% accuracy to attain proficient/mastered status.
                    </div>
                  )}
                </div>
              </div>
              <div className="pt-3 mt-3 border-t border-[#30203F] text-[11px] text-[#A1A1AA] flex justify-between">
                <span>Strong Topics Count:</span>
                <span className="text-emerald-400 font-bold">{data.strong_topics.length}</span>
              </div>
            </GlowCard>

            {/* Weak Topics */}
            <GlowCard className="p-5 flex flex-col justify-between">
              <div>
                <h2 className="text-sm font-bold text-white mb-2 flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-amber-400" /> Weak Topics (Needs Practice)
                </h2>
                <div className="space-y-2 mt-3 max-h-72 overflow-y-auto pr-1">
                  {data.weak_topics && data.weak_topics.length > 0 ? (
                    data.weak_topics.map((t) => (
                      <div
                        key={t.id}
                        className="p-2.5 rounded-lg bg-[#100B18] border border-[#30203F] text-xs flex items-center justify-between"
                      >
                        <div className="max-w-[180px]">
                          <div className="font-semibold text-white truncate">{t.topic_name}</div>
                          <div className="text-[10px] text-amber-400 font-medium mt-0.5">
                            {t.accuracy_percentage}% Accuracy • {t.total_attempts} attempts
                          </div>
                        </div>
                        <div className="flex items-center gap-1.5">
                          <Link
                            href={`/dashboard/notes?topic_id=${t.topic_id}`}
                            className="px-2 py-1 rounded bg-[#191225] border border-[#30203F] text-[10px] text-[#A1A1AA] hover:text-white"
                            title="Generate Smart Notes"
                          >
                            Notes
                          </Link>
                          <Link
                            href={`/dashboard/quiz?topic_id=${t.topic_id}`}
                            className="px-2 py-1 rounded bg-[#8B5CF6]/20 border border-[#A855F7]/40 text-[10px] font-bold text-[#C084FC] hover:bg-[#8B5CF6]/30"
                          >
                            Retest
                          </Link>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-xs text-[#A1A1AA] py-6 text-center">
                      No weak topics flagged right now! All practiced topics meet target proficiency.
                    </div>
                  )}
                </div>
              </div>
              <div className="pt-3 mt-3 border-t border-[#30203F] text-[11px] text-[#A1A1AA] flex justify-between">
                <span>Priority Revision Count:</span>
                <span className="text-amber-400 font-bold">{data.weak_topics.length}</span>
              </div>
            </GlowCard>

            {/* Practical Action Items */}
            <GlowCard className="p-5 flex flex-col justify-between">
              <div>
                <h2 className="text-sm font-bold text-white mb-2 flex items-center gap-2">
                  <Target className="w-4 h-4 text-[#C084FC]" /> Practical Revision Action Items
                </h2>
                <div className="space-y-2 mt-3 max-h-72 overflow-y-auto pr-1">
                  {data.revision_recommendations && data.revision_recommendations.length > 0 ? (
                    data.revision_recommendations.map((rec, i) => (
                      <div
                        key={i}
                        className="p-2.5 rounded-lg bg-[#100B18] border border-[#30203F] text-xs text-[#D8B4FE] leading-relaxed"
                      >
                        • {rec}
                      </div>
                    ))
                  ) : (
                    <div className="text-xs text-[#A1A1AA] py-6 text-center">
                      No action items needed at this time.
                    </div>
                  )}
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-[#30203F]">
                <Link
                  href="/dashboard/study-planner"
                  className="w-full py-2 rounded-lg bg-gradient-to-r from-[#8B5CF6] to-[#A855F7] text-white text-xs font-bold flex items-center justify-center gap-1.5 hover:opacity-95 shadow-md"
                >
                  Sync to Study Planner <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </GlowCard>
          </div>
        </>
      )}
    </div>
  );
}
