"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  Compass,
  ArrowRight,
  TrendingUp,
  DollarSign,
  Layers,
  Milestone,
  ShieldAlert,
  Info,
  CheckCircle2,
  GitCompare,
  FolderGit2,
  Route,
  Target,
  Wrench,
  Check,
  ChevronDown,
  ChevronUp
} from "lucide-react";
import { GlowCard } from "@/components/GlowCard";
import { api } from "@/lib/api";
import {
  CareerRecommendation,
  CareerComparisonResponse,
  CareerProjectItem,
  CareerPathwayItem,
  LearningProfile
} from "@/lib/types";

export default function CareerIntelligencePage() {
  const [recommendations, setRecommendations] = useState<CareerRecommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"readiness" | "compare" | "projects" | "pathways">("readiness");

  // Comparison State
  const [selectedRoleIds, setSelectedRoleIds] = useState<string[]>([]);
  const [comparisonData, setComparisonData] = useState<CareerComparisonResponse | null>(null);
  const [comparing, setComparing] = useState(false);

  // Projects State
  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const [projects, setProjects] = useState<CareerProjectItem[]>([]);
  const [loadingProjects, setLoadingProjects] = useState(false);
  const [expandedProject, setExpandedProject] = useState<string | null>(null);

  // Pathways State
  const [pathways, setPathways] = useState<CareerPathwayItem[]>([]);
  const [loadingPathways, setLoadingPathways] = useState(false);

  // Profile target career
  const [targetCareerId, setTargetCareerId] = useState<string>("");

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [data, profile] = await Promise.all([
          api.getCareerRecommendations(),
          api.getLearningProfile().catch(() => null)
        ]);
        setRecommendations(data);

        if (profile?.target_career_id) {
          setTargetCareerId(profile.target_career_id);
        }

        // Initialize comparison with top 2 roles
        if (data.length >= 2) {
          const top2 = [data[0].career_role.id, data[1].career_role.id];
          setSelectedRoleIds(top2);
          setSelectedProjectId(data[0].career_role.id);
        }
      } catch (e) {
        console.error("Error loading career data:", e);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleRunComparison = async (ids: string[]) => {
    if (ids.length < 2) return;
    try {
      setComparing(true);
      const res = await api.compareCareers(ids);
      setComparisonData(res);
    } catch (e) {
      console.error("Comparison error:", e);
    } finally {
      setComparing(false);
    }
  };

  const handleToggleComparisonRole = (roleId: string) => {
    let nextIds: string[];
    if (selectedRoleIds.includes(roleId)) {
      if (selectedRoleIds.length <= 2) return; // Keep at least 2
      nextIds = selectedRoleIds.filter(id => id !== roleId);
    } else {
      if (selectedRoleIds.length >= 4) return; // Max 4
      nextIds = [...selectedRoleIds, roleId];
    }
    setSelectedRoleIds(nextIds);
    handleRunComparison(nextIds);
  };

  const handleSelectProjectRole = async (roleId: string) => {
    setSelectedProjectId(roleId);
    try {
      setLoadingProjects(true);
      const projs = await api.getCareerProjects(roleId);
      setProjects(projs);
    } catch (e) {
      console.error("Projects error:", e);
    } finally {
      setLoadingProjects(false);
    }
  };

  const handleSelectPathwayRole = async (roleId: string) => {
    setSelectedProjectId(roleId);
    try {
      setLoadingPathways(true);
      const res = await api.getCareerPathways(roleId);
      setPathways(res.outbound_pathways || []);
    } catch (e) {
      console.error("Pathways error:", e);
    } finally {
      setLoadingPathways(false);
    }
  };

  const handleSetTargetCareer = async (roleId: string) => {
    try {
      await api.updateLearningProfile({ target_career_id: roleId });
      setTargetCareerId(roleId);
    } catch (e) {
      console.error("Failed to set target career:", e);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#30203F] pb-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Compass className="w-5 h-5 text-[#C084FC]" />
            Career Intelligence 2.0 & Pathway Navigation
          </h1>
          <p className="text-xs text-[#A1A1AA] mt-0.5">
            Dynamic career readiness projections derived from verified academic performance, multi-role comparisons, and practical projects.
          </p>
        </div>

        {/* Tab Controls */}
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-[#160F23] border border-[#30203F]">
          <button
            onClick={() => setActiveTab("readiness")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
              activeTab === "readiness"
                ? "bg-[#8B5CF6]/30 text-white border border-[#A855F7]/40 shadow-[0_0_10px_rgba(168,85,247,0.3)]"
                : "text-[#A1A1AA] hover:text-white"
            }`}
          >
            Readiness ({recommendations.length})
          </button>

          <button
            onClick={() => {
              setActiveTab("compare");
              if (!comparisonData && selectedRoleIds.length >= 2) {
                handleRunComparison(selectedRoleIds);
              }
            }}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ${
              activeTab === "compare"
                ? "bg-[#8B5CF6]/30 text-white border border-[#A855F7]/40 shadow-[0_0_10px_rgba(168,85,247,0.3)]"
                : "text-[#A1A1AA] hover:text-white"
            }`}
          >
            <GitCompare className="w-3.5 h-3.5" />
            <span>Role Comparison</span>
          </button>

          <button
            onClick={() => {
              setActiveTab("projects");
              if (selectedProjectId) {
                handleSelectProjectRole(selectedProjectId);
              }
            }}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ${
              activeTab === "projects"
                ? "bg-[#8B5CF6]/30 text-white border border-[#A855F7]/40 shadow-[0_0_10px_rgba(168,85,247,0.3)]"
                : "text-[#A1A1AA] hover:text-white"
            }`}
          >
            <FolderGit2 className="w-3.5 h-3.5" />
            <span>Projects</span>
          </button>

          <button
            onClick={() => {
              setActiveTab("pathways");
              if (selectedProjectId) {
                handleSelectPathwayRole(selectedProjectId);
              }
            }}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ${
              activeTab === "pathways"
                ? "bg-[#8B5CF6]/30 text-white border border-[#A855F7]/40 shadow-[0_0_10px_rgba(168,85,247,0.3)]"
                : "text-[#A1A1AA] hover:text-white"
            }`}
          >
            <Route className="w-3.5 h-3.5" />
            <span>Pathways</span>
          </button>
        </div>
      </div>

      {/* Advisory Banner (Mandatory Requirement) */}
      <div className="p-4 rounded-xl bg-purple-950/30 border border-purple-500/30 flex items-start gap-3 text-xs text-[#D8B4FE]">
        <Info className="w-5 h-5 text-[#C084FC] shrink-0 mt-0.5" />
        <div>
          <strong className="text-white block mb-0.5">Academic & Industry Advisory Notice</strong>
          EduPath AI provides curriculum-grounded skill evaluations and career suitability projections.
          These recommendations reflect your demonstrated strengths in academic assessments and do not promise or guarantee employment.
        </div>
      </div>

      {/* TAB 1: Career Readiness Grid */}
      {activeTab === "readiness" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {recommendations.map((rec) => {
            const role = rec.career_role;
            const isTarget = targetCareerId === role.id;
            return (
              <GlowCard key={rec.id} glow={rec.match_score >= 50} className="p-6 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between gap-2 mb-3">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-semibold px-2.5 py-1 rounded bg-[#8B5CF6]/20 text-[#C084FC] border border-[#A855F7]/30">
                        {role.industry_demand} Demand
                      </span>
                      {isTarget && (
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                          Target Goal
                        </span>
                      )}
                    </div>
                    <div className="text-right">
                      <span className="text-lg font-extrabold text-white">
                        {rec.match_score}%
                      </span>
                      <span className="text-[10px] text-[#A1A1AA] block">Readiness</span>
                    </div>
                  </div>

                  <h2 className="text-lg font-bold text-white mb-1.5">{role.title}</h2>
                  <p className="text-xs text-[#A1A1AA] leading-relaxed mb-4">{role.description}</p>

                  {/* Salary & Details */}
                  <div className="flex items-center gap-4 text-xs text-[#D8B4FE] mb-4 p-2.5 rounded bg-[#100B18] border border-[#30203F]">
                    <div className="flex items-center gap-1">
                      <DollarSign className="w-3.5 h-3.5 text-emerald-400" />
                      <span>{role.salary_range || "Market Competitive"}</span>
                    </div>
                    <div>•</div>
                    <div>{rec.matching_skills.length} Demonstrated</div>
                    <div>•</div>
                    <div className="text-amber-400">{rec.missing_skills_count} Skill Gaps</div>
                  </div>

                  {/* Rationale */}
                  <div className="p-3 rounded-lg bg-[#191225] border border-[#30203F] text-xs text-gray-300 mb-4">
                    <strong className="text-[#C084FC] block text-[11px] mb-1">Engine Rationale:</strong>
                    {rec.rationale}
                  </div>
                </div>

                {/* Actions */}
                <div className="pt-4 border-t border-[#30203F] flex flex-wrap items-center justify-between gap-2">
                  <button
                    onClick={() => handleSetTargetCareer(role.id)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1 transition-all ${
                      isTarget
                        ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                        : "bg-[#100B18] border border-[#30203F] text-[#A1A1AA] hover:text-white hover:border-[#8B5CF6]"
                    }`}
                  >
                    <Target className="w-3.5 h-3.5" />
                    <span>{isTarget ? "Targeted Career" : "Set as Target"}</span>
                  </button>

                  <div className="flex items-center gap-2">
                    <Link
                      href={`/dashboard/skill-gaps?role_id=${role.id}`}
                      className="px-3 py-1.5 rounded-lg bg-[#100B18] border border-[#30203F] hover:border-purple-500/50 text-xs font-bold text-white flex items-center gap-1.5 transition-all"
                    >
                      <Layers className="w-3.5 h-3.5 text-[#C084FC]" />
                      <span>Gaps</span>
                    </Link>

                    <Link
                      href={`/dashboard/roadmaps?role_id=${role.id}`}
                      className="px-3 py-1.5 rounded-lg bg-gradient-to-r from-[#8B5CF6] to-[#A855F7] text-xs font-bold text-white shadow-[0_0_12px_rgba(168,85,247,0.3)] hover:shadow-[0_0_18px_rgba(168,85,247,0.6)] flex items-center gap-1.5 transition-all"
                    >
                      <Milestone className="w-3.5 h-3.5" />
                      <span>Roadmap</span>
                    </Link>
                  </div>
                </div>
              </GlowCard>
            );
          })}
        </div>
      )}

      {/* TAB 2: Multi-Role Comparison */}
      {activeTab === "compare" && (
        <div className="p-6 rounded-2xl bg-[#160F23] border border-[#30203F] space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-[#30203F]">
            <div>
              <h2 className="text-base font-bold text-white">Side-by-Side Career Role Comparison</h2>
              <p className="text-xs text-[#A1A1AA]">Select 2 to 4 roles to compare demonstrated readiness, skill overlap, and market metrics.</p>
            </div>

            {/* Role Selectors */}
            <div className="flex flex-wrap gap-1.5">
              {recommendations.map((r) => {
                const isSelected = selectedRoleIds.includes(r.career_role.id);
                return (
                  <button
                    key={r.career_role.id}
                    onClick={() => handleToggleComparisonRole(r.career_role.id)}
                    className={`px-3 py-1 rounded-lg text-xs font-semibold border transition-all ${
                      isSelected
                        ? "bg-[#8B5CF6] text-white border-[#A855F7] shadow-[0_0_10px_rgba(168,85,247,0.4)]"
                        : "bg-[#191225] border-[#30203F] text-[#A1A1AA] hover:text-white"
                    }`}
                  >
                    {r.career_role.title}
                  </button>
                );
              })}
            </div>
          </div>

          {comparing ? (
            <div className="p-12 text-center text-xs text-[#A1A1AA] animate-pulse">
              Computing multi-role readiness and skill divergence...
            </div>
          ) : comparisonData ? (
            <div className="space-y-6">
              {/* Shared Skills Banner */}
              {comparisonData.shared_skills.length > 0 && (
                <div className="p-4 rounded-xl bg-purple-950/20 border border-purple-500/30 flex items-center gap-3">
                  <CheckCircle2 className="w-5 h-5 text-[#C084FC] shrink-0" />
                  <div className="text-xs">
                    <span className="font-bold text-white">Shared Competencies across compared roles: </span>
                    <span className="text-[#D4D4D8]">{comparisonData.shared_skills.join(", ")}</span>
                  </div>
                </div>
              )}

              {/* Side-by-Side Table */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {comparisonData.compared_roles.map((cr) => (
                  <div key={cr.id} className="p-5 rounded-xl bg-[#191225] border border-[#30203F] space-y-4 flex flex-col justify-between">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-bold text-white">{cr.title}</span>
                        <span className="text-base font-black text-[#C084FC]">{cr.readiness_score}%</span>
                      </div>

                      <div className="space-y-1 text-xs text-[#A1A1AA] pb-3 border-b border-[#30203F]">
                        <p><span className="text-[#71717A]">Salary:</span> {cr.salary_range}</p>
                        <p><span className="text-[#71717A]">Demand:</span> {cr.industry_demand}</p>
                      </div>

                      {/* Demonstrated Skills */}
                      <div className="pt-3 space-y-1.5">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-400 block">
                          Demonstrated ({cr.demonstrated_skills.length})
                        </span>
                        {cr.demonstrated_skills.length === 0 ? (
                          <span className="text-[11px] text-[#71717A] italic">None demonstrated yet</span>
                        ) : (
                          cr.demonstrated_skills.map((s, i) => (
                            <div key={i} className="text-[11px] text-[#D4D4D8] flex items-center justify-between">
                              <span className="truncate">{s.skill}</span>
                              <span className="text-emerald-400 font-bold">{s.proficiency}%</span>
                            </div>
                          ))
                        )}
                      </div>

                      {/* Missing Skills */}
                      <div className="pt-3 space-y-1.5">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-rose-400 block">
                          Missing or Needs Improvement ({cr.missing_skills.length + cr.in_progress_skills.length})
                        </span>
                        {[...cr.in_progress_skills, ...cr.missing_skills].slice(0, 4).map((s, i) => (
                          <div key={i} className="text-[11px] text-[#A1A1AA] flex items-center justify-between">
                            <span className="truncate">{s.skill}</span>
                            <span className="text-rose-400 text-[10px]">{s.proficiency}% / {s.target}%</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <Link
                      href={`/dashboard/roadmaps?role_id=${cr.id}`}
                      className="w-full text-center py-2 rounded-lg bg-[#251A38] border border-[#382650] hover:border-[#8B5CF6] text-xs font-bold text-white transition-all block mt-4"
                    >
                      View Roadmap →
                    </Link>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="p-8 text-center text-xs text-[#71717A]">Select roles and click Run Comparison.</div>
          )}
        </div>
      )}

      {/* TAB 3: Practical Portfolio Projects */}
      {activeTab === "projects" && (
        <div className="p-6 rounded-2xl bg-[#160F23] border border-[#30203F] space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-[#30203F]">
            <div>
              <h2 className="text-base font-bold text-white">Practical Project Recommendations</h2>
              <p className="text-xs text-[#A1A1AA]">Real-world portfolio projects complete with tools, step-by-step guides, and competency verification.</p>
            </div>

            {/* Career Selector */}
            <select
              value={selectedProjectId}
              onChange={(e) => handleSelectProjectRole(e.target.value)}
              className="px-3.5 py-2 rounded-xl bg-[#191225] border border-[#30203F] text-xs font-semibold text-white focus:outline-none focus:border-[#8B5CF6]"
            >
              {recommendations.map((r) => (
                <option key={r.career_role.id} value={r.career_role.id}>
                  {r.career_role.title} Projects
                </option>
              ))}
            </select>
          </div>

          {loadingProjects ? (
            <div className="p-12 text-center text-xs text-[#A1A1AA] animate-pulse">
              Loading practical portfolio projects...
            </div>
          ) : projects.length === 0 ? (
            <div className="p-8 text-center text-xs text-[#71717A]">No projects cataloged for this role yet.</div>
          ) : (
            <div className="space-y-4">
              {projects.map((proj) => {
                const isExpanded = expandedProject === proj.id;
                return (
                  <div key={proj.id} className="p-5 rounded-xl bg-[#191225] border border-[#30203F] space-y-4">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-bold text-white">{proj.title}</span>
                        <span className="px-2 py-0.5 rounded-full bg-purple-500/20 text-[#C084FC] text-[10px] font-bold border border-purple-500/30">
                          {proj.difficulty}
                        </span>
                      </div>
                      <span className="text-xs text-[#A1A1AA] font-semibold">{proj.competency_focus}</span>
                    </div>

                    <p className="text-xs text-[#D4D4D8] leading-relaxed">{proj.objective}</p>

                    {/* Tools & Skills */}
                    <div className="flex flex-wrap gap-2 text-xs">
                      <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#100B18] border border-[#30203F] text-[#C084FC]">
                        <Wrench className="w-3.5 h-3.5" />
                        <span>Tools: {proj.tools.join(", ")}</span>
                      </div>
                    </div>

                    {/* Expected Outcome */}
                    <div className="p-3 rounded-lg bg-[#251A38] border border-[#382650] text-xs text-[#D4D4D8]">
                      <span className="font-bold text-white">Expected Portfolio Outcome: </span>
                      {proj.expected_outcome}
                    </div>

                    {/* Steps Toggle */}
                    <button
                      onClick={() => setExpandedProject(isExpanded ? null : proj.id)}
                      className="text-xs text-[#C084FC] hover:text-white font-bold flex items-center gap-1 transition-colors"
                    >
                      {isExpanded ? (
                        <>
                          <span>Hide Implementation Steps</span>
                          <ChevronUp className="w-3.5 h-3.5" />
                        </>
                      ) : (
                        <>
                          <span>View Step-by-Step Implementation Guide ({proj.steps.length} Steps)</span>
                          <ChevronDown className="w-3.5 h-3.5" />
                        </>
                      )}
                    </button>

                    {isExpanded && (
                      <div className="pt-3 border-t border-[#30203F] space-y-2">
                        {proj.steps.map((st, i) => (
                          <div key={i} className="flex items-start gap-2.5 text-xs text-[#D4D4D8]">
                            <span className="w-5 h-5 rounded-full bg-[#2A1D45] text-[#C084FC] text-[10px] font-bold flex items-center justify-center shrink-0 mt-0.5">
                              {i + 1}
                            </span>
                            <p className="leading-relaxed">{st}</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* TAB 4: Career Pathways */}
      {activeTab === "pathways" && (
        <div className="p-6 rounded-2xl bg-[#160F23] border border-[#30203F] space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-[#30203F]">
            <div>
              <h2 className="text-base font-bold text-white">Career Transition Pathways</h2>
              <p className="text-xs text-[#A1A1AA]">Understand transition difficulty, required bridge competencies, and guidance between industry roles.</p>
            </div>

            {/* From Role Selector */}
            <select
              value={selectedProjectId}
              onChange={(e) => handleSelectPathwayRole(e.target.value)}
              className="px-3.5 py-2 rounded-xl bg-[#191225] border border-[#30203F] text-xs font-semibold text-white focus:outline-none focus:border-[#8B5CF6]"
            >
              {recommendations.map((r) => (
                <option key={r.career_role.id} value={r.career_role.id}>
                  Transition From: {r.career_role.title}
                </option>
              ))}
            </select>
          </div>

          {loadingPathways ? (
            <div className="p-12 text-center text-xs text-[#A1A1AA] animate-pulse">
              Loading career pathway options...
            </div>
          ) : pathways.length === 0 ? (
            <div className="p-8 text-center text-xs text-[#71717A]">No transition pathways mapped for this role yet.</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {pathways.map((pw) => (
                <div key={pw.id} className="p-5 rounded-xl bg-[#191225] border border-[#30203F] space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-bold text-white">Transition to {pw.target_role_title}</span>
                    <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${
                      pw.transition_difficulty === "Smooth"
                        ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/30"
                        : pw.transition_difficulty === "Moderate"
                        ? "bg-purple-500/20 text-purple-300 border-purple-500/30"
                        : "bg-rose-500/20 text-rose-300 border-rose-500/30"
                    }`}>
                      {pw.transition_difficulty} Transition
                    </span>
                  </div>

                  <p className="text-xs text-[#D4D4D8] leading-relaxed">{pw.guidance}</p>

                  <div className="pt-2">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-[#A1A1AA] block mb-1">
                      Bridge Skills to Acquire:
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {pw.bridge_skills.map((bs, i) => (
                        <span key={i} className="px-2 py-0.5 rounded bg-[#251A38] text-[#C084FC] text-[11px] font-medium border border-[#382650]">
                          {bs}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
