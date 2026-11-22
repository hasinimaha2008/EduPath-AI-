"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import {
  Layers,
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  ArrowRight,
  ShieldAlert,
  Sparkles,
  BookOpen,
  FolderGit2,
  Bookmark,
  Check,
  ShieldCheck,
  Filter
} from "lucide-react";
import { GlowCard } from "@/components/GlowCard";
import { api } from "@/lib/api";
import { SkillGapResponse, CareerRole } from "@/lib/types";

function SkillGapContent() {
  const searchParams = useSearchParams();
  const initialRoleId = searchParams.get("role_id");

  const [roles, setRoles] = useState<CareerRole[]>([]);
  const [selectedRoleId, setSelectedRoleId] = useState<string>(initialRoleId || "");
  const [gapData, setGapData] = useState<SkillGapResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [filterStatus, setFilterStatus] = useState<"all" | "missing" | "needs_improvement" | "existing" | "high_priority">("all");

  useEffect(() => {
    async function loadRoles() {
      try {
        const rolesList = await api.getCareerRoles();
        setRoles(rolesList);
        if (rolesList.length > 0 && !selectedRoleId) {
          setSelectedRoleId(rolesList[0].id);
        }
      } catch (e) {
        console.error("Error loading roles:", e);
      }
    }
    loadRoles();
  }, []);

  useEffect(() => {
    if (!selectedRoleId) return;
    async function loadGaps() {
      setLoading(true);
      try {
        const data = await api.getSkillGaps(selectedRoleId);
        setGapData(data);
      } catch (e) {
        console.error("Error loading gaps:", e);
      } finally {
        setLoading(false);
      }
    }
    loadGaps();
  }, [selectedRoleId]);

  const getSourceBadge = (source: string, isVerified?: boolean) => {
    if (source === "demonstrated" || isVerified) {
      return (
        <span className="px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 text-[10px] font-bold flex items-center gap-1">
          <ShieldCheck className="w-3 h-3 text-emerald-400" />
          Verified (Quiz Evidence)
        </span>
      );
    } else if (source === "self_reported") {
      return (
        <span className="px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/40 text-[10px] font-bold flex items-center gap-1">
          Self-Reported Skill
        </span>
      );
    } else {
      return (
        <span className="px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/40 text-[10px] font-bold flex items-center gap-1">
          Missing Evidence
        </span>
      );
    }
  };

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case "High":
        return <span className="text-rose-400 font-bold text-[10px] px-2 py-0.5 rounded bg-rose-500/10 border border-rose-500/20">High Priority</span>;
      case "Medium":
        return <span className="text-amber-400 font-bold text-[10px] px-2 py-0.5 rounded bg-amber-500/10 border border-amber-500/20">Medium Priority</span>;
      default:
        return <span className="text-[#A1A1AA] text-[10px] px-2 py-0.5 rounded bg-[#100B18] border border-[#30203F]">Low Priority</span>;
    }
  };

  const filteredGaps = gapData?.gaps.filter(g => {
    if (filterStatus === "all") return true;
    if (filterStatus === "high_priority") return g.priority === "High";
    return g.status === filterStatus;
  }) || [];

  const verifiedCount = gapData?.gaps.filter(g => g.is_verified || g.evidence_source === "demonstrated").length || 0;
  const selfReportedCount = gapData?.gaps.filter(g => g.evidence_source === "self_reported").length || 0;
  const missingCount = gapData?.gaps.filter(g => g.status === "missing").length || 0;

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#30203F] pb-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-white flex items-center gap-2">
            <Layers className="w-6 h-6 text-[#C084FC]" /> Skill Gap Identification & Learning Guidance
          </h1>
          <p className="text-xs text-[#A1A1AA] mt-1">
            Compare skills required for target career against verified learning evidence. Clearly differentiates demonstrated from self-reported skills.
          </p>
        </div>

        {/* Career Selector */}
        <div className="flex items-center gap-2 self-start sm:self-auto">
          <label className="text-xs text-[#A1A1AA] uppercase font-semibold">Target Career:</label>
          <select
            value={selectedRoleId}
            onChange={(e) => setSelectedRoleId(e.target.value)}
            className="px-3.5 py-2 rounded-lg bg-[#191225] border border-[#30203F] text-xs font-bold text-white focus:outline-none focus:border-[#A855F7]"
          >
            {roles.map((r) => (
              <option key={r.id} value={r.id}>
                {r.title}
              </option>
            ))}
          </select>
        </div>
      </div>

      {gapData && (
        <>
          {/* Summary Card */}
          <GlowCard glow className="p-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <span className="text-[10px] font-bold text-[#A855F7] uppercase tracking-wider">
                  Target Role Readiness Profile
                </span>
                <h2 className="text-2xl font-extrabold text-white mt-0.5">
                  {gapData.career_role.title}
                </h2>
                <p className="text-xs text-[#A1A1AA] mt-1 max-w-xl leading-relaxed">
                  {gapData.career_role.description}
                </p>
              </div>

              <div className="text-right sm:border-l sm:border-[#30203F] sm:pl-6 shrink-0">
                <span className="text-3xl font-extrabold text-white">
                  {gapData.overall_readiness}%
                </span>
                <span className="text-xs text-[#C084FC] block font-semibold">
                  Overall Role Readiness
                </span>
              </div>
            </div>

            {/* Readiness Bar */}
            <div className="mt-5">
              <div className="w-full h-2 rounded-full bg-[#100B18] overflow-hidden border border-[#30203F]">
                <div
                  className="h-full bg-gradient-to-r from-[#8B5CF6] to-[#A855F7] transition-all duration-500"
                  style={{ width: `${Math.min(gapData.overall_readiness, 100)}%` }}
                />
              </div>
            </div>

            {/* Metrics Breakdown */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-5 pt-4 border-t border-[#30203F]">
              <div className="p-2.5 rounded-lg bg-[#100B18] border border-[#30203F]">
                <span className="text-[10px] text-[#A1A1AA] block">Total Required</span>
                <span className="text-base font-bold text-white">{gapData.gaps.length} Skills</span>
              </div>
              <div className="p-2.5 rounded-lg bg-[#100B18] border border-[#30203F]">
                <span className="text-[10px] text-emerald-400 block flex items-center gap-1">
                  <ShieldCheck className="w-3 h-3" /> Verified (Quiz)
                </span>
                <span className="text-base font-bold text-emerald-300">{verifiedCount} Skills</span>
              </div>
              <div className="p-2.5 rounded-lg bg-[#100B18] border border-[#30203F]">
                <span className="text-[10px] text-blue-400 block">Self-Reported</span>
                <span className="text-base font-bold text-blue-300">{selfReportedCount} Skills</span>
              </div>
              <div className="p-2.5 rounded-lg bg-[#100B18] border border-[#30203F]">
                <span className="text-[10px] text-rose-400 block">Missing Evidence</span>
                <span className="text-base font-bold text-rose-300">{missingCount} Skills</span>
              </div>
            </div>
          </GlowCard>

          {/* Filter Pills */}
          <div className="flex flex-wrap items-center gap-2 pt-2">
            <span className="text-xs text-[#A1A1AA] flex items-center gap-1 font-semibold mr-1">
              <Filter className="w-3.5 h-3.5 text-[#C084FC]" /> Filter Skills:
            </span>
            <button
              onClick={() => setFilterStatus("all")}
              className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
                filterStatus === "all"
                  ? "bg-[#8B5CF6] text-white border border-[#A855F7]"
                  : "bg-[#160F23] border border-[#30203F] text-[#A1A1AA] hover:text-white"
              }`}
            >
              All Skills ({gapData.gaps.length})
            </button>
            <button
              onClick={() => setFilterStatus("high_priority")}
              className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
                filterStatus === "high_priority"
                  ? "bg-rose-500 text-white border border-rose-400"
                  : "bg-[#160F23] border border-[#30203F] text-[#A1A1AA] hover:text-white"
              }`}
            >
              High Priority ({gapData.gaps.filter(g => g.priority === "High").length})
            </button>
            <button
              onClick={() => setFilterStatus("missing")}
              className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
                filterStatus === "missing"
                  ? "bg-[#8B5CF6] text-white border border-[#A855F7]"
                  : "bg-[#160F23] border border-[#30203F] text-[#A1A1AA] hover:text-white"
              }`}
            >
              Missing Skills ({missingCount})
            </button>
            <button
              onClick={() => setFilterStatus("needs_improvement")}
              className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
                filterStatus === "needs_improvement"
                  ? "bg-amber-500 text-white border border-amber-400"
                  : "bg-[#160F23] border border-[#30203F] text-[#A1A1AA] hover:text-white"
              }`}
            >
              Needs Improvement ({gapData.gaps.filter(g => g.status === "needs_improvement").length})
            </button>
            <button
              onClick={() => setFilterStatus("existing")}
              className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
                filterStatus === "existing"
                  ? "bg-emerald-500 text-white border border-emerald-400"
                  : "bg-[#160F23] border border-[#30203F] text-[#A1A1AA] hover:text-white"
              }`}
            >
              Mastered ({gapData.gaps.filter(g => g.status === "existing").length})
            </button>
          </div>

          {/* Detailed Skill Inventory Cards */}
          <div className="space-y-4">
            <h2 className="text-base font-bold text-white">Competency & Skill Gap Breakdown</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {filteredGaps.map((item, idx) => (
                <GlowCard key={idx} className="p-5 flex flex-col justify-between">
                  <div>
                    {/* Header */}
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-[10px] font-semibold text-[#A1A1AA] uppercase">
                            {item.category}
                          </span>
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-[#100B18] border border-[#30203F] text-[#D8B4FE]">
                            {item.job_market_importance || "Essential Core"}
                          </span>
                        </div>
                        <h3 className="text-sm font-bold text-white mt-1">{item.skill_name}</h3>
                      </div>
                      <div className="text-right flex flex-col items-end gap-1">
                        {getSourceBadge(item.evidence_source, item.is_verified)}
                        <div>{getPriorityBadge(item.priority)}</div>
                      </div>
                    </div>

                    {/* Proficiency Bar */}
                    <div className="mt-3 mb-2">
                      <div className="flex items-center justify-between text-xs mb-1">
                        <span className="text-[#A1A1AA]">Current Demonstrated Proficiency</span>
                        <span className="font-bold text-white">{item.proficiency}%</span>
                      </div>
                      <div className="w-full bg-[#100B18] h-1.5 rounded-full overflow-hidden border border-[#30203F]">
                        <div
                          className={`h-full rounded-full ${
                            item.proficiency >= 70 ? "bg-emerald-400" : item.proficiency >= 50 ? "bg-amber-400" : "bg-rose-500"
                          }`}
                          style={{ width: `${Math.min(item.proficiency, 100)}%` }}
                        />
                      </div>
                    </div>

                    {/* Learning Recommendation */}
                    <div className="p-3 rounded-lg bg-[#100B18] border border-[#30203F] text-xs text-[#D8B4FE] mt-3 leading-relaxed">
                      <strong className="text-white block mb-0.5">Learning Recommendation:</strong>
                      {item.learning_recommendation}
                    </div>

                    {/* Recommended Resources */}
                    {item.learning_resources && item.learning_resources.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-[#20152B]">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-[#A1A1AA] flex items-center gap-1 mb-1.5">
                          <Bookmark className="w-3 h-3 text-[#C084FC]" /> Curated Learning Resources
                        </span>
                        <ul className="text-[11px] text-[#A1A1AA] space-y-1 pl-3 list-disc">
                          {item.learning_resources.map((res, rIdx) => (
                            <li key={rIdx} className="leading-snug">{res}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Suggested Projects */}
                    {item.suggested_projects && item.suggested_projects.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-[#20152B]">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1 mb-1.5">
                          <FolderGit2 className="w-3 h-3 text-emerald-400" /> Practical Hands-on Projects
                        </span>
                        <ul className="text-[11px] text-[#D8B4FE] space-y-1 pl-3 list-disc">
                          {item.suggested_projects.map((proj, pIdx) => (
                            <li key={pIdx} className="leading-snug">{proj}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="mt-4 pt-3 border-t border-[#30203F] flex items-center justify-between">
                    <Link
                      href="/dashboard/quiz"
                      className="text-xs font-bold text-[#C084FC] hover:underline flex items-center gap-1"
                    >
                      Take Verification Quiz <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                    <Link
                      href={`/dashboard/roadmaps?role_id=${selectedRoleId}`}
                      className="text-xs text-[#A1A1AA] hover:text-white"
                    >
                      View in Roadmap
                    </Link>
                  </div>
                </GlowCard>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default function SkillGapPage() {
  return (
    <Suspense fallback={<div className="p-8 text-xs text-[#A1A1AA]">Loading skill gap analysis...</div>}>
      <SkillGapContent />
    </Suspense>
  );
}
