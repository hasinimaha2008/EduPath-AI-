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
  CheckCircle2
} from "lucide-react";
import { GlowCard } from "@/components/GlowCard";
import { api } from "@/lib/api";
import { CareerRecommendation } from "@/lib/types";

export default function CareerIntelligencePage() {
  const [recommendations, setRecommendations] = useState<CareerRecommendation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await api.getCareerRecommendations();
        setRecommendations(data);
      } catch (e) {
        console.error("Error loading career recommendations:", e);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <Compass className="w-5 h-5 text-[#C084FC]" /> Career Intelligence & Industry Recommendations
        </h1>
        <p className="text-xs text-[#A1A1AA] mt-0.5">
          Dynamic career readiness projections derived from your verified academic performance and topic assessments.
        </p>
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

      {/* 8 Career Roles Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {recommendations.map((rec) => {
          const role = rec.career_role;
          return (
            <GlowCard key={rec.id} glow={rec.match_score >= 50} className="p-6 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between gap-2 mb-3">
                  <span className="text-xs font-semibold px-2.5 py-1 rounded bg-[#8B5CF6]/20 text-[#C084FC] border border-[#A855F7]/30">
                    {role.industry_demand} Demand
                  </span>
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
                  <div>{rec.matching_skills.length} Demonstrated Skills</div>
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
              <div className="pt-4 border-t border-[#30203F] flex items-center justify-between">
                <Link
                  href={`/dashboard/skill-gaps?role_id=${role.id}`}
                  className="px-3.5 py-1.5 rounded-lg bg-[#100B18] border border-[#30203F] hover:border-purple-500/50 text-xs font-bold text-white flex items-center gap-1.5 transition-all"
                >
                  <Layers className="w-3.5 h-3.5 text-[#C084FC]" />
                  <span>Identify Gaps</span>
                </Link>

                <Link
                  href={`/dashboard/roadmaps?role_id=${role.id}`}
                  className="px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-[#8B5CF6] to-[#A855F7] text-xs font-bold text-white shadow-[0_0_12px_rgba(168,85,247,0.3)] hover:shadow-[0_0_18px_rgba(168,85,247,0.6)] flex items-center gap-1.5 transition-all"
                >
                  <Milestone className="w-3.5 h-3.5" />
                  <span>Build Roadmap</span>
                </Link>
              </div>
            </GlowCard>
          );
        })}
      </div>
    </div>
  );
}
