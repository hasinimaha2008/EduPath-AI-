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
  BookOpen
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

  const getSourceBadge = (source: string) => {
    if (source === "demonstrated") {
      return (
        <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-[10px] font-bold">
          Demonstrated (Verified Quiz)
        </span>
      );
    } else if (source === "self_reported") {
      return (
        <span className="px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 border border-blue-500/30 text-[10px] font-bold">
          Self-Reported
        </span>
      );
    } else {
      return (
        <span className="px-2 py-0.5 rounded bg-red-500/20 text-red-300 border border-red-500/30 text-[10px] font-bold">
          Missing Evidence
        </span>
      );
    }
  };

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case "High":
        return <span className="text-red-400 font-bold text-[10px]">High Priority</span>;
      case "Medium":
        return <span className="text-amber-400 font-bold text-[10px]">Medium Priority</span>;
      default:
        return <span className="text-[#A1A1AA] text-[10px]">Low Priority</span>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Layers className="w-5 h-5 text-[#C084FC]" /> Skill Gap Identification
          </h1>
          <p className="text-xs text-[#A1A1AA] mt-0.5">
            Compare skills required for target career against verified learning evidence. Clearly differentiates demonstrated from self-reported skills.
          </p>
        </div>

        {/* Career Selector */}
        <div className="flex items-center gap-2">
          <label className="text-xs text-[#A1A1AA] uppercase font-semibold">Target Career:</label>
          <select
            value={selectedRoleId}
            onChange={(e) => setSelectedRoleId(e.target.value)}
            className="px-3 py-1.5 rounded-lg bg-[#191225] border border-[#30203F] text-xs font-semibold text-white focus:outline-none focus:border-[#A855F7]"
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
                <p className="text-xs text-[#A1A1AA] mt-1 max-w-xl">
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

            <div className="mt-5">
              <div className="w-full h-2 rounded-full bg-[#100B18] overflow-hidden border border-[#30203F]">
                <div
                  className="h-full bg-gradient-to-r from-[#8B5CF6] to-[#A855F7] transition-all duration-500"
                  style={{ width: `${Math.min(gapData.overall_readiness, 100)}%` }}
                />
              </div>
            </div>
          </GlowCard>

          {/* Detailed Skill Breakdown */}
          <div className="space-y-4">
            <h2 className="text-base font-bold text-white">Competency & Skill Inventory</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {gapData.gaps.map((item, idx) => (
                <GlowCard key={idx} className="p-5 flex flex-col justify-between">
                  <div>
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <div>
                        <span className="text-[10px] font-semibold text-[#A1A1AA] uppercase">
                          {item.category}
                        </span>
                        <h3 className="text-sm font-bold text-white mt-0.5">{item.skill_name}</h3>
                      </div>
                      <div className="text-right">
                        {getSourceBadge(item.evidence_source)}
                        <div className="mt-1">{getPriorityBadge(item.priority)}</div>
                      </div>
                    </div>

                    <div className="mt-3 mb-2 flex items-center justify-between text-xs">
                      <span className="text-[#A1A1AA]">Demonstrated Proficiency</span>
                      <span className="font-bold text-white">{item.proficiency}%</span>
                    </div>

                    <div className="p-3 rounded-lg bg-[#100B18] border border-[#30203F] text-xs text-[#D8B4FE] mt-3">
                      <strong>Learning Recommendation:</strong> {item.learning_recommendation}
                    </div>
                  </div>

                  <div className="mt-4 pt-3 border-t border-[#30203F] flex items-center justify-between">
                    <Link
                      href="/dashboard/quiz"
                      className="text-xs font-semibold text-[#C084FC] hover:text-white flex items-center gap-1"
                    >
                      Take Topic Quiz <ArrowRight className="w-3.5 h-3.5" />
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
