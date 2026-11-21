"use client";

import React, { useState, useEffect, useRef } from "react";
import Link from "next/link";
import {
  Sparkles,
  CheckCircle2,
  Bell,
  Check,
  AlertTriangle,
  Calendar,
  Compass,
  BookOpen,
  X
} from "lucide-react";
import { api } from "@/lib/api";
import { NotificationItem } from "@/lib/types";

interface NavbarProps {
  title?: string;
  subtitle?: string;
}

export const Navbar: React.FC<NavbarProps> = ({
  title = "Intelligent Learning Ecosystem",
  subtitle = "Learn Smarter. Grow Better. Build Your Career.",
}) => {
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [unreadCount, setUnreadCount] = useState<number>(0);
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const fetchNotifications = async () => {
    try {
      setLoading(true);
      const res = await api.listNotifications();
      setNotifications(res.notifications || []);
      setUnreadCount(res.unread_count || 0);
    } catch (err) {
      // ignore unauthenticated or background error
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 45000);
    return () => clearInterval(interval);
  }, []);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [isOpen]);

  const handleMarkAsRead = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await api.markNotificationRead(id);
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, is_read: true } : n));
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (err) {
      console.error("Failed to mark notification read", err);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await api.markAllNotificationsRead();
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch (err) {
      console.error("Failed to mark all read", err);
    }
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case "weak_topic_alert":
        return <AlertTriangle className="w-4 h-4 text-amber-400" />;
      case "revision_due":
        return <Calendar className="w-4 h-4 text-purple-400" />;
      case "career_milestone":
        return <Compass className="w-4 h-4 text-emerald-400" />;
      case "quiz_feedback":
        return <CheckCircle2 className="w-4 h-4 text-blue-400" />;
      default:
        return <BookOpen className="w-4 h-4 text-[#A855F7]" />;
    }
  };

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
          <span>Intelligence Engine 2.0</span>
        </div>

        {/* Notification Bell Dropdown */}
        <div className="relative" ref={dropdownRef}>
          <button
            onClick={() => {
              setIsOpen(!isOpen);
              if (!isOpen) fetchNotifications();
            }}
            className="relative p-2 rounded-lg bg-[#191225] border border-[#30203F] text-[#A1A1AA] hover:text-white hover:border-[#A855F7] transition-all"
            title="Notifications & Study Reminders"
          >
            <Bell className="w-4 h-4" />
            {unreadCount > 0 && (
              <span className="absolute -top-1 -right-1 px-1.5 py-0.2 min-w-[18px] h-[18px] rounded-full bg-gradient-to-r from-purple-500 to-pink-500 text-white text-[10px] font-bold flex items-center justify-center shadow-[0_0_8px_rgba(168,85,247,0.7)] animate-pulse">
                {unreadCount > 9 ? "9+" : unreadCount}
              </span>
            )}
          </button>

          {/* Popover */}
          {isOpen && (
            <div className="absolute right-0 mt-2 w-80 sm:w-96 bg-[#160F23] border border-[#30203F] rounded-xl shadow-[0_10px_35px_rgba(0,0,0,0.6)] py-3 z-50 text-left">
              <div className="px-4 pb-2.5 border-b border-[#30203F] flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-sm text-white">Notifications</span>
                  {unreadCount > 0 && (
                    <span className="px-1.5 py-0.5 rounded-full bg-[#A855F7]/20 text-[#C084FC] text-[10px] font-bold">
                      {unreadCount} new
                    </span>
                  )}
                </div>
                {unreadCount > 0 && (
                  <button
                    onClick={handleMarkAllRead}
                    className="text-xs text-[#A1A1AA] hover:text-white transition-colors"
                  >
                    Mark all read
                  </button>
                )}
              </div>

              <div className="max-h-80 overflow-y-auto divide-y divide-[#30203F]/50">
                {notifications.length === 0 ? (
                  <div className="p-6 text-center text-[#71717A] text-xs">
                    No new notifications. You are completely caught up!
                  </div>
                ) : (
                  notifications.map((n) => (
                    <div
                      key={n.id}
                      className={`p-3.5 hover:bg-[#1C142D] transition-colors flex items-start gap-3 cursor-pointer ${
                        !n.is_read ? "bg-[#1F1533]/40" : ""
                      }`}
                      onClick={() => {
                        if (n.action_url) {
                          window.location.href = n.action_url;
                        }
                      }}
                    >
                      <div className="mt-0.5 p-1.5 rounded-lg bg-[#251A38] border border-[#382650]">
                        {getNotificationIcon(n.notification_type)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between gap-1">
                          <p className={`text-xs font-semibold truncate ${!n.is_read ? "text-white" : "text-[#D4D4D8]"}`}>
                            {n.title}
                          </p>
                          {!n.is_read && (
                            <button
                              onClick={(e) => handleMarkAsRead(n.id, e)}
                              className="text-[#71717A] hover:text-[#C084FC] p-0.5"
                              title="Mark read"
                            >
                              <Check className="w-3.5 h-3.5" />
                            </button>
                          )}
                        </div>
                        <p className="text-[11px] text-[#A1A1AA] mt-1 line-clamp-2 leading-relaxed">
                          {n.message}
                        </p>
                        <span className="text-[10px] text-[#71717A] mt-1.5 block">
                          {new Date(n.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                      </div>
                    </div>
                  ))
                )}
              </div>

              <div className="px-4 pt-2 border-t border-[#30203F] text-center">
                <Link
                  href="/dashboard/workspace"
                  onClick={() => setIsOpen(false)}
                  className="text-xs text-[#A855F7] hover:text-[#C084FC] font-medium"
                >
                  Go to Learning Workspace →
                </Link>
              </div>
            </div>
          )}
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
