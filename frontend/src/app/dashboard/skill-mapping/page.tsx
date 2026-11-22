"use client";

import React, { useState, useEffect } from "react";
import { 
  Network, 
  Search, 
  BookOpen, 
  Layers, 
  ArrowRight, 
  Briefcase, 
  Code2, 
  ChevronDown, 
  ChevronUp, 
  Sparkles, 
  Building2,
  Table as TableIcon,
  LayoutGrid
} from "lucide-react";
import { GlowCard } from "@/components/GlowCard";
import { api } from "@/lib/api";
import { SubjectSkillMapping } from "@/lib/types";

export default function SkillMappingPage() {
  const [mappings, setMappings] = useState<SubjectSkillMapping[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [selectedSubject, setSelectedSubject] = useState("all");
  const [selectedRole, setSelectedRole] = useState("all");
  const [viewMode, setViewMode] = useState<"cards" | "table">("cards");
  const [expandedId, setExpandedId] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await api.getSkillMappings();
        setMappings(data);
      } catch (e) {
        console.error("Error loading mappings:", e);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const subjects = Array.from(new Set(mappings.map((m) => m.subject_name)));
  const roles = Array.from(new Set(mappings.map((m) => m.career_role_title)));

  const filtered = mappings.filter((m) => {
    const matchesSearch =
      m.subject_name.toLowerCase().includes(search.toLowerCase()) ||
      m.topic_name.toLowerCase().includes(search.toLowerCase()) ||
      m.competency_name.toLowerCase().includes(search.toLowerCase()) ||
      m.skill_name.toLowerCase().includes(search.toLowerCase()) ||
      m.career_role_title.toLowerCase().includes(search.toLowerCase()) ||
      (m.industry_application && m.industry_application.toLowerCase().includes(search.toLowerCase())) ||
      (m.practical_project_example && m.practical_project_example.toLowerCase().includes(search.toLowerCase()));

    const matchesSubject = selectedSubject === "all" || m.subject_name === selectedSubject;
    const matchesRole = selectedRole === "all" || m.career_role_title === selectedRole;

    return matchesSearch && matchesSubject && matchesRole;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Network className="w-5 h-5 text-[#C084FC]" /> Academic-to-Industry Skill Mapping
          </h1>
          <p className="text-xs text-[#A1A1AA] mt-1 max-w-2xl">
            Bridge theoretical classroom coursework with real-world engineering. Discover how academic subjects, university topics, and core competencies translate into industry production architectures and career roles.
          </p>
        </div>

        {/* View Mode Toggle */}
        <div className="flex items-center gap-1 p-1 bg-[#100B18] border border-[#30203F] rounded-lg self-start">
          <button
            onClick={() => setViewMode("cards")}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
              viewMode === "cards"
                ? "bg-[#8B5CF6] text-white shadow-sm"
                : "text-[#A1A1AA] hover:text-white"
            }`}
          >
            <LayoutGrid className="w-3.5 h-3.5" />
            Application Cards
          </button>
          <button
            onClick={() => setViewMode("table")}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
              viewMode === "table"
                ? "bg-[#8B5CF6] text-white shadow-sm"
                : "text-[#A1A1AA] hover:text-white"
            }`}
          >
            <TableIcon className="w-3.5 h-3.5" />
            Taxonomy Table
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
        <div className="sm:col-span-2 relative">
          <Search className="w-4 h-4 text-[#A1A1AA] absolute left-3.5 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search academic topics, industry applications, or tools..."
            className="w-full pl-10 pr-4 py-2.5 rounded-lg bg-[#191225] border border-[#30203F] text-xs text-white placeholder-[#A1A1AA]/50 focus:outline-none focus:border-[#A855F7]"
          />
        </div>

        <div>
          <select
            value={selectedSubject}
            onChange={(e) => setSelectedSubject(e.target.value)}
            className="w-full px-3 py-2.5 rounded-lg bg-[#191225] border border-[#30203F] text-xs text-white focus:outline-none focus:border-[#A855F7]"
          >
            <option value="all">All Academic Subjects</option>
            {subjects.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>

        <div>
          <select
            value={selectedRole}
            onChange={(e) => setSelectedRole(e.target.value)}
            className="w-full px-3 py-2.5 rounded-lg bg-[#191225] border border-[#30203F] text-xs text-white focus:outline-none focus:border-[#A855F7]"
          >
            <option value="all">All Target Roles</option>
            {roles.map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Total Filtered Count */}
      <div className="flex items-center justify-between text-xs text-[#A1A1AA]">
        <span>Showing <strong className="text-white">{filtered.length}</strong> academic-to-industry mappings</span>
        {search || selectedSubject !== "all" || selectedRole !== "all" ? (
          <button
            onClick={() => {
              setSearch("");
              setSelectedSubject("all");
              setSelectedRole("all");
            }}
            className="text-[#C084FC] hover:underline"
          >
            Clear filters
          </button>
        ) : null}
      </div>

      {/* Content Rendering based on ViewMode */}
      {viewMode === "cards" ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filtered.map((m) => {
            const isExpanded = expandedId === m.id;
            return (
              <GlowCard key={m.id} className="p-4 flex flex-col justify-between">
                <div>
                  {/* Academic Context Header */}
                  <div className="flex items-start justify-between gap-2 border-b border-[#30203F]/60 pb-3 mb-3">
                    <div>
                      <div className="flex items-center gap-1.5 text-[11px] text-[#A1A1AA]">
                        <BookOpen className="w-3.5 h-3.5 text-[#A855F7]" />
                        <span className="font-semibold text-[#D8B4FE]">{m.subject_name}</span>
                        <span>•</span>
                        <span>Topic: <strong className="text-white">{m.topic_name}</strong></span>
                      </div>
                      <h3 className="text-sm font-bold text-white mt-1">{m.competency_name}</h3>
                    </div>

                    <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-[#8B5CF6]/20 border border-[#A855F7]/30 text-[#C084FC] whitespace-nowrap">
                      {m.skill_name}
                    </span>
                  </div>

                  {/* Industry Target Role */}
                  <div className="flex items-center gap-2 mb-3 px-2.5 py-1.5 rounded-md bg-[#100B18] border border-[#30203F]/40 text-xs text-[#A1A1AA]">
                    <Building2 className="w-3.5 h-3.5 text-[#C084FC]" />
                    <span>Industry Target:</span>
                    <strong className="text-white flex items-center gap-1">
                      {m.career_role_title}
                    </strong>
                  </div>

                  {/* Real World Industry Application */}
                  <div className="space-y-2 text-xs">
                    <div className="bg-[#191225] border border-[#30203F] rounded-lg p-3">
                      <div className="flex items-center gap-1.5 text-[#C084FC] font-semibold text-[11px] mb-1">
                        <Briefcase className="w-3.5 h-3.5" />
                        <span>Real-World Production Application</span>
                      </div>
                      <p className="text-[#D4D4D8] leading-relaxed text-[11px]">
                        {m.industry_application || "Applied in distributed software engineering workflows to ensure high throughput, data consistency, and scalable cloud performance."}
                      </p>
                    </div>

                    {/* Practical Project Example */}
                    {m.practical_project_example && (
                      <div className="bg-[#100B18] border border-[#8B5CF6]/20 rounded-lg p-3">
                        <div className="flex items-center gap-1.5 text-[#A855F7] font-semibold text-[11px] mb-1">
                          <Code2 className="w-3.5 h-3.5" />
                          <span>Industry Project Application</span>
                        </div>
                        <p className="text-[#A1A1AA] leading-relaxed text-[11px]">
                          {m.practical_project_example}
                        </p>
                      </div>
                    )}
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-[#30203F]/40 flex items-center justify-between text-[11px] text-[#A1A1AA]">
                  <span className="flex items-center gap-1 text-[#34D399]">
                    <Sparkles className="w-3 h-3" /> Industry Relevant
                  </span>
                  <span className="text-[#A1A1AA]/70">Curriculum-to-Production</span>
                </div>
              </GlowCard>
            );
          })}
        </div>
      ) : (
        /* Taxonomy Table View */
        <GlowCard className="overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#100B18] text-[#A1A1AA] uppercase text-[10px] font-semibold border-b border-[#30203F]">
                <tr>
                  <th className="px-4 py-3.5">Academic Subject</th>
                  <th className="px-4 py-3.5">Topic</th>
                  <th className="px-4 py-3.5">Industry Competency</th>
                  <th className="px-4 py-3.5">Verified Skill</th>
                  <th className="px-4 py-3.5">Target Career Role</th>
                  <th className="px-4 py-3.5">Production Application</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#30203F]/60">
                {filtered.map((m) => (
                  <tr key={m.id} className="hover:bg-[#100B18]/40 transition-colors">
                    <td className="px-4 py-3 font-semibold text-white">{m.subject_name}</td>
                    <td className="px-4 py-3 text-[#D8B4FE] font-medium">{m.topic_name}</td>
                    <td className="px-4 py-3 text-[#A1A1AA]">{m.competency_name}</td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-0.5 rounded bg-[#8B5CF6]/20 border border-[#A855F7]/30 text-[#C084FC] font-semibold">
                        {m.skill_name}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-white font-medium">
                      <span className="flex items-center gap-1.5">
                        <ArrowRight className="w-3 h-3 text-[#A855F7]" />
                        {m.career_role_title}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-[11px] text-[#A1A1AA] max-w-xs truncate" title={m.industry_application}>
                      {m.industry_application || "Production engineering workflows"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </GlowCard>
      )}

      {filtered.length === 0 && (
        <div className="text-center py-12 text-xs text-[#A1A1AA]">
          No skill mappings found matching your search or filters.
        </div>
      )}
    </div>
  );
}
