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
  ChevronUp,
  UserCheck,
  Sparkles,
  Plus,
  Trash2,
  ExternalLink,
  BookOpen,
  Award,
  ShieldCheck,
  Filter
} from "lucide-react";
import { GlowCard } from "@/components/GlowCard";
import { api } from "@/lib/api";
import {
  CareerRecommendation,
  CareerComparisonResponse,
  CareerProjectItem,
  CareerPathwayItem,
  StudentCareerProfile,
  ProjectExperienceItem
} from "@/lib/types";

const ALL_DOMAINS = [
  "All Domains",
  "Software Development",
  "Artificial Intelligence",
  "Machine Learning",
  "Data Science",
  "Cybersecurity",
  "Cloud Computing",
  "Web Development",
  "Data Systems & Architecture"
];

export default function CareerIntelligencePage() {
  const [recommendations, setRecommendations] = useState<CareerRecommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"readiness" | "profile" | "compare" | "projects" | "pathways">("readiness");
  const [selectedDomain, setSelectedDomain] = useState<string>("All Domains");

  // Student Profile State
  const [studentProfile, setStudentProfile] = useState<StudentCareerProfile | null>(null);
  const [savingProfile, setSavingProfile] = useState(false);
  const [profileSavedNotice, setProfileSavedNotice] = useState(false);

  // Profile Form State
  const [formInterests, setFormInterests] = useState<string[]>([]);
  const [newInterestInput, setNewInterestInput] = useState("");
  const [formDomains, setFormDomains] = useState<string[]>([]);
  const [formGoal, setFormGoal] = useState("");
  const [formSkills, setFormSkills] = useState<string[]>([]);
  const [newSkillInput, setNewSkillInput] = useState("");
  const [formProjects, setFormProjects] = useState<ProjectExperienceItem[]>([]);
  const [newProjTitle, setNewProjTitle] = useState("");
  const [newProjDesc, setNewProjDesc] = useState("");
  const [newProjTech, setNewProjTech] = useState("");

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

  // Target career
  const [targetCareerId, setTargetCareerId] = useState<string>("");

  useEffect(() => {
    loadAllData();
  }, []);

  async function loadAllData() {
    try {
      setLoading(true);
      const [recs, profile] = await Promise.all([
        api.getCareerRecommendations(),
        api.getStudentCareerProfile().catch(() => null)
      ]);
      setRecommendations(recs);

      if (profile) {
        setStudentProfile(profile);
        setFormInterests(profile.interests || []);
        setFormDomains(profile.preferred_domains || []);
        setFormGoal(profile.career_goals || "");
        setFormSkills(profile.self_reported_skills || []);
        setFormProjects(profile.projects_and_experience || []);
        if (profile.target_career_id) {
          setTargetCareerId(profile.target_career_id);
        }
      }

      if (recs.length >= 2) {
        setSelectedRoleIds([recs[0].career_role.id, recs[1].career_role.id]);
        setSelectedProjectId(recs[0].career_role.id);
      }
    } catch (e) {
      console.error("Error loading career data:", e);
    } finally {
      setLoading(false);
    }
  }

  const handleSaveProfile = async () => {
    try {
      setSavingProfile(true);
      const updated = await api.updateStudentCareerProfile({
        interests: formInterests,
        preferred_domains: formDomains,
        career_goals: formGoal,
        self_reported_skills: formSkills,
        projects_and_experience: formProjects,
        target_career_id: targetCareerId || undefined
      });
      setStudentProfile(updated);
      setProfileSavedNotice(true);
      setTimeout(() => setProfileSavedNotice(false), 4000);

      // Refresh career recommendations with new profile
      const newRecs = await api.getCareerRecommendations();
      setRecommendations(newRecs);
    } catch (e) {
      console.error("Error updating profile:", e);
    } finally {
      setSavingProfile(false);
    }
  };

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
      if (selectedRoleIds.length <= 2) return;
      nextIds = selectedRoleIds.filter(id => id !== roleId);
    } else {
      if (selectedRoleIds.length >= 4) return;
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
      await api.updateStudentCareerProfile({ target_career_id: roleId });
      setTargetCareerId(roleId);
      const newRecs = await api.getCareerRecommendations();
      setRecommendations(newRecs);
    } catch (e) {
      console.error("Failed to set target career:", e);
    }
  };

  const handleAddInterest = () => {
    if (!newInterestInput.trim()) return;
    if (!formInterests.includes(newInterestInput.trim())) {
      setFormInterests([...formInterests, newInterestInput.trim()]);
    }
    setNewInterestInput("");
  };

  const handleRemoveInterest = (item: string) => {
    setFormInterests(formInterests.filter(i => i !== item));
  };

  const handleToggleDomain = (dom: string) => {
    if (formDomains.includes(dom)) {
      setFormDomains(formDomains.filter(d => d !== dom));
    } else {
      setFormDomains([...formDomains, dom]);
    }
  };

  const handleAddSkill = () => {
    if (!newSkillInput.trim()) return;
    if (!formSkills.includes(newSkillInput.trim())) {
      setFormSkills([...formSkills, newSkillInput.trim()]);
    }
    setNewSkillInput("");
  };

  const handleRemoveSkill = (skill: string) => {
    setFormSkills(formSkills.filter(s => s !== skill));
  };

  const handleAddProject = () => {
    if (!newProjTitle.trim() || !newProjDesc.trim()) return;
    const techs = newProjTech.split(",").map(t => t.trim()).filter(Boolean);
    const newEntry: ProjectExperienceItem = {
      title: newProjTitle.trim(),
      description: newProjDesc.trim(),
      technologies: techs
    };
    setFormProjects([...formProjects, newEntry]);
    setNewProjTitle("");
    setNewProjDesc("");
    setNewProjTech("");
  };

  const handleRemoveProject = (index: number) => {
    setFormProjects(formProjects.filter((_, i) => i !== index));
  };

  // Filter recommendations by selected domain
  const filteredRecommendations = recommendations.filter(rec => {
    if (selectedDomain === "All Domains") return true;
    return (rec.domain || "").toLowerCase().includes(selectedDomain.toLowerCase());
  });

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#30203F] pb-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-white flex items-center gap-2">
            <Compass className="w-6 h-6 text-[#C084FC]" />
            Career Intelligence & Practical Guidance
          </h1>
          <p className="text-xs text-[#A1A1AA] mt-1">
            Dynamic career matching combining verified academic quiz performance, self-reported skills, personal goals, and practical projects.
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="flex flex-wrap items-center gap-1.5 p-1 rounded-xl bg-[#160F23] border border-[#30203F]">
          <button
            onClick={() => setActiveTab("readiness")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
              activeTab === "readiness"
                ? "bg-[#8B5CF6]/30 text-white border border-[#A855F7]/40 shadow-[0_0_10px_rgba(168,85,247,0.3)]"
                : "text-[#A1A1AA] hover:text-white"
            }`}
          >
            Recommendations ({recommendations.length})
          </button>

          <button
            onClick={() => setActiveTab("profile")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ${
              activeTab === "profile"
                ? "bg-[#8B5CF6]/30 text-white border border-[#A855F7]/40 shadow-[0_0_10px_rgba(168,85,247,0.3)]"
                : "text-[#A1A1AA] hover:text-white"
            }`}
          >
            <UserCheck className="w-3.5 h-3.5 text-[#C084FC]" />
            <span>Student Profile</span>
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

      {/* Advisory Banner */}
      <div className="p-4 rounded-xl bg-purple-950/30 border border-purple-500/30 flex items-start gap-3 text-xs text-[#D8B4FE]">
        <Info className="w-5 h-5 text-[#C084FC] shrink-0 mt-0.5" />
        <div>
          <strong className="text-white block mb-0.5">Academic & Job-Market Advisory Notice</strong>
          Recommendations clearly distinguish <strong>verified academic qualifications</strong> (demonstrated via curriculum quizzes) from <strong>estimated recommendations</strong> and self-reported skills. Does not promise or guarantee employment.
        </div>
      </div>

      {/* TAB 1: Career Readiness & Recommendations */}
      {activeTab === "readiness" && (
        <div className="space-y-6">
          {/* Domain Filter Pills */}
          <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-thin">
            <span className="text-xs text-[#A1A1AA] flex items-center gap-1 font-semibold shrink-0 mr-1">
              <Filter className="w-3.5 h-3.5 text-[#C084FC]" /> Filter Domain:
            </span>
            {ALL_DOMAINS.map((domain) => (
              <button
                key={domain}
                onClick={() => setSelectedDomain(domain)}
                className={`px-3 py-1 rounded-full text-xs font-medium whitespace-nowrap transition-all ${
                  selectedDomain === domain
                    ? "bg-[#8B5CF6] text-white shadow-md shadow-[#8B5CF6]/30 border border-[#A855F7]"
                    : "bg-[#160F23] border border-[#30203F] text-[#A1A1AA] hover:text-white"
                }`}
              >
                {domain}
              </button>
            ))}
          </div>

          {/* Career Recommendations Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {filteredRecommendations.map((rec) => {
              const role = rec.career_role;
              const isTarget = targetCareerId === role.id;
              const domainName = rec.domain || "Technology";

              return (
                <GlowCard key={rec.id} glow={rec.match_score >= 50} className="p-6 flex flex-col justify-between">
                  <div>
                    {/* Header Badges */}
                    <div className="flex items-center justify-between gap-2 mb-3">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-[#8B5CF6]/20 text-[#C084FC] border border-[#A855F7]/30">
                          {domainName}
                        </span>
                        <span className="text-[10px] font-medium px-2 py-0.5 rounded bg-[#100B18] text-[#A1A1AA] border border-[#30203F]">
                          {role.industry_demand} Demand
                        </span>
                        {isTarget && (
                          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 flex items-center gap-1">
                            <Check className="w-3 h-3" /> Target Goal
                          </span>
                        )}
                      </div>
                      <div className="text-right shrink-0">
                        <span className="text-xl font-extrabold text-white">
                          {rec.match_score}%
                        </span>
                        <span className="text-[10px] text-[#A1A1AA] block">Readiness</span>
                      </div>
                    </div>

                    <h2 className="text-lg font-bold text-white mb-1.5">{role.title}</h2>
                    <p className="text-xs text-[#A1A1AA] leading-relaxed mb-4">{role.description}</p>

                    {/* Readiness Distinction: Demonstrated vs Estimated */}
                    <div className="p-3 rounded-xl bg-[#100B18] border border-[#30203F] space-y-2 mb-4">
                      <div className="flex justify-between text-xs">
                        <span className="text-[#A1A1AA] flex items-center gap-1">
                          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> Verified Academic Match:
                        </span>
                        <span className="font-bold text-emerald-400">{rec.demonstrated_match_score ?? 0}%</span>
                      </div>
                      <div className="w-full bg-[#191225] h-1.5 rounded-full overflow-hidden">
                        <div
                          className="bg-emerald-400 h-full rounded-full"
                          style={{ width: `${Math.min(rec.demonstrated_match_score ?? 0, 100)}%` }}
                        />
                      </div>

                      <div className="flex justify-between text-[11px] pt-1 border-t border-[#20152B]">
                        <span className="text-[#71717A]">Self-Reported/Curriculum Match:</span>
                        <span className="text-purple-300 font-medium">{rec.self_reported_match_score ?? 0}%</span>
                      </div>
                    </div>

                    {/* Salary & Metrics */}
                    <div className="flex flex-wrap items-center gap-3 text-xs text-[#D8B4FE] mb-4 p-2.5 rounded-lg bg-[#140D22] border border-[#30203F]">
                      <div className="flex items-center gap-1">
                        <DollarSign className="w-3.5 h-3.5 text-emerald-400" />
                        <span>{role.salary_range || "Competitive Range"}</span>
                      </div>
                      <div>•</div>
                      <div className="text-emerald-300 font-medium">{rec.matching_skills.length} Competencies</div>
                      <div>•</div>
                      <div className="text-amber-400 font-medium">{rec.missing_skills_count} Skill Gaps</div>
                    </div>

                    {/* Explainable Rationale */}
                    <div className="p-3 rounded-lg bg-[#191225] border border-[#30203F] text-xs text-gray-300 mb-4">
                      <div className="flex items-center gap-1.5 text-[#C084FC] font-bold text-[11px] mb-1">
                        <Sparkles className="w-3.5 h-3.5" /> Explainable Match Rationale:
                      </div>
                      <p className="leading-relaxed text-[11px] text-[#D8B4FE]">{rec.rationale}</p>
                    </div>

                    {/* Matching Skills */}
                    {rec.matching_skills.length > 0 && (
                      <div className="mb-4">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-[#A1A1AA] block mb-1.5">
                          Demonstrated & Matching Skills
                        </span>
                        <div className="flex flex-wrap gap-1.5">
                          {rec.matching_skills.map((s, idx) => (
                            <span
                              key={idx}
                              className={`text-[10px] px-2 py-0.5 rounded border ${
                                s.includes("(Verified)")
                                  ? "bg-emerald-500/10 text-emerald-300 border-emerald-500/30"
                                  : "bg-blue-500/10 text-blue-300 border-blue-500/30"
                              }`}
                            >
                              {s}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="pt-4 border-t border-[#30203F] flex flex-wrap items-center justify-between gap-2">
                    <button
                      onClick={() => handleSetTargetCareer(role.id)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all ${
                        isTarget
                          ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                          : "bg-[#100B18] border border-[#30203F] text-[#A1A1AA] hover:text-white hover:border-[#8B5CF6]"
                      }`}
                    >
                      <Target className="w-3.5 h-3.5" />
                      <span>{isTarget ? "Target Career" : "Set Target"}</span>
                    </button>

                    <div className="flex items-center gap-2">
                      <Link
                        href={`/dashboard/skill-gaps?role_id=${role.id}`}
                        className="px-3 py-1.5 rounded-lg bg-[#100B18] border border-[#30203F] hover:border-purple-500/50 text-xs font-bold text-white flex items-center gap-1.5 transition-all"
                      >
                        <Layers className="w-3.5 h-3.5 text-[#C084FC]" />
                        <span>Skill Gaps</span>
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
        </div>
      )}

      {/* TAB 2: Student Career Profile Manager */}
      {activeTab === "profile" && (
        <div className="space-y-6">
          <GlowCard className="p-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#30203F] pb-4 mb-6">
              <div>
                <h2 className="text-base font-bold text-white flex items-center gap-2">
                  <UserCheck className="w-5 h-5 text-[#C084FC]" /> Student Career Profile
                </h2>
                <p className="text-xs text-[#A1A1AA] mt-0.5">
                  Update your technical interests, career aspirations, and self-reported skills. We never fabricate qualifications.
                </p>
              </div>

              <button
                onClick={handleSaveProfile}
                disabled={savingProfile}
                className="px-4 py-2 rounded-lg bg-gradient-to-r from-[#8B5CF6] to-[#A855F7] text-white text-xs font-bold hover:opacity-95 shadow-md flex items-center gap-1.5 transition-all self-start sm:self-auto disabled:opacity-50"
              >
                {savingProfile ? "Saving & Recalculating..." : "Save Profile & Update Matches"}
              </button>
            </div>

            {profileSavedNotice && (
              <div className="p-3 mb-6 rounded-lg bg-emerald-500/20 border border-emerald-500/30 text-emerald-300 text-xs font-medium flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                Profile updated successfully! Career recommendation match scores and skill gaps re-evaluated.
              </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Preferred Domains */}
              <div className="space-y-3">
                <label className="text-xs font-bold text-white uppercase tracking-wider block">
                  Preferred Technology Domains
                </label>
                <div className="flex flex-wrap gap-2">
                  {ALL_DOMAINS.filter(d => d !== "All Domains").map((dom) => {
                    const isSelected = formDomains.includes(dom);
                    return (
                      <button
                        key={dom}
                        type="button"
                        onClick={() => handleToggleDomain(dom)}
                        className={`px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
                          isSelected
                            ? "bg-[#8B5CF6]/30 text-white border-[#A855F7] shadow-sm"
                            : "bg-[#100B18] border-[#30203F] text-[#A1A1AA] hover:text-white"
                        }`}
                      >
                        {isSelected ? `✓ ${dom}` : `+ ${dom}`}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Career Goal */}
              <div className="space-y-3">
                <label className="text-xs font-bold text-white uppercase tracking-wider block">
                  Career Goal & Target Ambition
                </label>
                <input
                  type="text"
                  value={formGoal}
                  onChange={(e) => setFormGoal(e.target.value)}
                  placeholder="e.g. Target Senior Cloud Architect role at high-scale tech firm"
                  className="w-full px-3.5 py-2.5 rounded-lg bg-[#100B18] border border-[#30203F] text-xs text-white placeholder-[#71717A] focus:outline-none focus:border-[#A855F7]"
                />
              </div>

              {/* Technical Interests */}
              <div className="space-y-3">
                <label className="text-xs font-bold text-white uppercase tracking-wider block">
                  Technical Interests & Topics
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={newInterestInput}
                    onChange={(e) => setNewInterestInput(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), handleAddInterest())}
                    placeholder="e.g. Distributed Systems, Kubernetes, RAG"
                    className="flex-1 px-3.5 py-2 rounded-lg bg-[#100B18] border border-[#30203F] text-xs text-white placeholder-[#71717A] focus:outline-none focus:border-[#A855F7]"
                  />
                  <button
                    type="button"
                    onClick={handleAddInterest}
                    className="px-3 py-2 rounded-lg bg-[#191225] border border-[#30203F] text-xs font-semibold text-white hover:border-[#A855F7]"
                  >
                    Add
                  </button>
                </div>
                <div className="flex flex-wrap gap-1.5 min-h-[32px]">
                  {formInterests.map((interest) => (
                    <span
                      key={interest}
                      className="px-2.5 py-1 rounded bg-[#8B5CF6]/15 border border-[#8B5CF6]/30 text-xs text-[#C084FC] flex items-center gap-1.5"
                    >
                      {interest}
                      <button
                        type="button"
                        onClick={() => handleRemoveInterest(interest)}
                        className="hover:text-red-400"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>

              {/* Self-Reported Skills */}
              <div className="space-y-3">
                <label className="text-xs font-bold text-white uppercase tracking-wider block">
                  Self-Reported Skills (Estimated)
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={newSkillInput}
                    onChange={(e) => setNewSkillInput(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), handleAddSkill())}
                    placeholder="e.g. Python Programming, SQL Querying, React"
                    className="flex-1 px-3.5 py-2 rounded-lg bg-[#100B18] border border-[#30203F] text-xs text-white placeholder-[#71717A] focus:outline-none focus:border-[#A855F7]"
                  />
                  <button
                    type="button"
                    onClick={handleAddSkill}
                    className="px-3 py-2 rounded-lg bg-[#191225] border border-[#30203F] text-xs font-semibold text-white hover:border-[#A855F7]"
                  >
                    Add Skill
                  </button>
                </div>
                <div className="flex flex-wrap gap-1.5 min-h-[32px]">
                  {formSkills.map((skill) => (
                    <span
                      key={skill}
                      className="px-2.5 py-1 rounded bg-blue-500/15 border border-blue-500/30 text-xs text-blue-300 flex items-center gap-1.5"
                    >
                      {skill}
                      <button
                        type="button"
                        onClick={() => handleRemoveSkill(skill)}
                        className="hover:text-red-400"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Practical Projects & Portfolio Experience */}
            <div className="mt-8 pt-6 border-t border-[#30203F] space-y-4">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <FolderGit2 className="w-4 h-4 text-[#C084FC]" /> Personal Projects & Practical Experience
              </h3>

              {/* Add Project Form */}
              <div className="p-4 rounded-xl bg-[#100B18] border border-[#30203F] space-y-3">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <input
                    type="text"
                    value={newProjTitle}
                    onChange={(e) => setNewProjTitle(e.target.value)}
                    placeholder="Project Title (e.g. Microservices Order API)"
                    className="px-3 py-2 rounded-lg bg-[#160F23] border border-[#30203F] text-xs text-white placeholder-[#71717A] focus:outline-none focus:border-[#A855F7]"
                  />
                  <input
                    type="text"
                    value={newProjTech}
                    onChange={(e) => setNewProjTech(e.target.value)}
                    placeholder="Technologies (comma-separated: FastAPI, Docker, PostgreSQL)"
                    className="px-3 py-2 rounded-lg bg-[#160F23] border border-[#30203F] text-xs text-white placeholder-[#71717A] focus:outline-none focus:border-[#A855F7]"
                  />
                </div>
                <textarea
                  value={newProjDesc}
                  onChange={(e) => setNewProjDesc(e.target.value)}
                  placeholder="Describe project implementation, architecture, and personal contributions..."
                  rows={2}
                  className="w-full px-3 py-2 rounded-lg bg-[#160F23] border border-[#30203F] text-xs text-white placeholder-[#71717A] focus:outline-none focus:border-[#A855F7]"
                />
                <button
                  type="button"
                  onClick={handleAddProject}
                  className="px-3 py-1.5 rounded-lg bg-[#8B5CF6]/30 border border-[#A855F7]/40 text-xs font-bold text-white hover:bg-[#8B5CF6]/50 flex items-center gap-1.5"
                >
                  <Plus className="w-3.5 h-3.5" /> Add Project Entry
                </button>
              </div>

              {/* Existing Projects List */}
              <div className="space-y-2 mt-3">
                {formProjects.map((p, idx) => (
                  <div key={idx} className="p-3 rounded-lg bg-[#140D22] border border-[#30203F] flex items-start justify-between gap-4">
                    <div>
                      <div className="font-bold text-xs text-white">{p.title}</div>
                      <p className="text-[11px] text-[#A1A1AA] mt-1 leading-relaxed">{p.description}</p>
                      {p.technologies && p.technologies.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-2">
                          {p.technologies.map((t, tIdx) => (
                            <span key={tIdx} className="px-2 py-0.5 rounded bg-[#100B18] border border-[#30203F] text-[10px] text-[#D8B4FE]">
                              {t}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                    <button
                      type="button"
                      onClick={() => handleRemoveProject(idx)}
                      className="text-red-400 hover:text-red-300 p-1"
                      title="Remove Project"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))}
              </div>
            </div>

            {/* Verified Learning Progress (Read-Only) */}
            {studentProfile && (
              <div className="mt-8 pt-6 border-t border-[#30203F]">
                <h3 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
                  <Award className="w-4 h-4 text-emerald-400" /> Verified Academic Learning Progress
                </h3>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div className="p-3 rounded-lg bg-[#100B18] border border-[#30203F]">
                    <div className="text-[10px] text-[#A1A1AA]">Quizzes Completed</div>
                    <div className="text-lg font-bold text-white">{studentProfile.learning_progress.total_quizzes_attempted}</div>
                  </div>
                  <div className="p-3 rounded-lg bg-[#100B18] border border-[#30203F]">
                    <div className="text-[10px] text-[#A1A1AA]">Average Score</div>
                    <div className="text-lg font-bold text-emerald-400">{studentProfile.learning_progress.average_quiz_score}%</div>
                  </div>
                  <div className="p-3 rounded-lg bg-[#100B18] border border-[#30203F]">
                    <div className="text-[10px] text-[#A1A1AA]">Study Time</div>
                    <div className="text-lg font-bold text-white">{studentProfile.learning_progress.study_hours} hrs</div>
                  </div>
                  <div className="p-3 rounded-lg bg-[#100B18] border border-[#30203F]">
                    <div className="text-[10px] text-[#A1A1AA]">Mastered Topics</div>
                    <div className="text-lg font-bold text-[#C084FC]">{studentProfile.learning_progress.mastered_topics_count}</div>
                  </div>
                </div>
              </div>
            )}
          </GlowCard>
        </div>
      )}

      {/* TAB 3: Multi-Role Comparison */}
      {activeTab === "compare" && (
        <div className="p-6 rounded-2xl bg-[#160F23] border border-[#30203F] space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-[#30203F]">
            <div>
              <h2 className="text-base font-bold text-white">Side-by-Side Career Role Comparison</h2>
              <p className="text-xs text-[#A1A1AA]">Select 2 to 4 roles to compare demonstrated readiness, skill overlap, and market metrics.</p>
            </div>

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
            <div className="py-12 text-center text-xs text-[#A1A1AA]">Comparing role architectures...</div>
          ) : comparisonData ? (
            <div className="space-y-6">
              {comparisonData.shared_skills && comparisonData.shared_skills.length > 0 && (
                <div className="p-4 rounded-xl bg-[#100B18] border border-[#30203F]">
                  <span className="text-xs font-bold text-emerald-400 block mb-2">
                    Universal Shared Competencies ({comparisonData.shared_skills.length})
                  </span>
                  <div className="flex flex-wrap gap-2">
                    {comparisonData.shared_skills.map((s, idx) => (
                      <span key={idx} className="px-2.5 py-1 rounded bg-emerald-500/10 border border-emerald-500/30 text-xs text-emerald-300">
                        ✓ {s}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div className={`grid grid-cols-1 md:grid-cols-${comparisonData.compared_roles.length} gap-4`}>
                {comparisonData.compared_roles.map((cr) => (
                  <div key={cr.id} className="p-5 rounded-xl bg-[#100B18] border border-[#30203F] space-y-4">
                    <div className="border-b border-[#30203F] pb-3">
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-sm font-bold text-white">{cr.title}</span>
                        <span className="text-base font-extrabold text-[#C084FC]">{cr.readiness_score}%</span>
                      </div>
                      <div className="text-[11px] text-[#A1A1AA]">{cr.salary_range}</div>
                    </div>

                    <div>
                      <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-400 block mb-1.5">
                        Demonstrated ({cr.demonstrated_skills.length})
                      </span>
                      <div className="space-y-1">
                        {cr.demonstrated_skills.map((s, i) => (
                          <div key={i} className="text-xs text-white flex justify-between">
                            <span>{s.skill}</span>
                            <span className="text-emerald-400 font-bold">{s.proficiency}%</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div>
                      <span className="text-[10px] font-bold uppercase tracking-wider text-amber-400 block mb-1.5">
                        Missing Skills ({cr.missing_skills.length})
                      </span>
                      <div className="space-y-1">
                        {cr.missing_skills.map((s, i) => (
                          <div key={i} className="text-xs text-[#A1A1AA] flex justify-between">
                            <span>{s.skill}</span>
                            <span className="text-amber-400 font-medium">Target: {s.target}%</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <Link
                      href={`/dashboard/roadmaps?role_id=${cr.id}`}
                      className="w-full py-2 rounded-lg bg-gradient-to-r from-[#8B5CF6] to-[#A855F7] text-white text-xs font-bold flex items-center justify-center gap-1 mt-4"
                    >
                      View Roadmap <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>
                ))}
              </div>
            </div>
          ) : null}
        </div>
      )}

      {/* TAB 4: Practical Projects */}
      {activeTab === "projects" && (
        <div className="space-y-6">
          <div className="flex flex-wrap items-center gap-2 pb-2">
            {recommendations.map((r) => (
              <button
                key={r.career_role.id}
                onClick={() => handleSelectProjectRole(r.career_role.id)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
                  selectedProjectId === r.career_role.id
                    ? "bg-[#8B5CF6] text-white border-[#A855F7]"
                    : "bg-[#191225] border-[#30203F] text-[#A1A1AA] hover:text-white"
                }`}
              >
                {r.career_role.title}
              </button>
            ))}
          </div>

          {loadingProjects ? (
            <div className="py-12 text-center text-xs text-[#A1A1AA]">Loading practical projects...</div>
          ) : projects.length > 0 ? (
            <div className="space-y-4">
              {projects.map((proj) => {
                const isExpanded = expandedProject === proj.id;
                return (
                  <GlowCard key={proj.id} className="p-5">
                    <div
                      className="cursor-pointer flex items-center justify-between"
                      onClick={() => setExpandedProject(isExpanded ? null : proj.id)}
                    >
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-[#8B5CF6]/20 text-[#C084FC]">
                            {proj.difficulty}
                          </span>
                          <span className="text-xs text-[#A1A1AA]">{proj.competency_focus}</span>
                        </div>
                        <h3 className="text-sm font-bold text-white">{proj.title}</h3>
                      </div>
                      {isExpanded ? <ChevronUp className="w-5 h-5 text-[#A1A1AA]" /> : <ChevronDown className="w-5 h-5 text-[#A1A1AA]" />}
                    </div>

                    <p className="text-xs text-[#A1A1AA] mt-2">{proj.objective}</p>

                    {isExpanded && (
                      <div className="mt-4 pt-4 border-t border-[#30203F] space-y-3">
                        <div>
                          <span className="text-[10px] font-bold uppercase tracking-wider text-[#A1A1AA] block mb-1">
                            Tools & Frameworks
                          </span>
                          <div className="flex flex-wrap gap-1.5">
                            {proj.tools.map((t, idx) => (
                              <span key={idx} className="px-2 py-0.5 rounded bg-[#100B18] border border-[#30203F] text-xs text-[#D8B4FE]">
                                {t}
                              </span>
                            ))}
                          </div>
                        </div>

                        <div>
                          <span className="text-[10px] font-bold uppercase tracking-wider text-[#A1A1AA] block mb-1">
                            Step-by-Step Implementation Steps
                          </span>
                          <ol className="list-decimal list-inside text-xs text-[#D8B4FE] space-y-1">
                            {proj.steps.map((s, idx) => (
                              <li key={idx} className="leading-relaxed">{s}</li>
                            ))}
                          </ol>
                        </div>

                        <div className="p-3 rounded-lg bg-[#100B18] border border-[#30203F] text-xs text-emerald-400">
                          <strong className="block text-[11px] mb-0.5">Expected Portfolio Outcome:</strong>
                          {proj.expected_outcome}
                        </div>
                      </div>
                    )}
                  </GlowCard>
                );
              })}
            </div>
          ) : (
            <div className="py-12 text-center text-xs text-[#A1A1AA]">Select a career role to view practical projects.</div>
          )}
        </div>
      )}

      {/* TAB 5: Career Transition Pathways */}
      {activeTab === "pathways" && (
        <div className="space-y-6">
          <div className="flex flex-wrap items-center gap-2 pb-2">
            {recommendations.map((r) => (
              <button
                key={r.career_role.id}
                onClick={() => handleSelectPathwayRole(r.career_role.id)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
                  selectedProjectId === r.career_role.id
                    ? "bg-[#8B5CF6] text-white border-[#A855F7]"
                    : "bg-[#191225] border-[#30203F] text-[#A1A1AA] hover:text-white"
                }`}
              >
                {r.career_role.title}
              </button>
            ))}
          </div>

          {loadingPathways ? (
            <div className="py-12 text-center text-xs text-[#A1A1AA]">Loading transition pathways...</div>
          ) : pathways.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {pathways.map((pw) => (
                <GlowCard key={pw.id} className="p-5 flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-bold text-white flex items-center gap-1.5">
                        <Route className="w-4 h-4 text-[#C084FC]" /> Transition to: {pw.target_role_title}
                      </span>
                      <span className="text-[10px] px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 font-bold">
                        {pw.transition_difficulty}
                      </span>
                    </div>

                    <p className="text-xs text-[#A1A1AA] leading-relaxed mb-4">{pw.guidance}</p>

                    <div>
                      <span className="text-[10px] font-bold uppercase tracking-wider text-[#A1A1AA] block mb-1.5">
                        Bridge Skills to Master
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {pw.bridge_skills.map((bs, i) => (
                          <span key={i} className="text-xs px-2.5 py-1 rounded bg-[#100B18] border border-[#30203F] text-purple-300">
                            → {bs}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="pt-4 mt-4 border-t border-[#30203F]">
                    <Link
                      href={`/dashboard/roadmaps?role_id=${pw.target_role_id}`}
                      className="text-xs font-bold text-[#C084FC] hover:underline flex items-center gap-1"
                    >
                      View Pathway Roadmap <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>
                </GlowCard>
              ))}
            </div>
          ) : (
            <div className="py-12 text-center text-xs text-[#A1A1AA]">No transition pathways mapped for this role.</div>
          )}
        </div>
      )}
    </div>
  );
}
