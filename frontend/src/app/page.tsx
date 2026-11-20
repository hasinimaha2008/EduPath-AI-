"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  GraduationCap,
  Sparkles,
  Bot,
  FileText,
  CheckCircle2,
  BarChart3,
  Compass,
  Network,
  Layers,
  Milestone,
  CalendarCheck,
  UploadCloud,
  ArrowRight,
  ShieldCheck,
  Zap
} from "lucide-react";
import { GlowCard } from "@/components/GlowCard";
import { api } from "@/lib/api";

export default function LandingPage() {
  const router = useRouter();
  const [loadingDemo, setLoadingDemo] = useState(false);

  const handleDemoAccess = async () => {
    try {
      setLoadingDemo(true);
      await api.demoLogin();
      router.push("/dashboard");
    } catch (e) {
      router.push("/login");
    } finally {
      setLoadingDemo(false);
    }
  };

  const featureCards = [
    {
      title: "AI Study Assistant",
      desc: "Instant academic explanations with step-by-step breakdowns and verified RAG document citations.",
      icon: Bot,
      color: "#8B5CF6",
    },
    {
      title: "Smart Notes Generator",
      desc: "Generate 8 distinct note formats: detailed, exam-oriented, revision, definitions, and high-yield questions.",
      icon: FileText,
      color: "#A855F7",
    },
    {
      title: "AI Quiz Generator",
      desc: "Dynamic MCQ and short-answer evaluations with difficulty scaling. Answer keys strictly masked during quiz.",
      icon: CheckCircle2,
      color: "#C084FC",
    },
    {
      title: "Learning Analytics",
      desc: "Real quiz metrics, retention trends, and verified weak-topic alerts visualized through Recharts.",
      icon: BarChart3,
      color: "#8B5CF6",
    },
    {
      title: "Academic-to-Industry Mapping",
      desc: "Connects course topics to industry competencies, verified skills, and in-demand technical roles.",
      icon: Network,
      color: "#A855F7",
    },
    {
      title: "Career Intelligence & Gaps",
      desc: "Calculates match readiness across 8 tech careers, comparing verified learning evidence against industry standards.",
      icon: Compass,
      color: "#C084FC",
    },
    {
      title: "Personalized Career Roadmap",
      desc: "Phased project milestones, sequence guidance, and progress tracking validated by skill requirements.",
      icon: Milestone,
      color: "#8B5CF6",
    },
    {
      title: "AI Study Planner",
      desc: "Conflict-free daily study tasks that automatically adapt to schedule priority and weak-topic revision.",
      icon: CalendarCheck,
      color: "#A855F7",
    },
  ];

  return (
    <div className="min-h-screen bg-[#08060D] text-white flex flex-col selection:bg-[#8B5CF6]">
      {/* Top Navigation */}
      <header className="border-b border-[#30203F] bg-[#100B18]/80 backdrop-blur-md sticky top-0 z-50 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#8B5CF6] to-[#A855F7] flex items-center justify-center shadow-[0_0_15px_rgba(168,85,247,0.4)]">
              <GraduationCap className="w-6 h-6 text-white" />
            </div>
            <div>
              <span className="font-extrabold text-xl text-white tracking-tight flex items-center gap-1.5">
                EduPath <span className="text-[#C084FC]">AI</span>
              </span>
              <span className="text-[10px] uppercase font-semibold text-[#A1A1AA] tracking-wider block">
                Intelligent Learning Ecosystem
              </span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <Link
              href="/login"
              className="text-sm font-semibold text-[#A1A1AA] hover:text-white transition-colors"
            >
              Sign In
            </Link>
            <button
              onClick={handleDemoAccess}
              disabled={loadingDemo}
              className="px-4 py-2 rounded-lg text-sm font-bold bg-gradient-to-r from-[#8B5CF6] to-[#A855F7] hover:shadow-[0_0_20px_rgba(168,85,247,0.6)] text-white transition-all flex items-center gap-2"
            >
              {loadingDemo ? "Accessing..." : "Launch Demo"}
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative px-6 py-20 lg:py-28 text-center max-w-5xl mx-auto flex flex-col items-center">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#191225] border border-purple-500/40 text-xs font-semibold text-[#C084FC] mb-8 shadow-[0_0_15px_rgba(168,85,247,0.25)]">
          <Sparkles className="w-4 h-4 text-[#A855F7]" />
          Intelligent Learning & Career Ecosystem
        </div>

        <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight leading-[1.1] mb-6">
          Learn Smarter. Grow Better. <br />
          <span className="bg-gradient-to-r from-[#C084FC] via-[#A855F7] to-[#8B5CF6] bg-clip-text text-transparent text-glow">
            Build Your Career.
          </span>
        </h1>

        <p className="text-lg sm:text-xl text-[#A1A1AA] max-w-3xl mb-10 leading-relaxed">
          The unified intelligence engine connecting academic study, RAG question-answering,
          knowledge evaluation, industry skill taxonomy, and personalized career roadmaps.
        </p>

        <div className="flex flex-col sm:flex-row items-center gap-4 w-full sm:w-auto">
          <button
            onClick={handleDemoAccess}
            disabled={loadingDemo}
            className="w-full sm:w-auto px-8 py-3.5 rounded-xl text-base font-bold bg-gradient-to-r from-[#8B5CF6] to-[#A855F7] text-white shadow-[0_0_25px_rgba(168,85,247,0.5)] hover:shadow-[0_0_35px_rgba(168,85,247,0.8)] transition-all flex items-center justify-center gap-2"
          >
            {loadingDemo ? "Launching..." : "Explore Ecosystem Now"}
            <ArrowRight className="w-5 h-5" />
          </button>
          <Link
            href="/register"
            className="w-full sm:w-auto px-8 py-3.5 rounded-xl text-base font-semibold bg-[#191225] border border-[#30203F] hover:border-purple-500/50 text-white transition-all text-center"
          >
            Create Free Account
          </Link>
        </div>
      </section>

      {/* Central Intelligence Engine Workflow Banner */}
      <section className="px-6 py-12 max-w-7xl mx-auto w-full">
        <GlowCard glow className="p-8 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-80 h-80 bg-purple-600/10 rounded-full blur-[100px] pointer-events-none" />
          <div className="max-w-3xl mb-8">
            <span className="text-xs font-bold uppercase tracking-wider text-[#C084FC]">
              Core Differentiator
            </span>
            <h2 className="text-2xl sm:text-3xl font-bold mt-1 text-white">
              The Central EduPath Intelligence Engine
            </h2>
            <p className="text-[#A1A1AA] text-sm mt-2">
              Unlike disconnected tools, EduPath AI creates a continuous closed-loop learning profile:
              quiz performance directly feeds topic tracking, maps to industry competencies, recalculates career readiness, and updates your study schedule.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-4 rounded-lg bg-[#100B18] border border-[#30203F]">
              <div className="text-xs font-bold text-[#A855F7] mb-1">01. Academic Input</div>
              <div className="text-sm font-semibold text-white">Upload Notes & Ask RAG Questions</div>
              <div className="text-xs text-[#A1A1AA] mt-1">Grounds study in verified course material with page citations.</div>
            </div>
            <div className="p-4 rounded-lg bg-[#100B18] border border-[#30203F]">
              <div className="text-xs font-bold text-[#A855F7] mb-1">02. Knowledge Evaluation</div>
              <div className="text-sm font-semibold text-white">Interactive Assessment Quizzes</div>
              <div className="text-xs text-[#A1A1AA] mt-1">Tracks accuracy and requires repeated evidence for mastery.</div>
            </div>
            <div className="p-4 rounded-lg bg-[#100B18] border border-[#30203F]">
              <div className="text-xs font-bold text-[#A855F7] mb-1">03. Skill Mapping</div>
              <div className="text-sm font-semibold text-white">Academic → Industry Taxonomies</div>
              <div className="text-xs text-[#A1A1AA] mt-1">Connects topics like Normalization to SQL & Backend roles.</div>
            </div>
            <div className="p-4 rounded-lg bg-[#100B18] border border-[#30203F]">
              <div className="text-xs font-bold text-[#A855F7] mb-1">04. Adaptive Planning</div>
              <div className="text-sm font-semibold text-white">Targeted Roadmaps & Tasks</div>
              <div className="text-xs text-[#A1A1AA] mt-1">Auto-schedules revision sessions for weak areas.</div>
            </div>
          </div>
        </GlowCard>
      </section>

      {/* 8 Feature Modules Showcase */}
      <section className="px-6 py-16 max-w-7xl mx-auto w-full">
        <div className="text-center max-w-2xl mx-auto mb-12">
          <h2 className="text-3xl font-extrabold text-white">Complete Integrated Suite</h2>
          <p className="text-sm text-[#A1A1AA] mt-2">
            Every feature is purpose-built to accelerate your academic mastery and bridge you to career success.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {featureCards.map((f, i) => {
            const Icon = f.icon;
            return (
              <GlowCard key={i} className="p-6 flex flex-col justify-between">
                <div>
                  <div
                    className="w-12 h-12 rounded-xl flex items-center justify-center mb-4 border border-[#30203F]"
                    style={{ backgroundColor: "rgba(139, 92, 246, 0.15)" }}
                  >
                    <Icon className="w-6 h-6 text-[#C084FC]" />
                  </div>
                  <h3 className="text-base font-bold text-white mb-2">{f.title}</h3>
                  <p className="text-xs text-[#A1A1AA] leading-relaxed">{f.desc}</p>
                </div>
              </GlowCard>
            );
          })}
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto border-t border-[#30203F] bg-[#100B18] px-6 py-8">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-[#A1A1AA]">
          <div className="flex items-center gap-2">
            <span className="font-bold text-white">EduPath AI</span>
            <span>– Intelligent Learning & Career Ecosystem.</span>
          </div>
          <div>All academic rights reserved. Secure RAG and encrypted data architecture.</div>
        </div>
      </footer>
    </div>
  );
}
