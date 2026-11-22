"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  CalendarCheck,
  CheckCircle2,
  Circle,
  Clock,
  Sparkles,
  Calendar,
  AlertCircle,
  ArrowRight,
  RotateCcw,
  BookOpen,
  Plus,
  Trash2,
  Edit3,
  ExternalLink,
  Flame,
  Target,
  X,
  Filter,
  Check,
  Zap,
  HelpCircle
} from "lucide-react";
import { GlowCard } from "@/components/GlowCard";
import { api } from "@/lib/api";
import {
  StudyPlan,
  StudyTask,
  PlannerProgress,
  AdaptiveRecommendationItem,
  StudyPlanGenerateOptions,
  StudyTaskCreateInput,
  StudyTaskUpdateInput,
  Subject
} from "@/lib/types";

export default function StudyPlannerPage() {
  const [plan, setPlan] = useState<StudyPlan | null>(null);
  const [progress, setProgress] = useState<PlannerProgress | null>(null);
  const [recommendations, setRecommendations] = useState<AdaptiveRecommendationItem[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [loading, setLoading] = useState(true);

  // Filter state
  const [activeTab, setActiveTab] = useState<"all" | "today" | "pending" | "overdue">("all");
  const [typeFilter, setTypeFilter] = useState<string>("all");

  // Modals state
  const [showConfigModal, setShowConfigModal] = useState(false);
  const [showAddTaskModal, setShowAddTaskModal] = useState(false);
  const [editingTask, setEditingTask] = useState<StudyTask | null>(null);
  const [rescheduleTaskId, setRescheduleTaskId] = useState<string | null>(null);
  const [newDateVal, setNewDateVal] = useState<string>("");

  // Plan generation form
  const [genTitle, setGenTitle] = useState("Personalized Adaptive Study Plan");
  const [genDailyHours, setGenDailyHours] = useState(2.0);
  const [genDurationDays, setGenDurationDays] = useState(14);
  const [genExamDate, setGenExamDate] = useState("");
  const [genPriority, setGenPriority] = useState<string>("weak_topics_first");
  const [genIncludeRevision, setGenIncludeRevision] = useState(true);
  const [genIncludeQuizzes, setGenIncludeQuizzes] = useState(true);
  const [generating, setGenerating] = useState(false);

  // New task form
  const [newTaskTitle, setNewTaskTitle] = useState("");
  const [newTaskTopic, setNewTaskTopic] = useState("");
  const [newTaskDate, setNewTaskDate] = useState(new Date().toISOString().split("T")[0]);
  const [newTaskDuration, setNewTaskDuration] = useState(45);
  const [newTaskPriority, setNewTaskPriority] = useState<"High" | "Medium" | "Low">("Medium");
  const [newTaskType, setNewTaskType] = useState<string>("study");
  const [creatingTask, setCreatingTask] = useState(false);

  // Rebalancing state
  const [rebalancing, setRebalancing] = useState(false);
  const [rebalanceMsg, setRebalanceMsg] = useState<string | null>(null);

  useEffect(() => {
    loadAllPlannerData();
  }, []);

  async function loadAllPlannerData() {
    setLoading(true);
    try {
      const [activePlan, progressData, recsData, subjList] = await Promise.all([
        api.getActiveStudyPlan().catch(() => null),
        api.getPlannerProgress().catch(() => null),
        api.getPlannerAdaptiveRecommendations().catch(() => []),
        api.getSubjects().catch(() => [])
      ]);

      if (activePlan) setPlan(activePlan);
      if (progressData) setProgress(progressData);
      setRecommendations(recsData);
      setSubjects(subjList);
    } catch (e) {
      console.error("Error loading study planner data:", e);
    } finally {
      setLoading(false);
    }
  }

  // Handle plan regeneration
  const handleGeneratePlan = async (e: React.FormEvent) => {
    e.preventDefault();
    setGenerating(true);
    try {
      const options: StudyPlanGenerateOptions = {
        title: genTitle,
        daily_hours_target: genDailyHours,
        days_duration: genDurationDays,
        exam_date: genExamDate || undefined,
        learning_priority: genPriority,
        include_revision: genIncludeRevision,
        include_quizzes: genIncludeQuizzes,
        focus_weak_topics: true
      };
      const newPlan = await api.generateStudyPlan(options);
      setPlan(newPlan);
      setShowConfigModal(false);
      // Reload progress & recommendations
      const [prog, recs] = await Promise.all([
        api.getPlannerProgress().catch(() => null),
        api.getPlannerAdaptiveRecommendations().catch(() => [])
      ]);
      if (prog) setProgress(prog);
      setRecommendations(recs);
    } catch (e) {
      console.error("Error generating adaptive plan:", e);
    } finally {
      setGenerating(false);
    }
  };

  // Toggle task completion
  const handleToggleTask = async (taskId: string) => {
    try {
      const res = await api.toggleTask(taskId);
      if (plan) {
        setPlan({
          ...plan,
          tasks: plan.tasks.map((t) =>
            t.id === taskId
              ? { ...t, is_completed: res.is_completed, is_overdue: false, completed_at: res.completed_at }
              : t
          ),
        });
      }
      // Refresh progress
      const prog = await api.getPlannerProgress().catch(() => null);
      if (prog) setProgress(prog);
    } catch (e) {
      console.error("Error toggling task:", e);
    }
  };

  // Reschedule single task
  const handleReschedule = async (taskId: string) => {
    if (!newDateVal) return;
    try {
      await api.rescheduleTask(taskId, newDateVal);
      if (plan) {
        setPlan({
          ...plan,
          tasks: plan.tasks.map((t) =>
            t.id === taskId ? { ...t, scheduled_date: newDateVal, is_overdue: false } : t
          ),
        });
      }
      setRescheduleTaskId(null);
      setNewDateVal("");
      const prog = await api.getPlannerProgress().catch(() => null);
      if (prog) setProgress(prog);
    } catch (e) {
      console.error("Error rescheduling task:", e);
    }
  };

  // Intelligent bulk rebalance of missed/overdue tasks
  const handleRebalanceMissed = async () => {
    setRebalancing(true);
    setRebalanceMsg(null);
    try {
      const res = await api.rescheduleMissedTasks();
      setRebalanceMsg(res.message);
      await loadAllPlannerData();
    } catch (e) {
      console.error("Error rebalancing missed tasks:", e);
    } finally {
      setRebalancing(false);
    }
  };

  // Create custom task
  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTaskTitle.trim()) return;
    setCreatingTask(true);
    try {
      const input: StudyTaskCreateInput = {
        title: newTaskTitle.trim(),
        scheduled_date: newTaskDate,
        duration_minutes: newTaskDuration,
        priority: newTaskPriority,
        task_type: newTaskType,
        difficulty_level: "medium"
      };
      const created = await api.createCustomTask(input);
      if (plan) {
        setPlan({
          ...plan,
          tasks: [...plan.tasks, created]
        });
      }
      setShowAddTaskModal(false);
      setNewTaskTitle("");
      const prog = await api.getPlannerProgress().catch(() => null);
      if (prog) setProgress(prog);
    } catch (e) {
      console.error("Error creating custom task:", e);
    } finally {
      setCreatingTask(false);
    }
  };

  // Edit task save
  const handleSaveEditTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingTask) return;
    try {
      const updated = await api.updateTask(editingTask.id, {
        title: editingTask.title,
        description: editingTask.description,
        scheduled_date: editingTask.scheduled_date,
        duration_minutes: editingTask.duration_minutes,
        priority: editingTask.priority,
        task_type: editingTask.task_type,
        notes: editingTask.notes
      });
      if (plan) {
        setPlan({
          ...plan,
          tasks: plan.tasks.map((t) => (t.id === updated.id ? updated : t))
        });
      }
      setEditingTask(null);
      const prog = await api.getPlannerProgress().catch(() => null);
      if (prog) setProgress(prog);
    } catch (e) {
      console.error("Error updating task:", e);
    }
  };

  // Delete task
  const handleDeleteTask = async (taskId: string) => {
    if (!confirm("Remove this study task from your schedule?")) return;
    try {
      await api.deleteTask(taskId);
      if (plan) {
        setPlan({
          ...plan,
          tasks: plan.tasks.filter((t) => t.id !== taskId)
        });
      }
      const prog = await api.getPlannerProgress().catch(() => null);
      if (prog) setProgress(prog);
    } catch (e) {
      console.error("Error deleting task:", e);
    }
  };

  // Group and filter tasks
  const todayStr = progress?.today_date || new Date().toISOString().split("T")[0];

  const filteredTasks = (plan?.tasks || []).filter((task) => {
    if (activeTab === "today" && task.scheduled_date !== todayStr) return false;
    if (activeTab === "pending" && task.is_completed) return false;
    if (activeTab === "overdue" && (!task.is_overdue || task.is_completed)) return false;
    if (typeFilter !== "all" && task.task_type !== typeFilter) return false;
    return true;
  });

  const tasksByDate = filteredTasks.reduce<Record<string, StudyTask[]>>((acc, task) => {
    acc[task.scheduled_date] = acc[task.scheduled_date] || [];
    acc[task.scheduled_date].push(task);
    return acc;
  }, {});

  const datesSorted = Object.keys(tasksByDate).sort();

  const totalTasks = plan?.tasks.length || 0;
  const completedTasks = plan?.tasks.filter((t) => t.is_completed).length || 0;
  const overdueTasksCount = plan?.tasks.filter((t) => t.is_overdue && !t.is_completed).length || 0;
  const scheduleAdherencePct = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <CalendarCheck className="w-5 h-5 text-[#C084FC]" /> AI Adaptive Study Planner
          </h1>
          <p className="text-xs text-[#A1A1AA] mt-1 max-w-2xl">
            Generates realistic, non-overloading daily schedules that continuously adapt to your quiz results, pace, and examination deadlines.
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2 flex-wrap">
          <button
            onClick={() => setShowAddTaskModal(true)}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-[#191225] border border-[#30203F] text-white hover:border-[#8B5CF6] transition-colors flex items-center gap-1.5"
          >
            <Plus className="w-3.5 h-3.5 text-[#C084FC]" />
            Add Task
          </button>

          <button
            onClick={() => setShowConfigModal(true)}
            className="px-3.5 py-1.5 rounded-lg text-xs font-bold bg-gradient-to-r from-[#8B5CF6] to-[#A855F7] text-white shadow-[0_0_12px_rgba(168,85,247,0.3)] hover:shadow-[0_0_18px_rgba(168,85,247,0.6)] transition-all flex items-center gap-1.5"
          >
            <Sparkles className="w-3.5 h-3.5" />
            Adaptive Settings
          </button>
        </div>
      </div>

      {/* Adaptive Alerts & Overdue Intervention Banner */}
      {overdueTasksCount > 0 && (
        <div className="p-3.5 rounded-xl bg-red-950/30 border border-red-500/40 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-2 text-red-200">
            <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
            <span>
              You have <strong className="font-bold text-white">{overdueTasksCount} overdue tasks</strong> from past dates.
            </span>
          </div>

          <button
            onClick={handleRebalanceMissed}
            disabled={rebalancing}
            className="px-3 py-1.5 rounded-lg bg-red-500/20 border border-red-500/40 text-red-200 hover:bg-red-500/30 font-semibold transition-all flex items-center gap-1.5 self-start sm:self-auto shrink-0"
          >
            <RotateCcw className={`w-3.5 h-3.5 ${rebalancing ? "animate-spin" : ""}`} />
            {rebalancing ? "Rebalancing..." : "Auto-Rebalance Missed Tasks"}
          </button>
        </div>
      )}

      {rebalanceMsg && (
        <div className="p-3 rounded-lg bg-emerald-950/30 border border-emerald-500/40 text-emerald-200 text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>{rebalanceMsg}</span>
        </div>
      )}

      {/* Proactive Adaptive Recommendations Banner */}
      {recommendations.length > 0 && (
        <div className="space-y-2">
          {recommendations.map((rec) => (
            <div
              key={rec.id}
              className="p-3 rounded-xl bg-[#191225] border border-[#8B5CF6]/30 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs"
            >
              <div className="flex items-start gap-2.5">
                <Zap className="w-4 h-4 text-[#C084FC] shrink-0 mt-0.5" />
                <div>
                  <div className="font-semibold text-white">{rec.reason}</div>
                  <div className="text-[11px] text-[#A1A1AA] mt-0.5">{rec.suggested_action}</div>
                </div>
              </div>

              {rec.recommendation_type === "weak_topic_revision" && rec.topic_name && (
                <Link
                  href={`/dashboard/notes?topic=${encodeURIComponent(rec.topic_name)}&mode=revision`}
                  className="px-3 py-1.5 rounded-lg bg-[#8B5CF6]/20 border border-[#A855F7]/40 text-[#D8B4FE] hover:bg-[#8B5CF6]/30 font-semibold transition-all flex items-center gap-1 self-start sm:self-auto shrink-0"
                >
                  <BookOpen className="w-3.5 h-3.5" />
                  Open Smart Notes
                </Link>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Hero Progress Banner */}
      {plan && (
        <GlowCard glow className="p-5">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-center">
            {/* Title & Priority */}
            <div className="md:col-span-2">
              <div className="flex items-center gap-2 text-[10px] font-bold text-[#A855F7] uppercase tracking-wider">
                <span>Adaptive Active Plan</span>
                <span>•</span>
                <span className="text-[#C084FC]">
                  {plan.learning_priority === "weak_topics_first" ? "Weak Topics First" : plan.learning_priority}
                </span>
              </div>
              <h2 className="text-lg font-bold text-white mt-0.5">{plan.title}</h2>
              <div className="flex items-center gap-3 text-xs text-[#A1A1AA] mt-1">
                <span>Target: {plan.daily_hours_target} hrs/day</span>
                <span>•</span>
                <span>{completedTasks} of {totalTasks} tasks completed</span>
              </div>
            </div>

            {/* Exam Countdown (if set) */}
            {progress?.exam_countdown_days !== null && progress?.exam_countdown_days !== undefined ? (
              <div className="p-3 rounded-lg bg-[#100B18] border border-[#30203F] text-center">
                <span className="text-[10px] uppercase font-bold text-[#A1A1AA] flex items-center justify-center gap-1">
                  <Target className="w-3 h-3 text-[#A855F7]" /> Exam Target
                </span>
                <span className="text-xl font-extrabold text-white block mt-0.5">
                  {progress.exam_countdown_days} days
                </span>
                <span className="text-[10px] text-[#D8B4FE] block">
                  {plan.exam_date}
                </span>
              </div>
            ) : (
              <div className="p-3 rounded-lg bg-[#100B18] border border-[#30203F] text-center">
                <span className="text-[10px] uppercase font-bold text-[#A1A1AA] flex items-center justify-center gap-1">
                  <Flame className="w-3 h-3 text-orange-400" /> Study Streak
                </span>
                <span className="text-xl font-extrabold text-white block mt-0.5">
                  {progress?.learning_streak_days || 0} days
                </span>
                <span className="text-[10px] text-emerald-400 block">
                  {progress?.weak_topics_covered_count || 0} weak topics reinforced
                </span>
              </div>
            )}

            {/* Overall Schedule Adherence */}
            <div className="text-right sm:border-l sm:border-[#30203F] sm:pl-4">
              <span className="text-3xl font-extrabold text-white">{scheduleAdherencePct}%</span>
              <span className="text-xs text-[#C084FC] block font-semibold">
                Schedule Adherence
              </span>
              <div className="w-full h-1.5 rounded-full bg-[#100B18] overflow-hidden border border-[#30203F] mt-2">
                <div
                  className="h-full bg-gradient-to-r from-[#8B5CF6] to-[#A855F7] transition-all duration-500"
                  style={{ width: `${scheduleAdherencePct}%` }}
                />
              </div>
            </div>
          </div>
        </GlowCard>
      )}

      {/* Filter Tabs & Type Selector */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#30203F]/60 pb-3">
        {/* Navigation Tabs */}
        <div className="flex items-center gap-1 overflow-x-auto pb-1 sm:pb-0">
          <button
            onClick={() => setActiveTab("all")}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
              activeTab === "all"
                ? "bg-[#8B5CF6] text-white"
                : "text-[#A1A1AA] hover:text-white hover:bg-[#191225]"
            }`}
          >
            All Tasks ({plan?.tasks.length || 0})
          </button>
          <button
            onClick={() => setActiveTab("today")}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
              activeTab === "today"
                ? "bg-[#8B5CF6] text-white"
                : "text-[#A1A1AA] hover:text-white hover:bg-[#191225]"
            }`}
          >
            Today&apos;s Focus ({progress?.today_total_tasks || 0})
          </button>
          <button
            onClick={() => setActiveTab("pending")}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
              activeTab === "pending"
                ? "bg-[#8B5CF6] text-white"
                : "text-[#A1A1AA] hover:text-white hover:bg-[#191225]"
            }`}
          >
            Pending ({totalTasks - completedTasks})
          </button>
          {overdueTasksCount > 0 && (
            <button
              onClick={() => setActiveTab("overdue")}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                activeTab === "overdue"
                  ? "bg-red-600 text-white"
                  : "text-red-400 hover:text-white hover:bg-red-950/40"
              }`}
            >
              Overdue ({overdueTasksCount})
            </button>
          )}
        </div>

        {/* Task Type Filter Dropdown */}
        <div className="flex items-center gap-2 text-xs text-[#A1A1AA]">
          <Filter className="w-3.5 h-3.5 text-[#C084FC]" />
          <span>Type:</span>
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="px-2.5 py-1 rounded-md bg-[#191225] border border-[#30203F] text-xs text-white focus:outline-none focus:border-[#A855F7]"
          >
            <option value="all">All Task Types</option>
            <option value="study">Conceptual Study</option>
            <option value="revision">Spaced Revision</option>
            <option value="quiz">Practice Quizzes</option>
            <option value="career_project">Career Milestones</option>
            <option value="exam_prep">Exam Prep</option>
          </select>
        </div>
      </div>

      {/* Grouped Day-by-Day Timeline */}
      {plan && (
        <div className="space-y-6">
          {datesSorted.map((dateStr) => {
            const dayTasks = tasksByDate[dateStr];
            const isToday = dateStr === todayStr;
            const isPast = dateStr < todayStr;

            return (
              <div key={dateStr} className="space-y-3">
                <div className="flex items-center justify-between text-xs font-bold text-[#C084FC] uppercase tracking-wider">
                  <div className="flex items-center gap-2">
                    <Calendar className="w-3.5 h-3.5" />
                    <span>{dateStr}</span>
                    {isToday && (
                      <span className="px-2 py-0.5 rounded bg-[#8B5CF6] text-white text-[10px] font-extrabold lowercase">
                        today
                      </span>
                    )}
                    {isPast && (
                      <span className="text-[10px] text-gray-500 font-normal">
                        (past date)
                      </span>
                    )}
                  </div>
                  <span className="text-[11px] text-[#A1A1AA] font-normal lowercase">
                    {dayTasks.length} {dayTasks.length === 1 ? "task" : "tasks"}
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {dayTasks.map((task) => {
                    const isTaskOverdue = task.is_overdue && !task.is_completed;

                    return (
                      <GlowCard
                        key={task.id}
                        className={`p-4 transition-all flex flex-col justify-between ${
                          task.is_completed
                            ? "border-emerald-500/40 bg-[#120D1C]/60 opacity-80"
                            : isTaskOverdue
                            ? "border-red-500/40 bg-[#1a0f18]/60"
                            : ""
                        }`}
                      >
                        <div>
                          {/* Header row with task type & priority badges */}
                          <div className="flex items-start justify-between gap-2 border-b border-[#30203F]/40 pb-2.5 mb-2.5">
                            <div className="flex items-center gap-1.5 flex-wrap">
                              {/* Task Type badge */}
                              <span
                                className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded ${
                                  task.task_type === "quiz"
                                    ? "bg-blue-500/20 text-blue-300 border border-blue-500/30"
                                    : task.task_type === "revision"
                                    ? "bg-amber-500/20 text-amber-300 border border-amber-500/30"
                                    : task.task_type === "career_project"
                                    ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                                    : task.task_type === "exam_prep"
                                    ? "bg-red-500/20 text-red-300 border border-red-500/30"
                                    : "bg-purple-500/20 text-[#C084FC] border border-purple-500/30"
                                }`}
                              >
                                {task.task_type === "quiz"
                                  ? "Practice Quiz"
                                  : task.task_type === "revision"
                                  ? "Spaced Revision"
                                  : task.task_type === "career_project"
                                  ? "Career Milestone"
                                  : task.task_type === "exam_prep"
                                  ? "Exam Prep"
                                  : "Conceptual Study"}
                              </span>

                              {/* Priority badge */}
                              <span
                                className={`text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded ${
                                  task.priority === "High"
                                    ? "bg-red-900/30 text-red-300 border border-red-500/20"
                                    : "bg-gray-800/40 text-gray-400 border border-gray-700/30"
                                }`}
                              >
                                {task.priority} Priority
                              </span>

                              {isTaskOverdue && (
                                <span className="text-[10px] font-bold text-red-400 bg-red-950/40 px-1.5 py-0.5 rounded border border-red-500/30">
                                  Overdue
                                </span>
                              )}
                            </div>

                            {/* Duration & Edit controls */}
                            <div className="flex items-center gap-1.5 shrink-0">
                              <span className="text-[11px] text-[#A1A1AA] flex items-center gap-1">
                                <Clock className="w-3 h-3 text-[#A855F7]" />
                                {task.duration_minutes}m
                              </span>

                              <button
                                onClick={() => setEditingTask(task)}
                                className="p-1 rounded text-[#A1A1AA] hover:text-white hover:bg-[#191225]"
                                title="Edit Task"
                              >
                                <Edit3 className="w-3 h-3" />
                              </button>

                              <button
                                onClick={() => handleDeleteTask(task.id)}
                                className="p-1 rounded text-[#A1A1AA] hover:text-red-400 hover:bg-red-950/30"
                                title="Delete Task"
                              >
                                <Trash2 className="w-3 h-3" />
                              </button>
                            </div>
                          </div>

                          {/* Task Checkbox & Content */}
                          <div className="flex items-start gap-2.5">
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
                              <h4
                                className={`text-xs font-bold leading-snug ${
                                  task.is_completed ? "line-through text-gray-500" : "text-white"
                                }`}
                              >
                                {task.title}
                              </h4>
                              {task.description && (
                                <p className="text-[11px] text-[#A1A1AA] mt-1 leading-relaxed">
                                  {task.description}
                                </p>
                              )}
                              {task.notes && (
                                <div className="text-[10px] text-[#D8B4FE] mt-1.5 italic bg-[#100B18] p-1.5 rounded border border-[#30203F]/40">
                                  {task.notes}
                                </div>
                              )}
                            </div>
                          </div>
                        </div>

                        {/* Card Footer: Deep Links & Reschedule */}
                        <div className="mt-3 pt-2.5 border-t border-[#30203F]/40 flex items-center justify-between gap-2 text-xs">
                          {/* Module Integration Deep Link Button */}
                          <div>
                            {task.action_url ? (
                              <Link
                                href={task.action_url}
                                className="inline-flex items-center gap-1 text-[11px] font-semibold text-[#C084FC] hover:text-white transition-colors"
                              >
                                {task.task_type === "quiz" ? (
                                  <>Launch Assessment <ArrowRight className="w-3 h-3" /></>
                                ) : task.task_type === "career_project" ? (
                                  <>View Career Milestone <ArrowRight className="w-3 h-3" /></>
                                ) : (
                                  <>Open Smart Notes <ArrowRight className="w-3 h-3" /></>
                                )}
                              </Link>
                            ) : (
                              <span className="text-[10px] text-[#A1A1AA]">Curriculum Task</span>
                            )}
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

                        {/* Inline Reschedule date picker */}
                        {rescheduleTaskId === task.id && (
                          <div className="mt-2.5 pt-2 border-t border-[#30203F] flex items-center gap-2">
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
                              Save
                            </button>
                            <button
                              onClick={() => setRescheduleTaskId(null)}
                              className="px-2 py-1 text-xs text-[#A1A1AA] hover:text-white"
                            >
                              Cancel
                            </button>
                          </div>
                        )}
                      </GlowCard>
                    );
                  })}
                </div>
              </div>
            );
          })}

          {filteredTasks.length === 0 && (
            <div className="text-center py-12 text-xs text-[#A1A1AA]">
              No study tasks found matching the selected filter.
            </div>
          )}
        </div>
      )}

      {/* Adaptive Plan Settings Modal */}
      {showConfigModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#120B1C] border border-[#30203F] rounded-2xl w-full max-w-lg overflow-hidden shadow-2xl animate-in fade-in zoom-in-95">
            <div className="p-4 border-b border-[#30203F] flex items-center justify-between">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-[#C084FC]" /> Configure Adaptive Study Plan
              </h3>
              <button
                onClick={() => setShowConfigModal(false)}
                className="text-[#A1A1AA] hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleGeneratePlan} className="p-5 space-y-4 text-xs">
              <div>
                <label className="block text-[#A1A1AA] mb-1 font-semibold">Plan Title</label>
                <input
                  type="text"
                  value={genTitle}
                  onChange={(e) => setGenTitle(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-[#191225] border border-[#30203F] text-white focus:outline-none focus:border-[#A855F7]"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[#A1A1AA] mb-1 font-semibold">Daily Study Time</label>
                  <select
                    value={genDailyHours}
                    onChange={(e) => setGenDailyHours(Number(e.target.value))}
                    className="w-full px-3 py-2 rounded-lg bg-[#191225] border border-[#30203F] text-white focus:outline-none focus:border-[#A855F7]"
                  >
                    <option value={1.0}>1.0 hour / day</option>
                    <option value={1.5}>1.5 hours / day</option>
                    <option value={2.0}>2.0 hours / day</option>
                    <option value={3.0}>3.0 hours / day</option>
                    <option value={4.0}>4.0 hours / day</option>
                  </select>
                </div>

                <div>
                  <label className="block text-[#A1A1AA] mb-1 font-semibold">Plan Duration</label>
                  <select
                    value={genDurationDays}
                    onChange={(e) => setGenDurationDays(Number(e.target.value))}
                    className="w-full px-3 py-2 rounded-lg bg-[#191225] border border-[#30203F] text-white focus:outline-none focus:border-[#A855F7]"
                  >
                    <option value={7}>7 Days (1 Week Sprint)</option>
                    <option value={14}>14 Days (2 Weeks Standard)</option>
                    <option value={21}>21 Days (3 Weeks Intensive)</option>
                    <option value={30}>30 Days (1 Month Program)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-[#A1A1AA] mb-1 font-semibold">
                  Target Exam Date <span className="text-[#A1A1AA]/60">(Optional countdown pacing)</span>
                </label>
                <input
                  type="date"
                  value={genExamDate}
                  onChange={(e) => setGenExamDate(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-[#191225] border border-[#30203F] text-white focus:outline-none focus:border-[#A855F7]"
                />
              </div>

              <div>
                <label className="block text-[#A1A1AA] mb-1 font-semibold">Learning Priority</label>
                <select
                  value={genPriority}
                  onChange={(e) => setGenPriority(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-[#191225] border border-[#30203F] text-white focus:outline-none focus:border-[#A855F7]"
                >
                  <option value="weak_topics_first">Weak Topics First (Prioritize Low Quiz Scores)</option>
                  <option value="exam_prep">Exam Preparation Sprint (Fast Mock Pacing)</option>
                  <option value="career_skills">Career Roadmap Alignment (Industry Skills)</option>
                  <option value="balanced">Balanced Curriculum Coverage</option>
                </select>
              </div>

              <div className="space-y-2 pt-2 border-t border-[#30203F]/60">
                <label className="flex items-center gap-2 cursor-pointer text-white">
                  <input
                    type="checkbox"
                    checked={genIncludeRevision}
                    onChange={(e) => setGenIncludeRevision(e.target.checked)}
                    className="rounded bg-[#191225] border-[#30203F] text-[#8B5CF6] focus:ring-0"
                  />
                  <span>Include Spaced Revision sessions (2-3 days after study)</span>
                </label>

                <label className="flex items-center gap-2 cursor-pointer text-white">
                  <input
                    type="checkbox"
                    checked={genIncludeQuizzes}
                    onChange={(e) => setGenIncludeQuizzes(e.target.checked)}
                    className="rounded bg-[#191225] border-[#30203F] text-[#8B5CF6] focus:ring-0"
                  />
                  <span>Include Diagnostic Practice Quizzes with deep links</span>
                </label>
              </div>

              <div className="flex justify-end gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setShowConfigModal(false)}
                  className="px-3 py-2 rounded-lg text-xs font-semibold text-[#A1A1AA] hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={generating}
                  className="px-4 py-2 rounded-lg text-xs font-bold bg-[#8B5CF6] hover:bg-[#7C3AED] text-white shadow-md disabled:opacity-50 transition-colors"
                >
                  {generating ? "Synthesizing Schedule..." : "Generate Adaptive Plan"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Custom Task Modal */}
      {showAddTaskModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#120B1C] border border-[#30203F] rounded-2xl w-full max-w-md overflow-hidden shadow-2xl">
            <div className="p-4 border-b border-[#30203F] flex items-center justify-between">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Plus className="w-4 h-4 text-[#C084FC]" /> Add Custom Study Task
              </h3>
              <button
                onClick={() => setShowAddTaskModal(false)}
                className="text-[#A1A1AA] hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleCreateTask} className="p-5 space-y-3.5 text-xs">
              <div>
                <label className="block text-[#A1A1AA] mb-1 font-semibold">Task Title</label>
                <input
                  type="text"
                  value={newTaskTitle}
                  onChange={(e) => setNewTaskTitle(e.target.value)}
                  placeholder="e.g. Solve 10 SQL Subquery Exercises"
                  className="w-full px-3 py-2 rounded-lg bg-[#191225] border border-[#30203F] text-white focus:outline-none focus:border-[#A855F7]"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[#A1A1AA] mb-1 font-semibold">Scheduled Date</label>
                  <input
                    type="date"
                    value={newTaskDate}
                    onChange={(e) => setNewTaskDate(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-[#191225] border border-[#30203F] text-white focus:outline-none focus:border-[#A855F7]"
                    required
                  />
                </div>

                <div>
                  <label className="block text-[#A1A1AA] mb-1 font-semibold">Duration (minutes)</label>
                  <input
                    type="number"
                    min={10}
                    max={240}
                    value={newTaskDuration}
                    onChange={(e) => setNewTaskDuration(Number(e.target.value))}
                    className="w-full px-3 py-2 rounded-lg bg-[#191225] border border-[#30203F] text-white focus:outline-none focus:border-[#A855F7]"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[#A1A1AA] mb-1 font-semibold">Task Type</label>
                  <select
                    value={newTaskType}
                    onChange={(e) => setNewTaskType(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-[#191225] border border-[#30203F] text-white focus:outline-none focus:border-[#A855F7]"
                  >
                    <option value="study">Conceptual Study</option>
                    <option value="revision">Spaced Revision</option>
                    <option value="quiz">Practice Quiz</option>
                    <option value="career_project">Career Project</option>
                  </select>
                </div>

                <div>
                  <label className="block text-[#A1A1AA] mb-1 font-semibold">Priority</label>
                  <select
                    value={newTaskPriority}
                    onChange={(e) => setNewTaskPriority(e.target.value as "High" | "Medium" | "Low")}
                    className="w-full px-3 py-2 rounded-lg bg-[#191225] border border-[#30203F] text-white focus:outline-none focus:border-[#A855F7]"
                  >
                    <option value="High">High</option>
                    <option value="Medium">Medium</option>
                    <option value="Low">Low</option>
                  </select>
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setShowAddTaskModal(false)}
                  className="px-3 py-2 rounded-lg text-xs font-semibold text-[#A1A1AA] hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creatingTask}
                  className="px-4 py-2 rounded-lg text-xs font-bold bg-[#8B5CF6] hover:bg-[#7C3AED] text-white shadow-md disabled:opacity-50 transition-colors"
                >
                  {creatingTask ? "Adding..." : "Add to Schedule"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Task Modal */}
      {editingTask && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#120B1C] border border-[#30203F] rounded-2xl w-full max-w-md overflow-hidden shadow-2xl">
            <div className="p-4 border-b border-[#30203F] flex items-center justify-between">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Edit3 className="w-4 h-4 text-[#C084FC]" /> Edit Study Task
              </h3>
              <button
                onClick={() => setEditingTask(null)}
                className="text-[#A1A1AA] hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleSaveEditTask} className="p-5 space-y-3.5 text-xs">
              <div>
                <label className="block text-[#A1A1AA] mb-1 font-semibold">Title</label>
                <input
                  type="text"
                  value={editingTask.title}
                  onChange={(e) => setEditingTask({ ...editingTask, title: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-[#191225] border border-[#30203F] text-white focus:outline-none focus:border-[#A855F7]"
                  required
                />
              </div>

              <div>
                <label className="block text-[#A1A1AA] mb-1 font-semibold">Description / Notes</label>
                <textarea
                  value={editingTask.description || ""}
                  onChange={(e) => setEditingTask({ ...editingTask, description: e.target.value })}
                  rows={2}
                  className="w-full px-3 py-2 rounded-lg bg-[#191225] border border-[#30203F] text-white focus:outline-none focus:border-[#A855F7]"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[#A1A1AA] mb-1 font-semibold">Date</label>
                  <input
                    type="date"
                    value={editingTask.scheduled_date}
                    onChange={(e) => setEditingTask({ ...editingTask, scheduled_date: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg bg-[#191225] border border-[#30203F] text-white focus:outline-none focus:border-[#A855F7]"
                    required
                  />
                </div>

                <div>
                  <label className="block text-[#A1A1AA] mb-1 font-semibold">Duration (min)</label>
                  <input
                    type="number"
                    min={10}
                    max={240}
                    value={editingTask.duration_minutes}
                    onChange={(e) => setEditingTask({ ...editingTask, duration_minutes: Number(e.target.value) })}
                    className="w-full px-3 py-2 rounded-lg bg-[#191225] border border-[#30203F] text-white focus:outline-none focus:border-[#A855F7]"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[#A1A1AA] mb-1 font-semibold">Priority</label>
                  <select
                    value={editingTask.priority}
                    onChange={(e) => setEditingTask({ ...editingTask, priority: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg bg-[#191225] border border-[#30203F] text-white focus:outline-none focus:border-[#A855F7]"
                  >
                    <option value="High">High</option>
                    <option value="Medium">Medium</option>
                    <option value="Low">Low</option>
                  </select>
                </div>

                <div>
                  <label className="block text-[#A1A1AA] mb-1 font-semibold">Task Type</label>
                  <select
                    value={editingTask.task_type || "study"}
                    onChange={(e) => setEditingTask({ ...editingTask, task_type: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg bg-[#191225] border border-[#30203F] text-white focus:outline-none focus:border-[#A855F7]"
                  >
                    <option value="study">Conceptual Study</option>
                    <option value="revision">Spaced Revision</option>
                    <option value="quiz">Practice Quiz</option>
                    <option value="career_project">Career Project</option>
                  </select>
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setEditingTask(null)}
                  className="px-3 py-2 rounded-lg text-xs font-semibold text-[#A1A1AA] hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg text-xs font-bold bg-[#8B5CF6] hover:bg-[#7C3AED] text-white shadow-md transition-colors"
                >
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
