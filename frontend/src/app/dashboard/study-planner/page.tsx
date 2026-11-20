"use client";

import React, { useState, useEffect } from "react";
import {
  CalendarCheck,
  CheckCircle2,
  Circle,
  Clock,
  Sparkles,
  Calendar,
  AlertCircle,
  ArrowRight,
  RotateCcw
} from "lucide-react";
import { GlowCard } from "@/components/GlowCard";
import { api } from "@/lib/api";
import { StudyPlan, StudyTask } from "@/lib/types";

export default function StudyPlannerPage() {
  const [plan, setPlan] = useState<StudyPlan | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [dailyHours, setDailyHours] = useState(2.0);
  const [durationDays, setDurationDays] = useState(14);
  const [rescheduleTaskId, setRescheduleTaskId] = useState<string | null>(null);
  const [newDateVal, setNewDateVal] = useState<string>("");

  useEffect(() => {
    loadActivePlan();
  }, []);

  async function loadActivePlan() {
    setLoading(true);
    try {
      const active = await api.getActiveStudyPlan();
      setPlan(active);
    } catch (e) {
      console.error("Error loading study plan:", e);
    } finally {
      setLoading(false);
    }
  }

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setGenerating(true);
    try {
      const newPlan = await api.generateStudyPlan({
        daily_hours_target: dailyHours,
        days_duration: durationDays,
      });
      setPlan(newPlan);
    } catch (e) {
      console.error("Error generating plan:", e);
    } finally {
      setGenerating(false);
    }
  };

  const handleToggleTask = async (taskId: string) => {
    try {
      const res = await api.toggleTask(taskId);
      if (plan) {
        setPlan({
          ...plan,
          tasks: plan.tasks.map((t) =>
            t.id === taskId ? { ...t, is_completed: res.is_completed } : t
          ),
        });
      }
    } catch (e) {
      console.error("Error toggling task:", e);
    }
  };

  const handleReschedule = async (taskId: string) => {
    if (!newDateVal) return;
    try {
      await api.rescheduleTask(taskId, newDateVal);
      if (plan) {
        setPlan({
          ...plan,
          tasks: plan.tasks.map((t) =>
            t.id === taskId ? { ...t, scheduled_date: newDateVal } : t
          ),
        });
      }
      setRescheduleTaskId(null);
      setNewDateVal("");
    } catch (e) {
      console.error("Error rescheduling task:", e);
    }
  };

  // Group tasks by scheduled_date
  const tasksByDate = (plan?.tasks || []).reduce<Record<string, StudyTask[]>>((acc, task) => {
    acc[task.scheduled_date] = acc[task.scheduled_date] || [];
    acc[task.scheduled_date].push(task);
    return acc;
  }, {});

  const datesSorted = Object.keys(tasksByDate).sort();

  const totalTasks = plan?.tasks.length || 0;
  const completedTasks = plan?.tasks.filter((t) => t.is_completed).length || 0;
  const progressPct = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <CalendarCheck className="w-5 h-5 text-[#C084FC]" /> AI Adaptive Study Planner
          </h1>
          <p className="text-xs text-[#A1A1AA] mt-0.5">
            Generates realistic, non-overlapping daily tasks and revision schedules dynamically aligned with your verified weak topics.
          </p>
        </div>

        {/* Generate / Configure Modal toggle */}
        <form onSubmit={handleGenerate} className="flex items-center gap-2">
          <select
            value={dailyHours}
            onChange={(e) => setDailyHours(Number(e.target.value))}
            className="px-2.5 py-1.5 rounded-lg bg-[#191225] border border-[#30203F] text-xs text-white focus:outline-none focus:border-[#A855F7]"
          >
            <option value={1.5}>1.5 hrs / day</option>
            <option value={2.0}>2.0 hrs / day</option>
            <option value={3.0}>3.0 hrs / day</option>
          </select>

          <button
            type="submit"
            disabled={generating}
            className="px-4 py-1.5 rounded-lg text-xs font-bold bg-gradient-to-r from-[#8B5CF6] to-[#A855F7] text-white shadow-[0_0_12px_rgba(168,85,247,0.3)] hover:shadow-[0_0_18px_rgba(168,85,247,0.6)] disabled:opacity-50 transition-all flex items-center gap-1.5 shrink-0"
          >
            <Sparkles className="w-3.5 h-3.5" />
            {generating ? "Adapting..." : "Rebalance Schedule"}
          </button>
        </form>
      </div>

      {plan && (
        <>
          {/* Progress Banner */}
          <GlowCard glow className="p-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <span className="text-[10px] font-bold text-[#A855F7] uppercase tracking-wider">
                  Active Adaptive Schedule
                </span>
                <h2 className="text-xl font-bold text-white mt-0.5">{plan.title}</h2>
                <div className="flex items-center gap-3 text-xs text-[#A1A1AA] mt-1">
                  <span>Target: {plan.daily_hours_target} hrs/day</span>
                  <span>•</span>
                  <span>{completedTasks} of {totalTasks} tasks completed</span>
                </div>
              </div>

              <div className="text-right sm:border-l sm:border-[#30203F] sm:pl-6 shrink-0">
                <span className="text-3xl font-extrabold text-white">{progressPct}%</span>
                <span className="text-xs text-[#C084FC] block font-semibold">
                  Schedule Adherence
                </span>
              </div>
            </div>

            <div className="mt-4">
              <div className="w-full h-2 rounded-full bg-[#100B18] overflow-hidden border border-[#30203F]">
                <div
                  className="h-full bg-gradient-to-r from-[#8B5CF6] to-[#A855F7] transition-all duration-500"
                  style={{ width: `${progressPct}%` }}
                />
              </div>
            </div>
          </GlowCard>

          {/* Grouped Day-by-Day Timeline */}
          <div className="space-y-6">
            {datesSorted.map((dateStr) => {
              const dayTasks = tasksByDate[dateStr];
              return (
                <div key={dateStr} className="space-y-3">
                  <div className="flex items-center gap-2 text-xs font-bold text-[#C084FC] uppercase tracking-wider">
                    <Calendar className="w-3.5 h-3.5" />
                    <span>{dateStr}</span>
                    <span className="text-[10px] text-[#A1A1AA] font-normal">
                      ({dayTasks.length} tasks scheduled)
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {dayTasks.map((task) => (
                      <GlowCard
                        key={task.id}
                        className={`p-4 transition-all ${
                          task.is_completed ? "border-emerald-500/40 bg-[#120D1C]" : ""
                        }`}
                      >
                        <div className="flex items-start justify-between gap-3">
                          <div className="flex items-start gap-2.5 min-w-0">
                            <button
                              onClick={() => handleToggleTask(task.id)}
                              className="mt-0.5 text-[#A855F7] hover:scale-110 transition-transform shrink-0"
                            >
                              {task.is_completed ? (
                                <CheckCircle2 className="w-5 h-5 text-emerald-400 fill-emerald-400/20" />
                              ) : (
                                <Circle className="w-5 h-5 text-[#A1A1AA]" />
                              )}
                            </button>

                            <div className="min-w-0">
                              <span
                                className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded ${
                                  task.priority === "High"
                                    ? "bg-red-500/20 text-red-300 border border-red-500/30"
                                    : "bg-purple-500/20 text-[#C084FC] border border-purple-500/30"
                                }`}
                              >
                                {task.priority} Priority Focus
                              </span>

                              <h4
                                className={`text-sm font-bold mt-1 truncate ${
                                  task.is_completed ? "line-through text-gray-400" : "text-white"
                                }`}
                              >
                                {task.title}
                              </h4>
                              <p className="text-xs text-[#A1A1AA] mt-1 leading-relaxed">
                                {task.description}
                              </p>
                              <div className="flex items-center gap-2 mt-2 text-[10px] text-[#A1A1AA]">
                                <Clock className="w-3 h-3 text-[#A855F7]" />
                                <span>{task.duration_minutes} mins</span>
                                {task.topic_name && <span>• Topic: {task.topic_name}</span>}
                              </div>
                            </div>
                          </div>

                          <button
                            onClick={() => {
                              setRescheduleTaskId(task.id);
                              setNewDateVal(task.scheduled_date);
                            }}
                            className="text-[11px] text-[#A1A1AA] hover:text-[#C084FC] shrink-0"
                          >
                            Reschedule
                          </button>
                        </div>

                        {/* Reschedule inline form */}
                        {rescheduleTaskId === task.id && (
                          <div className="mt-3 pt-3 border-t border-[#30203F] flex items-center gap-2">
                            <input
                              type="date"
                              value={newDateVal}
                              onChange={(e) => setNewDateVal(e.target.value)}
                              className="px-2 py-1 rounded bg-[#100B18] border border-[#30203F] text-xs text-white"
                            />
                            <button
                              onClick={() => handleReschedule(task.id)}
                              className="px-2.5 py-1 rounded bg-purple-600 text-white text-xs font-bold"
                            >
                              Save Date
                            </button>
                            <button
                              onClick={() => setRescheduleTaskId(null)}
                              className="px-2.5 py-1 text-xs text-[#A1A1AA] hover:text-white"
                            >
                              Cancel
                            </button>
                          </div>
                        )}
                      </GlowCard>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}
