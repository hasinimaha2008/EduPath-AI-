"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import {
  Milestone,
  CheckCircle2,
  Circle,
  Sparkles,
  ArrowRight,
  FolderGit2,
  Compass,
  RotateCcw,
  Clock,
  BookOpen,
  Target,
  Award,
  Layers,
  ChevronRight,
  Bookmark
} from "lucide-react";
import { GlowCard } from "@/components/GlowCard";
import { api } from "@/lib/api";
import { CareerRoadmap, CareerRole } from "@/lib/types";

function CareerRoadmapsContent() {
  const searchParams = useSearchParams();
  const initialRoleId = searchParams.get("role_id");

  const [roles, setRoles] = useState<CareerRole[]>([]);
  const [selectedRoleId, setSelectedRoleId] = useState<string>(initialRoleId || "");
  const [roadmaps, setRoadmaps] = useState<CareerRoadmap[]>([]);
  const [activeRoadmap, setActiveRoadmap] = useState<CareerRoadmap | null>(null);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    async function init() {
      try {
        const [rolesList, existingRoadmaps] = await Promise.all([
          api.getCareerRoles().catch(() => []),
          api.listRoadmaps().catch(() => []),
        ]);
        setRoles(rolesList);
        setRoadmaps(existingRoadmaps);

        if (initialRoleId) {
          const match = existingRoadmaps.find((r) => r.career_role.id === initialRoleId);
          if (match) {
            setActiveRoadmap(match);
          } else {
            handleAutoGenerate(initialRoleId);
          }
          setSelectedRoleId(initialRoleId);
        } else if (existingRoadmaps.length > 0) {
          setActiveRoadmap(existingRoadmaps[0]);
          setSelectedRoleId(existingRoadmaps[0].career_role.id);
        } else if (rolesList.length > 0) {
          setSelectedRoleId(rolesList[0].id);
          handleAutoGenerate(rolesList[0].id);
        }
      } catch (e) {
        console.error("Error initializing roadmaps:", e);
      }
    }
    init();
  }, [initialRoleId]);

  const handleAutoGenerate = async (roleId: string) => {
    try {
      setGenerating(true);
      const newRm = await api.generateRoadmap(roleId, 6);
      setActiveRoadmap(newRm);
      setRoadmaps((prev) => [newRm, ...prev.filter((r) => r.id !== newRm.id)]);
    } catch (e) {
      console.error("Error auto-generating roadmap:", e);
    } finally {
      setGenerating(false);
    }
  };

  const handleGenerateRoadmap = async () => {
    if (!selectedRoleId) return;
    setGenerating(true);
    try {
      const newRm = await api.generateRoadmap(selectedRoleId, 6);
      setActiveRoadmap(newRm);
      setRoadmaps((prev) => [newRm, ...prev.filter((r) => r.id !== newRm.id)]);
    } catch (e) {
      console.error("Error generating roadmap:", e);
    } finally {
      setGenerating(false);
    }
  };

  const handleToggleMilestone = async (milestoneId: string) => {
    try {
      const res = await api.toggleMilestone(milestoneId);
      if (activeRoadmap) {
        const updatedMilestones = activeRoadmap.milestones.map((m) =>
          m.id === milestoneId ? { ...m, is_completed: res.is_completed } : m
        );
        setActiveRoadmap({
          ...activeRoadmap,
          progress_percentage: res.roadmap_progress,
          milestones: updatedMilestones,
        });
      }
    } catch (e) {
      console.error("Error toggling milestone:", e);
    }
  };

  const getStageBadge = (stage?: string, orderIndex: number = 1) => {
    const s = stage?.toLowerCase() || (orderIndex === 1 ? "beginner" : orderIndex === 2 ? "intermediate" : orderIndex === 3 ? "advanced" : "capstone");

    switch (s) {
      case "beginner":
        return <span className="px-2.5 py-0.5 rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/30 text-[10px] font-bold">Beginner Stage</span>;
      case "intermediate":
        return <span className="px-2.5 py-0.5 rounded-full bg-[#8B5CF6]/20 text-[#C084FC] border border-[#8B5CF6]/30 text-[10px] font-bold">Intermediate Stage</span>;
      case "advanced":
        return <span className="px-2.5 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30 text-[10px] font-bold">Advanced Stage</span>;
      default:
        return <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-[10px] font-bold">Capstone Stage</span>;
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#30203F] pb-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-white flex items-center gap-2">
            <Milestone className="w-6 h-6 text-[#C084FC]" /> Personalized Career Roadmap
          </h1>
          <p className="text-xs text-[#A1A1AA] mt-1">
            Structured career roadmap with Beginner, Intermediate, Advanced, and Capstone stages. Includes practical projects and learning resources.
          </p>
        </div>

        {/* Career Selector & Action */}
        <div className="flex items-center gap-2 self-start sm:self-auto">
          <select
            value={selectedRoleId}
            onChange={(e) => {
              setSelectedRoleId(e.target.value);
              const found = roadmaps.find((r) => r.career_role.id === e.target.value);
              if (found) {
                setActiveRoadmap(found);
              } else {
                handleAutoGenerate(e.target.value);
              }
            }}
            className="px-3 py-2 rounded-lg bg-[#191225] border border-[#30203F] text-xs font-bold text-white focus:outline-none focus:border-[#A855F7]"
          >
            {roles.map((r) => (
              <option key={r.id} value={r.id}>
                {r.title}
              </option>
            ))}
          </select>

          <button
            onClick={handleGenerateRoadmap}
            disabled={generating}
            className="px-4 py-2 rounded-lg text-xs font-bold bg-gradient-to-r from-[#8B5CF6] to-[#A855F7] text-white shadow-[0_0_12px_rgba(168,85,247,0.3)] hover:shadow-[0_0_18px_rgba(168,85,247,0.6)] disabled:opacity-50 transition-all flex items-center gap-1.5 shrink-0"
          >
            <Sparkles className="w-3.5 h-3.5" />
            {generating ? "Generating..." : activeRoadmap ? "Regenerate Roadmap" : "Generate Roadmap"}
          </button>
        </div>
      </div>

      {activeRoadmap ? (
        <div className="space-y-6">
          {/* Progress Header Card */}
          <GlowCard glow className="p-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <span className="text-[10px] font-bold text-[#A855F7] uppercase tracking-wider">
                  Target Career Pathway
                </span>
                <h2 className="text-xl sm:text-2xl font-bold text-white mt-0.5">
                  {activeRoadmap.title}
                </h2>
                <div className="flex items-center gap-3 text-xs text-[#A1A1AA] mt-1">
                  <span className="flex items-center gap-1 text-white font-medium">
                    <Clock className="w-3.5 h-3.5 text-[#C084FC]" /> {activeRoadmap.target_timeline_months} Months Target Duration
                  </span>
                  <span>•</span>
                  <span>{activeRoadmap.milestones.length} Phased Milestones</span>
                  <span>•</span>
                  <span className="text-emerald-400 font-bold">
                    {activeRoadmap.milestones.filter(m => m.is_completed).length} Completed
                  </span>
                </div>
              </div>

              <div className="text-right sm:border-l sm:border-[#30203F] sm:pl-6 shrink-0">
                <span className="text-3xl font-extrabold text-white">
                  {activeRoadmap.progress_percentage}%
                </span>
                <span className="text-xs text-[#C084FC] block font-semibold">
                  Milestone Progress
                </span>
              </div>
            </div>

            <div className="mt-4">
              <div className="w-full h-2 rounded-full bg-[#100B18] overflow-hidden border border-[#30203F]">
                <div
                  className="h-full bg-gradient-to-r from-[#8B5CF6] to-[#A855F7] transition-all duration-500"
                  style={{ width: `${Math.min(activeRoadmap.progress_percentage, 100)}%` }}
                />
              </div>
            </div>
          </GlowCard>

          {/* Phased Milestones Timeline */}
          <div className="space-y-4">
            <h3 className="text-base font-bold text-white">Structured Learning Stages & Industry Milestones</h3>
            {activeRoadmap.milestones.map((m, idx) => (
              <GlowCard
                key={m.id}
                className={`p-6 transition-all ${
                  m.is_completed ? "border-emerald-500/40 bg-[#120D1C]" : ""
                }`}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-3.5">
                    <button
                      onClick={() => handleToggleMilestone(m.id)}
                      className="mt-0.5 shrink-0 text-[#A855F7] hover:scale-110 transition-transform"
                      title={m.is_completed ? "Mark Incomplete" : "Mark Milestone Completed"}
                    >
                      {m.is_completed ? (
                        <CheckCircle2 className="w-6 h-6 text-emerald-400 fill-emerald-400/20" />
                      ) : (
                        <Circle className="w-6 h-6 text-[#A1A1AA]" />
                      )}
                    </button>

                    <div>
                      <div className="flex flex-wrap items-center gap-2 mb-1">
                        {getStageBadge(m.stage, m.order_index)}
                        {m.target_date && (
                          <span className="text-[10px] px-2 py-0.5 rounded bg-[#100B18] text-[#A1A1AA] border border-[#30203F]">
                            {m.target_date}
                          </span>
                        )}
                        {m.is_completed && (
                          <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-bold border border-emerald-500/30">
                            Completed ✓
                          </span>
                        )}
                      </div>
                      <h4
                        className={`text-base font-bold mt-1 ${
                          m.is_completed ? "line-through text-gray-400" : "text-white"
                        }`}
                      >
                        {m.title}
                      </h4>
                      <p className="text-xs text-[#A1A1AA] mt-1 leading-relaxed max-w-3xl">
                        {m.description}
                      </p>
                    </div>
                  </div>
                </div>

                {/* 3 Columns: Practical Projects, Learning Resources & Practice Activities */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-5 pt-4 border-t border-[#30203F]">
                  {/* Practical Projects */}
                  <div className="p-3.5 rounded-lg bg-[#100B18] border border-[#30203F]">
                    <div className="text-xs font-bold text-[#C084FC] flex items-center gap-1.5 mb-2">
                      <FolderGit2 className="w-3.5 h-3.5" /> Practical Industry Projects:
                    </div>
                    <ul className="space-y-1.5 text-xs text-gray-300">
                      {m.suggested_projects.map((proj, pIdx) => (
                        <li key={pIdx} className="flex items-start gap-2">
                          <span className="text-[#A855F7]">•</span>
                          <span className="leading-snug">{proj}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Learning Resources */}
                  <div className="p-3.5 rounded-lg bg-[#100B18] border border-[#30203F]">
                    <div className="text-xs font-bold text-purple-300 flex items-center gap-1.5 mb-2">
                      <Bookmark className="w-3.5 h-3.5 text-purple-400" /> Recommended Learning Resources:
                    </div>
                    <ul className="space-y-1.5 text-xs text-gray-300">
                      {(m.learning_resources && m.learning_resources.length > 0
                        ? m.learning_resources
                        : [
                            "Official Architecture & Specification Documents",
                            "Curated Academic Reference Textbooks",
                            "EduPath AI Smart Notes & Revision Cards"
                          ]
                      ).map((res, rIdx) => (
                        <li key={rIdx} className="flex items-start gap-2">
                          <span className="text-purple-400">•</span>
                          <span className="leading-snug">{res}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Practice Activities */}
                  <div className="p-3.5 rounded-lg bg-[#100B18] border border-[#30203F]">
                    <div className="text-xs font-bold text-emerald-300 flex items-center gap-1.5 mb-2">
                      <CheckCircle2 className="w-3.5 h-3.5" /> Practice Drills & Assessments:
                    </div>
                    <ul className="space-y-1.5 text-xs text-gray-300">
                      {m.practice_activities.map((act, aIdx) => (
                        <li key={aIdx} className="flex items-start gap-2">
                          <span className="text-emerald-400">•</span>
                          <span className="leading-snug">{act}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Quick Link to Quizzes / Notes */}
                <div className="mt-4 pt-3 border-t border-[#20152B] flex items-center justify-between text-xs">
                  <span className="text-[#71717A]">Stage {m.order_index} of {activeRoadmap.milestones.length}</span>
                  <div className="flex items-center gap-3">
                    <Link href="/dashboard/notes" className="text-[#A1A1AA] hover:text-white flex items-center gap-1">
                      <BookOpen className="w-3 h-3 text-[#C084FC]" /> Smart Notes
                    </Link>
                    <Link href="/dashboard/quiz" className="text-[#C084FC] hover:underline flex items-center gap-1 font-bold">
                      <Target className="w-3 h-3" /> Practice Quiz
                    </Link>
                  </div>
                </div>
              </GlowCard>
            ))}
          </div>
        </div>
      ) : (
        <div className="p-12 text-center text-xs text-[#A1A1AA]">
          {generating ? "Generating structured career roadmap..." : "Select a career role to view or generate its phased roadmap."}
        </div>
      )}
    </div>
  );
}

export default function CareerRoadmapsPage() {
  return (
    <Suspense fallback={<div className="p-8 text-xs text-[#A1A1AA]">Loading career roadmap...</div>}>
      <CareerRoadmapsContent />
    </Suspense>
  );
}
