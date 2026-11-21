"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  Target,
  CheckCircle2,
  Award,
  AlertTriangle,
  ArrowRight,
  BookOpen,
  Sparkles,
  Zap,
  Calendar,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  FileText,
  Bot,
  Layers,
  Filter
} from "lucide-react";
import { GlowCard } from "@/components/GlowCard";
import { api } from "@/lib/api";
import { Subject, Topic, TopicPerformance } from "@/lib/types";

export default function TopicPerformancePage() {
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [performances, setPerformances] = useState<TopicPerformance[]>([]);
  const [selectedSubjectId, setSelectedSubjectId] = useState<string>("");
  const [filterMode, setFilterMode] = useState<"all" | "core" | "emerging">("all");
  const [expandedTopicId, setExpandedTopicId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [subs, perfs] = await Promise.all([
          api.getSubjects().catch(() => []),
          api.getTopicPerformance().catch(() => []),
        ]);
        setSubjects(subs);
        setPerformances(perfs);
        if (subs.length > 0) {
          setSelectedSubjectId(subs[0].id);
        }
      } catch (e) {
        console.error("Error loading curriculum topics & performances:", e);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const currentSubject = subjects.find((s) => s.id === selectedSubjectId);
  const rawTopics = currentSubject?.topics || [];

  // Filter topics by Core vs Emerging
  const filteredTopics = rawTopics.filter((t) => {
    if (filterMode === "emerging") return t.is_emerging;
    if (filterMode === "core") return !t.is_emerging;
    return true;
  });

  // Group topics by Module/Unit
  const moduleGroups = filteredTopics.reduce((acc, topic) => {
    const mod = topic.module_name || "General Module";
    if (!acc[mod]) acc[mod] = [];
    acc[mod].push(topic);
    return acc;
  }, {} as Record<string, Topic[]>);

  // Performance lookup map: topic_id -> TopicPerformance
  const perfMap = new Map(performances.map((p) => [p.topic_id, p]));

  const getStatusBadge = (status?: string) => {
    if (!status) {
      return (
        <span className="px-2.5 py-1 rounded-full text-[11px] font-semibold bg-gray-500/10 text-[#A1A1AA] border border-gray-500/20">
          Not Attempted Yet
        </span>
      );
    }
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
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Target className="w-5 h-5 text-[#C084FC]" /> Multi-Subject Topics & Mastery Tracking
          </h1>
          <p className="text-xs text-[#A1A1AA] mt-0.5">
            Explore 16 canonical subjects organized unit-wise, discover emerging industry technologies, and review verified mastery evidence.
          </p>
        </div>

        {/* Core vs Emerging Filter */}
        <div className="flex items-center gap-1.5 p-1 bg-[#100B18] border border-[#30203F] rounded-xl self-start sm:self-auto">
          <button
            onClick={() => setFilterMode("all")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
              filterMode === "all" ? "bg-purple-900/60 text-white border border-[#A855F7]/40" : "text-[#A1A1AA] hover:text-white"
            }`}
          >
            All Topics
          </button>
          <button
            onClick={() => setFilterMode("core")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
              filterMode === "core" ? "bg-purple-900/60 text-white border border-[#A855F7]/40" : "text-[#A1A1AA] hover:text-white"
            }`}
          >
            Core Syllabus
          </button>
          <button
            onClick={() => setFilterMode("emerging")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1 ${
              filterMode === "emerging" ? "bg-amber-500/20 text-amber-300 border border-amber-500/40" : "text-[#A1A1AA] hover:text-white"
            }`}
          >
            <Zap className="w-3 h-3 text-amber-400" /> Emerging Tech
          </button>
        </div>
      </div>

      {/* Subject Selector Tabs */}
      <div className="space-y-2">
        <label className="text-[11px] font-bold text-[#A1A1AA] uppercase tracking-wider block">
          Select Academic Subject ({subjects.length} Subjects Available)
        </label>
        <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-8 gap-2">
          {subjects.map((sub) => {
            const isSelected = sub.id === selectedSubjectId;
            return (
              <button
                key={sub.id}
                onClick={() => setSelectedSubjectId(sub.id)}
                className={`p-2.5 rounded-xl border text-left transition-all ${
                  isSelected
                    ? "bg-gradient-to-r from-purple-900/60 to-purple-800/40 text-white border-[#A855F7] shadow-[0_0_15px_-3px_rgba(168,85,247,0.4)]"
                    : "bg-[#100B18] text-[#A1A1AA] border-[#30203F] hover:border-purple-500/40 hover:text-white"
                }`}
              >
                <div className="font-bold text-xs truncate" title={sub.name}>{sub.name}</div>
                <div className="text-[10px] text-[#C084FC] mt-0.5 truncate">{sub.code || "CS"}</div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Subject Header Card */}
      {currentSubject && (
        <GlowCard glow className="p-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className="px-2.5 py-0.5 rounded-md text-[11px] font-bold bg-purple-500/20 text-[#C084FC] border border-[#A855F7]/30">
                  {currentSubject.code || "CS Subject"}
                </span>
                <span className="text-xs text-[#A1A1AA]">&bull; {currentSubject.category || "Computer Science"}</span>
                <span className="text-xs text-purple-300">&bull; {rawTopics.length} Curriculum Topics</span>
              </div>
              <h2 className="text-xl font-extrabold text-white">{currentSubject.name}</h2>
              <p className="text-xs sm:text-sm text-[#A1A1AA] mt-1 max-w-2xl leading-relaxed">
                {currentSubject.description}
              </p>
            </div>

            <div className="flex items-center gap-3 shrink-0">
              <Link
                href="/dashboard/quiz"
                className="px-4 py-2.5 rounded-xl text-xs font-bold bg-gradient-to-r from-[#8B5CF6] to-[#A855F7] text-white shadow-[0_0_15px_rgba(168,85,247,0.4)] hover:shadow-[0_0_25px_rgba(168,85,247,0.7)] transition-all flex items-center gap-1.5"
              >
                <CheckCircle2 className="w-4 h-4" /> Generate Subject Quiz
              </Link>
            </div>
          </div>
        </GlowCard>
      )}

      {/* Module-Wise Topics Display */}
      {Object.keys(moduleGroups).length === 0 ? (
        <GlowCard className="p-12 text-center">
          <BookOpen className="w-12 h-12 text-[#A1A1AA] mx-auto mb-3 opacity-50" />
          <h3 className="text-sm font-bold text-white mb-1">No Topics Match Current Filter</h3>
          <p className="text-xs text-[#A1A1AA]">
            Try switching to &quot;All Topics&quot; to view all core syllabus and emerging industry concepts.
          </p>
        </GlowCard>
      ) : (
        <div className="space-y-6">
          {Object.entries(moduleGroups).map(([moduleName, moduleTopics]) => (
            <div key={moduleName} className="space-y-3">
              {/* Module Header */}
              <div className="flex items-center gap-2 px-1">
                <Layers className="w-4 h-4 text-[#C084FC]" />
                <h3 className="text-sm font-bold text-white uppercase tracking-wider">{moduleName}</h3>
                <span className="text-xs text-[#A1A1AA]">({moduleTopics.length} Topics)</span>
              </div>

              {/* Topics in this Module */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {moduleTopics.map((topic) => {
                  const perf = perfMap.get(topic.id);
                  const isExpanded = expandedTopicId === topic.id;
                  const subtopics = topic.subtopics || [];

                  return (
                    <GlowCard key={topic.id} className="p-5 space-y-3 flex flex-col justify-between">
                      <div>
                        {/* Topic Status Badges */}
                        <div className="flex items-center justify-between gap-2 mb-2">
                          {topic.is_emerging ? (
                            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40 flex items-center gap-1">
                              <Zap className="w-3 h-3 text-amber-400" /> Emerging Industry Tech
                            </span>
                          ) : (
                            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-purple-500/20 text-[#C084FC] border border-purple-500/30">
                              Core Syllabus
                            </span>
                          )}
                          {getStatusBadge(perf?.mastery_status)}
                        </div>

                        {/* Topic Title & Description */}
                        <h4 className="text-sm font-bold text-white">{topic.name}</h4>
                        <p className="text-xs text-[#A1A1AA] mt-1 leading-relaxed">{topic.description}</p>

                        {/* Verified Educational Source Reference */}
                        {topic.source_reference && (
                          <div className="mt-3 p-2.5 rounded-lg bg-[#100B18] border border-[#30203F] text-[11px] text-[#A1A1AA] flex items-center justify-between gap-2">
                            <span className="truncate" title={topic.source_reference}>
                              <strong className="text-white">Source:</strong> {topic.source_reference}
                            </span>
                            {topic.last_updated_date && (
                              <span className="text-[10px] text-[#C084FC] shrink-0 font-mono">
                                Updated {topic.last_updated_date}
                              </span>
                            )}
                          </div>
                        )}

                        {/* Subtopics Accordion */}
                        {subtopics.length > 0 && (
                          <div className="mt-3">
                            <button
                              onClick={() => setExpandedTopicId(isExpanded ? null : topic.id)}
                              className="text-[11px] font-semibold text-[#C084FC] hover:text-white flex items-center gap-1 transition-colors"
                            >
                              <span>{isExpanded ? "Hide Subtopics" : `View Subtopics (${subtopics.length})`}</span>
                              {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                            </button>

                            {isExpanded && (
                              <ul className="mt-2 space-y-1 pl-2 border-l border-purple-500/30 text-xs text-[#A1A1AA]">
                                {subtopics.map((st, i) => (
                                  <li key={i} className="flex items-center gap-1.5">
                                    <div className="w-1 h-1 rounded-full bg-[#A855F7]" />
                                    <span>{st}</span>
                                  </li>
                                ))}
                              </ul>
                            )}
                          </div>
                        )}

                        {/* Performance Details if Attempted */}
                        {perf && (
                          <div className="mt-3 grid grid-cols-3 gap-2 p-2.5 rounded-lg bg-[#100B18] border border-[#30203F] text-center">
                            <div>
                              <div className="text-xs font-bold text-white">{perf.total_attempts}</div>
                              <div className="text-[10px] text-[#A1A1AA]">Attempts</div>
                            </div>
                            <div>
                              <div className="text-xs font-bold text-emerald-400">{perf.accuracy_percentage}%</div>
                              <div className="text-[10px] text-[#A1A1AA]">Accuracy</div>
                            </div>
                            <div>
                              <div className="text-xs font-bold text-[#C084FC]">
                                {perf.correct_answers}/{perf.total_attempts}
                              </div>
                              <div className="text-[10px] text-[#A1A1AA]">Correct</div>
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Topic Action Buttons */}
                      <div className="pt-3 border-t border-[#30203F] flex items-center justify-between gap-2">
                        <Link
                          href={`/dashboard/quiz`}
                          className="px-3 py-1.5 rounded-lg text-[11px] font-bold bg-[#100B18] hover:bg-[#8B5CF6]/20 border border-[#30203F] hover:border-[#A855F7] text-white transition-all flex items-center gap-1"
                        >
                          <CheckCircle2 className="w-3 h-3 text-[#A855F7]" /> Practice Quiz
                        </Link>
                        <Link
                          href={`/dashboard/notes`}
                          className="px-3 py-1.5 rounded-lg text-[11px] font-bold bg-[#100B18] hover:bg-purple-950/40 border border-[#30203F] hover:border-purple-500 text-purple-300 transition-all flex items-center gap-1"
                        >
                          <FileText className="w-3 h-3" /> Smart Notes
                        </Link>
                        <Link
                          href={`/dashboard/assistant`}
                          className="px-3 py-1.5 rounded-lg text-[11px] font-bold bg-[#100B18] hover:bg-purple-950/40 border border-[#30203F] hover:border-purple-500 text-purple-300 transition-all flex items-center gap-1"
                        >
                          <Bot className="w-3 h-3 text-[#C084FC]" /> Ask AI
                        </Link>
                      </div>
                    </GlowCard>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
