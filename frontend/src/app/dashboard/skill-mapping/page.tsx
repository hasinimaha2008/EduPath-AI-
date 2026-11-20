"use client";

import React, { useState, useEffect } from "react";
import { Network, Search, Filter, BookOpen, Layers, ArrowRight } from "lucide-react";
import { GlowCard } from "@/components/GlowCard";
import { api } from "@/lib/api";
import { SubjectSkillMapping } from "@/lib/types";

export default function SkillMappingPage() {
  const [mappings, setMappings] = useState<SubjectSkillMapping[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [selectedSubject, setSelectedSubject] = useState("all");

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

  const filtered = mappings.filter((m) => {
    const matchesSearch =
      m.subject_name.toLowerCase().includes(search.toLowerCase()) ||
      m.topic_name.toLowerCase().includes(search.toLowerCase()) ||
      m.competency_name.toLowerCase().includes(search.toLowerCase()) ||
      m.skill_name.toLowerCase().includes(search.toLowerCase()) ||
      m.career_role_title.toLowerCase().includes(search.toLowerCase());

    const matchesSubject = selectedSubject === "all" || m.subject_name === selectedSubject;

    return matchesSearch && matchesSubject;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <Network className="w-5 h-5 text-[#C084FC]" /> Academic-to-Industry Skill Mapping
        </h1>
        <p className="text-xs text-[#A1A1AA] mt-0.5">
          Structured pedagogical taxonomy connecting academic subjects, specific topics, industry competencies, skills, and target career roles.
        </p>
      </div>

      {/* Filter and Search Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="sm:col-span-2 relative">
          <Search className="w-4 h-4 text-[#A1A1AA] absolute left-3.5 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search topic, competency, skill, or role (e.g. Normalization, SQL, Python)..."
            className="w-full pl-10 pr-4 py-2.5 rounded-lg bg-[#191225] border border-[#30203F] text-xs text-white placeholder-[#A1A1AA]/50 focus:outline-none focus:border-[#A855F7]"
          />
        </div>

        <div>
          <select
            value={selectedSubject}
            onChange={(e) => setSelectedSubject(e.target.value)}
            className="w-full px-3 py-2.5 rounded-lg bg-[#191225] border border-[#30203F] text-xs text-white focus:outline-none focus:border-[#A855F7]"
          >
            <option value="all">All Subjects ({mappings.length} mappings)</option>
            {subjects.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Mapping Taxonomy Table */}
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
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </GlowCard>
    </div>
  );
}
