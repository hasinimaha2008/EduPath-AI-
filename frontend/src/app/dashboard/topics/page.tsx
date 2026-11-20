"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Target, CheckCircle2, Award, AlertTriangle, ArrowRight, BookOpen } from "lucide-react";
import { GlowCard } from "@/components/GlowCard";
import { api } from "@/lib/api";
import { TopicPerformance } from "@/lib/types";

export default function TopicPerformancePage() {
  const [topics, setTopics] = useState<TopicPerformance[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterSubject, setFilterSubject] = useState<string>("all");

  useEffect(() => {
    async function loadData() {
      try {
        const res = await api.getTopicPerformance();
        setTopics(res);
      } catch (e) {
        console.error("Error loading topic performances:", e);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const subjects = Array.from(new Set(topics.map((t) => t.subject_name)));
  const filtered =
    filterSubject === "all"
      ? topics
      : topics.filter((t) => t.subject_name === filterSubject);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "mastered":
        return (
          <span className="px-2.5 py-1 rounded-full text-[11px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
            Mastered (≥90% & ≥3 Attempts)
          </span>
        );
      case "proficient":
        return (
          <span className="px-2.5 py-1 rounded-full text-[11px] font-bold bg-blue-500/20 text-blue-300 border border-blue-500/30">
            Proficient (≥75% & ≥2 Attempts)
          </span>
        );
      case "developing":
        return (
          <span className="px-2.5 py-1 rounded-full text-[11px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
            Developing (50% - 74%)
          </span>
        );
      default:
        return (
          <span className="px-2.5 py-1 rounded-full text-[11px] font-bold bg-red-500/20 text-red-300 border border-red-500/30">
            Needs Practice (&lt;50%)
          </span>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Target className="w-5 h-5 text-[#C084FC]" /> Topic-wise Performance Tracking
          </h1>
          <p className="text-xs text-[#A1A1AA] mt-0.5">
            Verified mastery requires repeated assessment consistency before marking an academic topic as mastered.
          </p>
        </div>

        {subjects.length > 0 && (
          <select
            value={filterSubject}
            onChange={(e) => setFilterSubject(e.target.value)}
            className="px-3 py-1.5 rounded-lg bg-[#191225] border border-[#30203F] text-xs text-white focus:outline-none focus:border-[#A855F7]"
          >
            <option value="all">All Subjects ({topics.length} topics)</option>
            {subjects.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        )}
      </div>

      {/* Grid of Topics */}
      {filtered.length === 0 ? (
        <GlowCard className="p-12 text-center">
          <BookOpen className="w-12 h-12 text-[#A1A1AA] mx-auto mb-3 opacity-50" />
          <h3 className="text-sm font-bold text-white mb-1">No Topic Records Yet</h3>
          <p className="text-xs text-[#A1A1AA] max-w-sm mx-auto mb-4">
            Attempt subject quizzes to record actual attempts and let the Intelligence Engine evaluate your mastery.
          </p>
          <Link
            href="/dashboard/quiz"
            className="px-4 py-2 rounded-lg text-xs font-bold bg-gradient-to-r from-[#8B5CF6] to-[#A855F7] text-white inline-flex items-center gap-2"
          >
            <CheckCircle2 className="w-4 h-4" /> Launch Quiz
          </Link>
        </GlowCard>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filtered.map((t) => (
            <GlowCard key={t.id} className="p-5 flex flex-col justify-between">
              <div>
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div>
                    <span className="text-[10px] font-bold text-[#A855F7] uppercase tracking-wider block">
                      {t.subject_name}
                    </span>
                    <h3 className="text-sm font-bold text-white mt-0.5">{t.topic_name}</h3>
                  </div>
                  <div>{getStatusBadge(t.mastery_status)}</div>
                </div>

                {/* Progress bar */}
                <div className="mt-4 mb-2">
                  <div className="flex justify-between text-[11px] mb-1">
                    <span className="text-[#A1A1AA]">Demonstrated Accuracy</span>
                    <span className="font-bold text-white">{t.accuracy_percentage}%</span>
                  </div>
                  <div className="w-full h-2 rounded-full bg-[#100B18] overflow-hidden border border-[#30203F]">
                    <div
                      className={`h-full transition-all duration-500 ${
                        t.accuracy_percentage >= 75
                          ? "bg-emerald-400"
                          : t.accuracy_percentage >= 50
                          ? "bg-amber-400"
                          : "bg-red-400"
                      }`}
                      style={{ width: `${Math.min(t.accuracy_percentage, 100)}%` }}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-2 mt-4 text-center">
                  <div className="p-2 rounded bg-[#100B18] border border-[#30203F]">
                    <span className="text-[10px] text-[#A1A1AA] block uppercase">Attempts</span>
                    <span className="text-xs font-bold text-white">{t.total_attempts}</span>
                  </div>
                  <div className="p-2 rounded bg-[#100B18] border border-[#30203F]">
                    <span className="text-[10px] text-emerald-400 block uppercase">Correct</span>
                    <span className="text-xs font-bold text-white">{t.correct_answers}</span>
                  </div>
                  <div className="p-2 rounded bg-[#100B18] border border-[#30203F]">
                    <span className="text-[10px] text-red-400 block uppercase">Incorrect</span>
                    <span className="text-xs font-bold text-white">{t.incorrect_answers}</span>
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-[#30203F] flex items-center justify-between">
                <span className="text-[10px] text-[#A1A1AA]">
                  Last practiced: {new Date(t.last_practiced_at).toLocaleDateString()}
                </span>
                <Link
                  href={`/dashboard/quiz?topic_id=${t.topic_id}`}
                  className="text-xs font-bold text-[#C084FC] hover:text-white flex items-center gap-1 transition-colors"
                >
                  Retest Topic <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </GlowCard>
          ))}
        </div>
      )}
    </div>
  );
}
