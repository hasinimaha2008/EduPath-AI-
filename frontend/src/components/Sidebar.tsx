"use client";

import React from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  LayoutDashboard,
  Bot,
  FileText,
  CheckCircle2,
  BarChart3,
  Target,
  Compass,
  Network,
  Layers,
  Milestone,
  CalendarCheck,
  UploadCloud,
  History,
  GraduationCap,
  LogOut,
  Sparkles
} from "lucide-react";
import { api } from "@/lib/api";

const navItems = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { label: "AI Study Assistant", href: "/dashboard/assistant", icon: Bot },
  { label: "Smart Notes", href: "/dashboard/notes", icon: FileText },
  { label: "AI Quiz Generator", href: "/dashboard/quiz", icon: CheckCircle2 },
  { label: "Learning Analytics", href: "/dashboard/analytics", icon: BarChart3 },
  { label: "Topic Performance", href: "/dashboard/topics", icon: Target },
  { label: "Career Intelligence", href: "/dashboard/careers", icon: Compass },
  { label: "Skill Mapping", href: "/dashboard/skill-mapping", icon: Network },
  { label: "Skill Gap Analysis", href: "/dashboard/skill-gaps", icon: Layers },
  { label: "Career Roadmap", href: "/dashboard/roadmaps", icon: Milestone },
  { label: "AI Study Planner", href: "/dashboard/study-planner", icon: CalendarCheck },
  { label: "Documents", href: "/dashboard/documents", icon: UploadCloud },
  { label: "Chat History", href: "/dashboard/chat-history", icon: History },
];

export const Sidebar: React.FC = () => {
  const pathname = usePathname();
  const router = useRouter();

  const handleLogout = () => {
    api.clearToken();
    router.push("/login");
  };

  return (
    <aside className="w-64 bg-[#120D1C] border-r border-[#30203F] flex flex-col h-screen sticky top-0 select-none z-30">
      {/* Brand Header */}
      <div className="p-5 border-b border-[#30203F] flex items-center justify-between">
        <Link href="/dashboard" className="flex items-center gap-3 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#8B5CF6] to-[#A855F7] flex items-center justify-center shadow-[0_0_15px_rgba(168,85,247,0.4)] group-hover:shadow-[0_0_22px_rgba(168,85,247,0.7)] transition-all">
            <GraduationCap className="w-6 h-6 text-white" />
          </div>
          <div>
            <span className="font-bold text-lg text-white tracking-tight flex items-center gap-1.5">
              EduPath <span className="text-[#C084FC]">AI</span>
            </span>
            <span className="text-[10px] uppercase font-semibold text-[#A1A1AA] tracking-wider block">
              Learning Ecosystem
            </span>
          </div>
        </Link>
      </div>

      {/* Nav List */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        <div className="px-3 pb-2 text-[10px] font-bold uppercase tracking-wider text-[#A1A1AA]">
          Main Navigation
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href));

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? "bg-gradient-to-r from-purple-900/60 to-purple-800/30 text-white border border-[#A855F7]/40 shadow-[0_0_15px_-3px_rgba(168,85,247,0.35)]"
                  : "text-[#A1A1AA] hover:text-white hover:bg-[#191225] hover:border hover:border-[#30203F]"
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? "text-[#C084FC]" : "text-[#A1A1AA]"}`} />
              <span className="truncate">{item.label}</span>
              {isActive && (
                <div className="ml-auto w-1.5 h-1.5 rounded-full bg-[#A855F7] shadow-[0_0_8px_#A855F7]" />
              )}
            </Link>
          );
        })}
      </nav>

      {/* Footer Profile & Logout */}
      <div className="p-3.5 border-t border-[#30203F] bg-[#100B18]">
        <div className="flex items-center justify-between p-2 rounded-lg bg-[#191225] border border-[#30203F]/60">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-8 h-8 rounded-full bg-[#8B5CF6]/30 border border-[#A855F7] flex items-center justify-center text-xs font-bold text-white shrink-0">
              AM
            </div>
            <div className="min-w-0">
              <div className="text-xs font-semibold text-white truncate">Alex Mercer</div>
              <div className="text-[10px] text-[#A1A1AA] truncate">demo@edupath.ai</div>
            </div>
          </div>
          <button
            onClick={handleLogout}
            title="Sign Out"
            className="p-1.5 text-[#A1A1AA] hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
};
