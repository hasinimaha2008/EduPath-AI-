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
  RefreshCw
} from "lucide-react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from "recharts";
import { GlowCard } from "@/components/GlowCard";
import { api } from "@/lib/api";
import { AnalyticsDashboard } from "@/lib/types";

export default function LearningAnalyticsPage() {
  const [data, setData] = useState<AnalyticsDashboard | null>(null);
  const [loading, setLoading] = useState(true);

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

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-[#C084FC]" /> Learning Analytics Dashboard
          </h1>
          <p className="text-xs text-[#A1A1AA] mt-0.5">
            Strictly verified performance metrics computed directly from your completed quizzes and topic assessments.
          </p>
        </div>
        <button
          onClick={loadAnalytics}
          className="px-3 py-1.5 rounded-lg bg-[#191225] border border-[#30203F] text-xs font-semibold text-white hover:border-[#A855F7] transition-all flex items-center gap-1.5 self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} /> Refresh Metrics
        </button>
      </div>

      {/* 4 Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <GlowCard className="p-5">
          <div className="flex items-center justify-between text-[#A1A1AA] mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider">Total Quizzes</span>
            <CheckCircle2 className="w-4 h-4 text-[#A855F7]" />
          </div>
          <div className="text-3xl font-extrabold text-white">
            {data?.total_quizzes_attempted ?? 0}
          </div>
          <div className="text-[11px] text-[#A1A1AA] mt-1">Verified assessments</div>
        </GlowCard>

        <GlowCard className="p-5">
          <div className="flex items-center justify-between text-[#A1A1AA] mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider">Average Accuracy</span>
            <Target className="w-4 h-4 text-[#C084FC]" />
          </div>
          <div className="text-3xl font-extrabold text-white">
            {data?.average_quiz_score ? `${data.average_quiz_score}%` : "0%"}
          </div>
          <div className="text-[11px] text-[#A1A1AA] mt-1">Overall percentage</div>
        </GlowCard>

        <GlowCard className="p-5">
          <div className="flex items-center justify-between text-[#A1A1AA] mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider">Learning Streak</span>
            <Flame className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-3xl font-extrabold text-white">
            {data?.learning_streak_days ?? 0} Days
          </div>
          <div className="text-[11px] text-[#A1A1AA] mt-1">Consecutive activity</div>
        </GlowCard>

        <GlowCard className="p-5">
          <div className="flex items-center justify-between text-[#A1A1AA] mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider">Study Time</span>
            <Clock className="w-4 h-4 text-[#A855F7]" />
          </div>
          <div className="text-3xl font-extrabold text-white">
            {data?.total_study_hours ?? 0} hrs
          </div>
          <div className="text-[11px] text-[#A1A1AA] mt-1">Assessment engagement</div>
        </GlowCard>
      </div>

      {/* Visual Charts: Activity & Questions Solved */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <GlowCard className="p-6">
          <h2 className="text-sm font-bold text-white mb-1 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-[#A855F7]" /> Daily Questions Solved
          </h2>
          <p className="text-xs text-[#A1A1AA] mb-4">Volume of questions answered over time</p>

          <div className="h-64 w-full">
            {data && data.recent_activity.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.recent_activity}>
                  <XAxis dataKey="date" stroke="#A1A1AA" fontSize={11} tickLine={false} />
                  <YAxis stroke="#A1A1AA" fontSize={11} tickLine={false} allowDecimals={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#191225",
                      borderColor: "#30203F",
                      borderRadius: "8px",
                      color: "#FFFFFF",
                      fontSize: "12px",
                    }}
                  />
                  <Bar dataKey="questions_solved" fill="#8B5CF6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-[#A1A1AA]">
                No quiz history available yet.
              </div>
            )}
          </div>
        </GlowCard>

        <GlowCard className="p-6">
          <h2 className="text-sm font-bold text-white mb-1 flex items-center gap-2">
            <Flame className="w-4 h-4 text-[#C084FC]" /> Daily Assessment Count
          </h2>
          <p className="text-xs text-[#A1A1AA] mb-4">Frequency of completed evaluation quizzes</p>

          <div className="h-64 w-full">
            {data && data.recent_activity.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data.recent_activity}>
                  <defs>
                    <linearGradient id="anGlow" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#A855F7" stopOpacity={0.5} />
                      <stop offset="95%" stopColor="#A855F7" stopOpacity={0.0} />
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="date" stroke="#A1A1AA" fontSize={11} tickLine={false} />
                  <YAxis stroke="#A1A1AA" fontSize={11} tickLine={false} allowDecimals={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#191225",
                      borderColor: "#30203F",
                      borderRadius: "8px",
                      color: "#FFFFFF",
                      fontSize: "12px",
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="quiz_count"
                    stroke="#C084FC"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#anGlow)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-[#A1A1AA]">
                No quiz history available yet.
              </div>
            )}
          </div>
        </GlowCard>
      </div>

      {/* Strong vs Weak Topics & Recommendations */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Strong Topics */}
        <GlowCard className="p-5">
          <h2 className="text-sm font-bold text-white mb-2 flex items-center gap-2">
            <Award className="w-4 h-4 text-emerald-400" /> Strong Topics (Proficient / Mastered)
          </h2>
          <div className="space-y-2 mt-3">
            {data?.strong_topics && data.strong_topics.length > 0 ? (
              data.strong_topics.map((t) => (
                <div key={t.id} className="p-2.5 rounded bg-[#100B18] border border-[#30203F] text-xs">
                  <div className="font-semibold text-white">{t.topic_name}</div>
                  <div className="text-[10px] text-emerald-400 font-medium mt-0.5">
                    {t.accuracy_percentage}% Accuracy • {t.total_attempts} attempts
                  </div>
                </div>
              ))
            ) : (
              <div className="text-xs text-[#A1A1AA] py-6 text-center">
                Complete more quizzes to attain proficient/mastered status.
              </div>
            )}
          </div>
        </GlowCard>

        {/* Weak Topics */}
        <GlowCard className="p-5">
          <h2 className="text-sm font-bold text-white mb-2 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" /> Weak Topics (Needs Practice)
          </h2>
          <div className="space-y-2 mt-3">
            {data?.weak_topics && data.weak_topics.length > 0 ? (
              data.weak_topics.map((t) => (
                <div key={t.id} className="p-2.5 rounded bg-[#100B18] border border-[#30203F] text-xs flex items-center justify-between">
                  <div>
                    <div className="font-semibold text-white">{t.topic_name}</div>
                    <div className="text-[10px] text-amber-400 font-medium mt-0.5">
                      {t.accuracy_percentage}% Accuracy • {t.total_attempts} attempts
                    </div>
                  </div>
                  <Link
                    href={`/dashboard/quiz?topic_id=${t.topic_id}`}
                    className="px-2 py-1 rounded bg-[#8B5CF6]/20 border border-[#A855F7]/40 text-[10px] font-bold text-[#C084FC]"
                  >
                    Retest
                  </Link>
                </div>
              ))
            ) : (
              <div className="text-xs text-[#A1A1AA] py-6 text-center">
                No weak topics flagged right now.
              </div>
            )}
          </div>
        </GlowCard>

        {/* Engine Recommendations */}
        <GlowCard className="p-5 flex flex-col justify-between">
          <div>
            <h2 className="text-sm font-bold text-white mb-2 flex items-center gap-2">
              <Target className="w-4 h-4 text-[#C084FC]" /> Revision Action Items
            </h2>
            <div className="space-y-2 mt-3">
              {data?.revision_recommendations.map((rec, i) => (
                <div key={i} className="p-2.5 rounded bg-[#100B18] border border-[#30203F] text-xs text-[#D8B4FE]">
                  • {rec}
                </div>
              ))}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-[#30203F]">
            <Link
              href="/dashboard/study-planner"
              className="w-full py-2 rounded-lg bg-gradient-to-r from-[#8B5CF6] to-[#A855F7] text-white text-xs font-bold flex items-center justify-center gap-1.5"
            >
              Sync to Study Planner <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </GlowCard>
      </div>
    </div>
  );
}
