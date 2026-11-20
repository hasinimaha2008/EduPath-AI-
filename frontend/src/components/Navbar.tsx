"use client";

import React from "react";
import Link from "next/link";
import { Sparkles, FileText, CheckCircle2, ShieldCheck } from "lucide-react";

interface NavbarProps {
  title?: string;
  subtitle?: string;
}

export const Navbar: React.FC<NavbarProps> = ({
  title = "Intelligent Learning Ecosystem",
  subtitle = "Learn Smarter. Grow Better. Build Your Career.",
}) => {
  return (
    <header className="h-16 border-b border-[#30203F] bg-[#100B18]/90 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-20">
      <div>
        <h1 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
          {title}
        </h1>
        <p className="text-xs text-[#A1A1AA] hidden sm:block">{subtitle}</p>
      </div>

      <div className="flex items-center gap-3">
        {/* Status indicator */}
        <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-[11px] font-medium text-emerald-400">
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          <span>Intelligence Engine Active</span>
        </div>

        {/* Quick actions */}
        <Link
          href="/dashboard/assistant"
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-[#191225] border border-[#30203F] text-white hover:border-[#A855F7] hover:shadow-[0_0_12px_rgba(168,85,247,0.3)] transition-all"
        >
          <Sparkles className="w-3.5 h-3.5 text-[#C084FC]" />
          <span>Ask AI</span>
        </Link>

        <Link
          href="/dashboard/quiz"
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-gradient-to-r from-[#8B5CF6] to-[#A855F7] text-white shadow-[0_0_15px_rgba(168,85,247,0.35)] hover:shadow-[0_0_20px_rgba(168,85,247,0.6)] transition-all"
        >
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>Take Quiz</span>
        </Link>
      </div>
    </header>
  );
};
