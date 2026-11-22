"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  BarChart3,
  CheckCircle2,
  Clock,
  Compass,
  FileText,
  Flame,
  Milestone,
  Sparkles,
  Target,
  ArrowRight,
  AlertTriangle,
  BookOpen
} from "lucide-react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
} from "recharts";
import { GlowCard } from "@/components/GlowCard";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/AuthContext";
import {
  AnalyticsDashboard,
  CareerRecommendation,
  StudyPlan,
  TopicPerformance,
  EcosystemSummaryResponse,
} from "@/lib/types";

export default function DashboardOverviewPage() {
  const { user } = useAuth();
  const [analytics, setAnalytics] = useState<AnalyticsDashboard | null>(null);
  const [recommendations, setRecommendations] = useState<CareerRecommendation[]>([]);
  const [studyPlan, setStudyPlan] = useState<StudyPlan | null>(null);
  const [ecosystem, setEcosystem] = useState<EcosystemSummaryResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [anData, recData, planData, ecoData] = await Promise.all([
          api.getDashboardAnalytics().catch(() => null),
          api.getCareerRecommendations().catch(() => []),
          api.getActiveStudyPlan().catch(() => null),
          api.getEcosystemSummary().catch(() => null),
        ]);
        if (anData) setAnalytics(anData);
        setRecommendations(recData);
        if (planData) setStudyPlan(planData);
        if (ecoData) setEcosystem(ecoData);
      } catch (e) {
        console.error("Dashboard data load error:", e);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const topCareer = recommendations.length > 0 ? recommendations[0] : null;

  return (
    <div className="space-y-8">
      {/* Welcome & Ecosystem Status */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-2xl bg-gradient-to-r from-purple-950/40 via-[#191225] to-[#100B18] border border-[#30203F] shadow-[0_0_25px_-5px_rgba(168,85,247,0.25)]">
        <div>
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-md bg-[#8B5CF6]/20 border border-[#A855F7]/40 text-xs font-semibold text-[#C084FC] mb-2">
            <Sparkles className="w-3.5 h-3.5" /> EduPath Intelligence Engine Connected
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            {user?.full_name ? `Welcome back, ${user.full_name}!` : "Learner Workspace & Career Ecosystem"}
          </h1>
          <p className="text-xs sm:text-sm text-[#A1A1AA] mt-1">
            {user?.email ? <span className="text-[#C084FC] font-medium">{user.email} &bull; </span> : null}
            Academic assessment evidence is dynamically mapping to your career competencies.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/dashboard/quiz"
            className="px-4 py-2.5 rounded-xl text-xs font-bold bg-gradient-to-r from-[#8B5CF6] to-[#A855F7] text-white shadow-[0_0_15px_rgba(168,85,247,0.4)] hover:shadow-[0_0_25px_rgba(168,85,247,0.7)] transition-all flex items-center gap-2"
          >
            <CheckCircle2 className="w-4 h-4" /> Take Assessment
          </Link>
          <Link
            href="/dashboard/assistant"
            className="px-4 py-2.5 rounded-xl text-xs font-bold bg-[#191225] border border-[#30203F] hover:border-purple-500/50 text-white transition-all flex items-center gap-2"
          >
            <Sparkles className="w-4 h-4 text-[#C084FC]" /> Ask Assistant
          </Link>
        </div>
      </div>

      {/* 4 Key Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <GlowCard className="p-5">
          <div className="flex items-center justify-between text-[#A1A1AA] mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider">Quizzes Taken</span>
            <CheckCircle2 className="w-4 h-4 text-[#A855F7]" />
          </div>
          <div className="text-3xl font-extrabold text-white">
            {analytics?.total_quizzes_attempted ?? 0}
          </div>
          <div className="text-[11px] text-[#A1A1AA] mt-1.5 flex items-center gap-1">
            <span>Verified assessments recorded</span>
          </div>
        </GlowCard>

        <GlowCard className="p-5">
          <div className="flex items-center justify-between text-[#A1A1AA] mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider">Average Score</span>
            <Target className="w-4 h-4 text-[#C084FC]" />
          </div>
          <div className="text-3xl font-extrabold text-white">
            {analytics?.average_quiz_score ? `${analytics.average_quiz_score}%` : "N/A"}
          </div>
          <div className="text-[11px] text-[#A1A1AA] mt-1.5">
            Based on demonstrated answers
          </div>
        </GlowCard>

        <GlowCard className="p-5">
          <div className="flex items-center justify-between text-[#A1A1AA] mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider">Learning Streak</span>
            <Flame className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-3xl font-extrabold text-white">
            {analytics?.learning_streak_days ?? 0} Days
          </div>
          <div className="text-[11px] text-[#A1A1AA] mt-1.5">
            Continuous activity timeline
          </div>
        </GlowCard>

        <GlowCard glow className="p-5 border-purple-500/50">
          <div className="flex items-center justify-between text-[#A1A1AA] mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider">Top Career Match</span>
            <Compass className="w-4 h-4 text-[#A855F7]" />
          </div>
          <div className="text-xl font-extrabold text-white truncate">
            {topCareer ? topCareer.career_role.title : "Calculating..."}
          </div>
          <div className="text-[11px] text-[#C084FC] mt-1.5 font-medium">
            {topCareer ? `${topCareer.match_score}% readiness score` : "Complete quizzes to evaluate"}
          </div>
        </GlowCard>
      </div>

      {/* Ecosystem Action Center */}
      {ecosystem?.recommendations && ecosystem.recommendations.length > 0 && (
        <div className="p-5 rounded-2xl bg-[#140D20] border border-[#30203F] shadow-[0_0_20px_-5px_rgba(168,85,247,0.15)]">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-[#C084FC]" />
              <h2 className="text-xs sm:text-sm font-bold text-white tracking-wide uppercase">
                Connected Ecosystem Actions
              </h2>
            </div>
            <span className="text-[11px] text-[#A1A1AA]">
              Cross-module recommendations tailored to your active learning & goals
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {ecosystem.recommendations.map((rec, idx) => (
              <div
                key={idx}
                className="p-3.5 rounded-xl bg-[#100B18] border border-[#30203F] hover:border-purple-500/40 flex flex-col justify-between transition-all group"
              >
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded bg-purple-500/20 text-[#C084FC] border border-purple-500/30">
                      {rec.source}
                    </span>
                    <span className={`text-[10px] font-semibold ${rec.priority === "High" ? "text-amber-400" : "text-[#A1A1AA]"}`}>
                      {rec.priority} Priority
                    </span>
                  </div>
                  <div className="text-xs font-semibold text-white group-hover:text-[#C084FC] transition-colors line-clamp-2">
                    {rec.title}
                  </div>
                </div>

                <Link
                  href={rec.action_url}
                  className="mt-3 inline-flex items-center justify-between text-[11px] font-bold text-[#C084FC] hover:text-white transition-colors pt-2 border-t border-[#30203F]"
                >
                  <span>{rec.action_label}</span>
                  <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
                </Link>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Main Grid: Learning Activity Chart & Priority Weak Topics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Activity Chart (2 cols) */}
        <GlowCard className="p-6 lg:col-span-2 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-base font-bold text-white flex items-center gap-2">
                  <BarChart3 className="w-4 h-4 text-[#A855F7]" /> Learning & Quiz Activity
                </h2>
                <p className="text-xs text-[#A1A1AA] mt-0.5">
                  Actual questions solved across recent practice days
                </p>
              </div>
              <Link
                href="/dashboard/analytics"
                className="text-xs text-[#C084FC] hover:underline font-semibold flex items-center gap-1"
              >
                Full Analytics <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            <div className="h-60 w-full mt-4">
              {analytics && analytics.recent_activity.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={analytics.recent_activity}>
                    <defs>
                      <linearGradient id="purpleGlow" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.6} />
                        <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0.0} />
                      </linearGradient>
                    </defs>
                    <XAxis
                      dataKey="date"
                      stroke="#A1A1AA"
                      fontSize={11}
                      tickLine={false}
                    />
                    <YAxis
                      stroke="#A1A1AA"
                      fontSize={11}
                      tickLine={false}
                      allowDecimals={false}
                    />
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
                      dataKey="questions_solved"
                      stroke="#A855F7"
                      strokeWidth={2}
                      fillOpacity={1}
                      fill="url(#purpleGlow)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex items-center justify-center text-xs text-[#A1A1AA]">
                  No quiz activity recorded yet. Take an assessment to populate your trends!
                </div>
              )}
            </div>
          </div>
        </GlowCard>

        {/* Priority Focus / Weak Topics (1 col) */}
        <GlowCard className="p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-400" /> Focus Areas
              </h2>
              <Link
                href="/dashboard/topics"
                className="text-xs text-[#C084FC] hover:underline font-semibold"
              >
                View All
              </Link>
            </div>
            <p className="text-xs text-[#A1A1AA] mb-4">
              Identified by the Intelligence Engine as needing repeated practice:
            </p>

            <div className="space-y-3">
              {analytics?.weak_topics && analytics.weak_topics.length > 0 ? (
                analytics.weak_topics.slice(0, 3).map((topic) => (
                  <div
                    key={topic.id}
                    className="p-3 rounded-lg bg-[#100B18] border border-[#30203F] flex items-center justify-between"
                  >
                    <div>
                      <div className="text-xs font-semibold text-white">
                        {topic.topic_name}
                      </div>
                      <div className="text-[10px] text-[#A1A1AA]">
                        {topic.subject_name} • Accuracy: {topic.accuracy_percentage}%
                      </div>
                    </div>
                    <Link
                      href={`/dashboard/quiz?topic_id=${topic.topic_id}`}
                      className="px-2.5 py-1 rounded bg-[#8B5CF6]/20 border border-[#A855F7]/40 text-[11px] font-semibold text-[#C084FC] hover:bg-[#8B5CF6]/30 transition-all"
                    >
                      Practice
                    </Link>
                  </div>
                ))
              ) : (
                <div className="p-4 rounded-lg bg-[#100B18] border border-[#30203F] text-xs text-[#A1A1AA] text-center">
                  All practiced topics are performing strongly, or no assessments attempted yet.
                </div>
              )}
            </div>
          </div>

          <div className="mt-5 pt-4 border-t border-[#30203F]">
            <Link
              href="/dashboard/study-planner"
              className="w-full py-2 rounded-lg bg-[#191225] border border-[#30203F] hover:border-purple-500/40 text-xs font-semibold text-white flex items-center justify-center gap-1.5 transition-all"
            >
              <BookOpen className="w-3.5 h-3.5 text-[#C084FC]" />
              <span>Review Adaptive Study Plan</span>
            </Link>
          </div>
        </GlowCard>
      </div>

      {/* Career Recommendations Section */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Compass className="w-5 h-5 text-[#C084FC]" /> Career Intelligence & Role Readiness
            </h2>
            <p className="text-xs text-[#A1A1AA] mt-0.5">
              Objective readiness projections derived from your verified academic competencies
            </p>
          </div>
          <Link
            href="/dashboard/careers"
            className="text-xs font-semibold text-[#C084FC] hover:underline flex items-center gap-1"
          >
            Explore All 8 Roles <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {recommendations.slice(0, 3).map((rec) => (
            <GlowCard key={rec.id} className="p-5 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-semibold px-2 py-0.5 rounded bg-purple-500/20 text-[#C084FC] border border-purple-500/30">
                    {rec.career_role.industry_demand} Demand
                  </span>
                  <span className="text-sm font-bold text-white">
                    {rec.match_score}% Match
                  </span>
                </div>
                <h3 className="text-base font-bold text-white mb-1">
                  {rec.career_role.title}
                </h3>
                <p className="text-xs text-[#A1A1AA] line-clamp-2 mb-3">
                  {rec.career_role.description}
                </p>
                <div className="text-[11px] text-[#A1A1AA]">
                  <span className="text-white font-medium">{rec.matching_skills.length}</span> matching skills •{" "}
                  <span className="text-amber-400 font-medium">{rec.missing_skills_count}</span> gaps
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-[#30203F] flex items-center justify-between">
                <Link
                  href={`/dashboard/skill-gaps?role_id=${rec.career_role.id}`}
                  className="text-xs font-semibold text-[#C084FC] hover:text-white flex items-center gap-1 transition-colors"
                >
                  Skill Gap Analysis <ArrowRight className="w-3.5 h-3.5" />
                </Link>
                <Link
                  href={`/dashboard/roadmaps?role_id=${rec.career_role.id}`}
                  className="text-xs text-[#A1A1AA] hover:text-white transition-colors"
                >
                  Roadmap
                </Link>
              </div>
            </GlowCard>
          ))}
        </div>
      </div>
    </div>
  );
}
