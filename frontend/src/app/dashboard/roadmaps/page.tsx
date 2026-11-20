"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import {
  Milestone,
  CheckCircle2,
  Circle,
  Sparkles,
  ArrowRight,
  FolderGit2,
  Compass,
  RotateCcw,
  Clock
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
          if (match) setActiveRoadmap(match);
          setSelectedRoleId(initialRoleId);
        } else if (existingRoadmaps.length > 0) {
          setActiveRoadmap(existingRoadmaps[0]);
          setSelectedRoleId(existingRoadmaps[0].career_role.id);
        } else if (rolesList.length > 0) {
          setSelectedRoleId(rolesList[0].id);
        }
      } catch (e) {
        console.error("Error initializing roadmaps:", e);
      }
    }
    init();
  }, [initialRoleId]);

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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Milestone className="w-5 h-5 text-[#C084FC]" /> Personalized Career Roadmap
          </h1>
          <p className="text-xs text-[#A1A1AA] mt-0.5">
            Step-by-step phased learning milestones, portfolio projects, and practice activities validated by career skill requirements.
          </p>
        </div>

        {/* Career Selector & Action */}
        <div className="flex items-center gap-2">
          <select
            value={selectedRoleId}
            onChange={(e) => {
              setSelectedRoleId(e.target.value);
              const found = roadmaps.find((r) => r.career_role.id === e.target.value);
              if (found) setActiveRoadmap(found);
            }}
            className="px-3 py-1.5 rounded-lg bg-[#191225] border border-[#30203F] text-xs font-semibold text-white focus:outline-none focus:border-[#A855F7]"
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
            className="px-4 py-1.5 rounded-lg text-xs font-bold bg-gradient-to-r from-[#8B5CF6] to-[#A855F7] text-white shadow-[0_0_12px_rgba(168,85,247,0.3)] hover:shadow-[0_0_18px_rgba(168,85,247,0.6)] disabled:opacity-50 transition-all flex items-center gap-1.5 shrink-0"
          >
            <Sparkles className="w-3.5 h-3.5" />
            {generating ? "Generating..." : activeRoadmap ? "Regenerate" : "Generate"}
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
                <h2 className="text-xl font-bold text-white mt-0.5">
                  {activeRoadmap.title}
                </h2>
                <div className="flex items-center gap-3 text-xs text-[#A1A1AA] mt-1">
                  <span className="flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5 text-[#C084FC]" /> {activeRoadmap.target_timeline_months} Months Target
                  </span>
                  <span>•</span>
                  <span>{activeRoadmap.milestones.length} Phased Milestones</span>
                </div>
              </div>

              <div className="text-right sm:border-l sm:border-[#30203F] sm:pl-6 shrink-0">
                <span className="text-3xl font-extrabold text-white">
                  {activeRoadmap.progress_percentage}%
                </span>
                <span className="text-xs text-[#C084FC] block font-semibold">
                  Milestone Completion
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
            <h3 className="text-base font-bold text-white">Learning Milestones & Actionable Projects</h3>
            {activeRoadmap.milestones.map((m, idx) => (
              <GlowCard
                key={m.id}
                className={`p-6 transition-all ${
                  m.is_completed ? "border-emerald-500/40 bg-[#120D1C]" : ""
                }`}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-3">
                    <button
                      onClick={() => handleToggleMilestone(m.id)}
                      className="mt-0.5 shrink-0 text-[#A855F7] hover:scale-110 transition-transform"
                      title={m.is_completed ? "Mark Incomplete" : "Mark Completed"}
                    >
                      {m.is_completed ? (
                        <CheckCircle2 className="w-6 h-6 text-emerald-400 fill-emerald-400/20" />
                      ) : (
                        <Circle className="w-6 h-6 text-[#A1A1AA]" />
                      )}
                    </button>

                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-[#A855F7] uppercase">
                          Phase {m.order_index}
                        </span>
                        {m.target_date && (
                          <span className="text-[10px] px-2 py-0.5 rounded bg-[#100B18] text-[#A1A1AA] border border-[#30203F]">
                            {m.target_date}
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
                      <p className="text-xs text-[#A1A1AA] mt-1 leading-relaxed">
                        {m.description}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Suggested Projects & Activities */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-5 pt-4 border-t border-[#30203F]">
                  <div className="p-3.5 rounded-lg bg-[#100B18] border border-[#30203F]">
                    <div className="text-xs font-bold text-[#C084FC] flex items-center gap-1.5 mb-2">
                      <FolderGit2 className="w-3.5 h-3.5" /> Suggested Industry Projects:
                    </div>
                    <ul className="space-y-1.5 text-xs text-gray-300">
                      {m.suggested_projects.map((proj, pIdx) => (
                        <li key={pIdx} className="flex items-start gap-2">
                          <span className="text-[#A855F7]">•</span>
                          <span>{proj}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="p-3.5 rounded-lg bg-[#100B18] border border-[#30203F]">
                    <div className="text-xs font-bold text-emerald-300 flex items-center gap-1.5 mb-2">
                      <CheckCircle2 className="w-3.5 h-3.5" /> Recommended Practice Activities:
                    </div>
                    <ul className="space-y-1.5 text-xs text-gray-300">
                      {m.practice_activities.map((act, aIdx) => (
                        <li key={aIdx} className="flex items-start gap-2">
                          <span className="text-emerald-400">•</span>
                          <span>{act}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </GlowCard>
            ))}
          </div>
        </div>
      ) : (
        <GlowCard className="p-12 text-center">
          <Milestone className="w-12 h-12 text-[#A1A1AA] mx-auto mb-3 opacity-50" />
          <h3 className="text-sm font-bold text-white mb-1">No Roadmap Generated Yet</h3>
          <p className="text-xs text-[#A1A1AA] max-w-sm mx-auto mb-4">
            Select a career role above and click &ldquo;Generate&rdquo; to build your tailored milestone sequence.
          </p>
          <button
            onClick={handleGenerateRoadmap}
            disabled={generating}
            className="px-5 py-2.5 rounded-lg text-xs font-bold bg-gradient-to-r from-[#8B5CF6] to-[#A855F7] text-white inline-flex items-center gap-2"
          >
            <Sparkles className="w-4 h-4" />
            {generating ? "Generating..." : "Generate Career Roadmap"}
          </button>
        </GlowCard>
      )}
    </div>
  );
}

export default function CareerRoadmapsPage() {
  return (
    <Suspense fallback={<div className="p-8 text-xs text-[#A1A1AA]">Loading career roadmaps...</div>}>
      <CareerRoadmapsContent />
    </Suspense>
  );
}
