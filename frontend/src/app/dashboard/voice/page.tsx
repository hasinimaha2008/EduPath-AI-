"use client";

import React, { useState, useEffect } from "react";
import {
  Mic,
  MicOff,
  Square,
  Sparkles,
  Volume2,
  VolumeX,
  Languages,
  BookOpen,
  MessageSquare,
  RotateCcw,
  Radio,
  Sliders,
  ChevronRight,
  AlertCircle,
  Headphones,
  Check,
  Zap
} from "lucide-react";
import { GlowCard } from "@/components/GlowCard";
import { useVoiceAgent, SupportedLanguage } from "@/lib/useVoiceAgent";
import { api } from "@/lib/api";
import { Subject } from "@/lib/types";

export default function VoiceAgentPage() {
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [showTranscript, setShowTranscript] = useState<boolean>(true);
  const [showSettings, setShowSettings] = useState<boolean>(false);

  const {
    state,
    errorMessage,
    language,
    setLanguage,
    selectedSubjectId,
    setSelectedSubjectId,
    continuousMode,
    setContinuousMode,
    interimTranscript,
    finalTranscript,
    turns,
    audioVolume,
    isMuted,
    availableVoices,
    selectedVoiceId,
    setSelectedVoiceId,
    startConversation,
    stopConversation,
    toggleMute,
    interruptAi,
    clearSession,
  } = useVoiceAgent();

  // Load 16 Subjects for subject-scoped voice mentoring
  useEffect(() => {
    async function loadSubjects() {
      try {
        const subs = await api.getSubjects();
        setSubjects(subs);
      } catch (err) {
        console.warn("Could not load subjects for voice agent:", err);
      }
    }
    loadSubjects();
  }, []);

  const currentSubject = subjects.find((s) => s.id === selectedSubjectId);

  // Dynamic visualizer scale based on real-time volume
  const volumeScale = 1 + (audioVolume / 100) * 0.45;
  const outerRippleScale = 1 + (audioVolume / 100) * 0.85;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-white flex items-center gap-2">
              <Headphones className="w-5 h-5 text-[#C084FC]" /> Conversational AI Voice Agent
            </h1>
            <span className="px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider rounded-full bg-[#8B5CF6]/20 border border-[#8B5CF6]/50 text-[#C084FC] flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-[#A855F7] animate-ping" />
              Live Voice Mode
            </span>
          </div>
          <p className="text-xs text-[#A1A1AA] mt-0.5">
            Real-time, natural human-like voice conversations. Speak naturally, ask follow-up questions, and learn interactively.
          </p>
        </div>

        {/* Quick Toolbar */}
        <div className="flex items-center gap-2">
          {/* Language Selector */}
          <div className="relative">
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value as SupportedLanguage)}
              className="bg-[#191225] text-xs text-white border border-[#30203F] rounded-xl px-3 py-1.5 focus:outline-none focus:border-[#8B5CF6] transition-colors cursor-pointer"
            >
              <option value="en">English (US / Global)</option>
              <option value="en-IN">Indian English</option>
              <option value="te">తెలుగు (Telugu)</option>
              <option value="hi">हिन्दी (Hindi)</option>
              <option value="ta">தமிழ் (Tamil)</option>
              <option value="kn">ಕನ್ನಡ (Kannada)</option>
              <option value="ml">മലയാളം (Malayalam)</option>
              <option value="bn">বাংলা (Bengali)</option>
              <option value="mr">मराठी (Marathi)</option>
              <option value="ur">اردو (Urdu)</option>
              <option value="es">Español (Spanish)</option>
              <option value="fr">Français (French)</option>
              <option value="de">Deutsch (German)</option>
              <option value="ja">日本語 (Japanese)</option>
              <option value="zh">中文 (Mandarin)</option>
            </select>
          </div>

          {/* Subject Context Selector */}
          <div className="relative">
            <select
              value={selectedSubjectId || ""}
              onChange={(e) => setSelectedSubjectId(e.target.value || null)}
              className="bg-[#191225] text-xs text-white border border-[#30203F] rounded-xl px-3 py-1.5 focus:outline-none focus:border-[#8B5CF6] transition-colors cursor-pointer max-w-[180px] truncate"
            >
              <option value="">General Academic Context</option>
              {subjects.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </div>

          {/* Settings Toggle */}
          <button
            onClick={() => setShowSettings(!showSettings)}
            className={`p-2 rounded-xl border transition-colors ${
              showSettings
                ? "bg-[#8B5CF6]/20 border-[#8B5CF6] text-white"
                : "bg-[#191225] border-[#30203F] text-[#A1A1AA] hover:text-white"
            }`}
            title="Voice & Audio Settings"
          >
            <Sliders className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Error / Permission Banner */}
      {errorMessage && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-3 text-red-300 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
            <span>{errorMessage}</span>
          </div>
          <button
            onClick={startConversation}
            className="px-2.5 py-1 text-xs bg-red-500/20 hover:bg-red-500/30 rounded-lg text-red-200 transition-colors"
          >
            Try Again
          </button>
        </div>
      )}

      {/* Settings Drawer (Collapsible) */}
      {showSettings && (
        <GlowCard glow className="p-4 space-y-4">
          <div className="flex items-center justify-between border-b border-[#30203F] pb-2">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
              <Sliders className="w-3.5 h-3.5 text-[#C084FC]" /> Voice Agent Preferences
            </h3>
            <button
              onClick={() => setShowSettings(false)}
              className="text-xs text-[#A1A1AA] hover:text-white"
            >
              Close
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
            {/* Neural Voice Model */}
            <div>
              <label className="text-[#A1A1AA] block mb-1">Neural Voice Model</label>
              <select
                value={selectedVoiceId}
                onChange={(e) => setSelectedVoiceId(e.target.value)}
                className="w-full bg-[#100B18] text-white border border-[#30203F] rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-[#8B5CF6]"
              >
                {availableVoices.map((v) => (
                  <option key={v.id} value={v.id}>
                    {v.name} ({v.gender})
                  </option>
                ))}
              </select>
            </div>

            {/* Continuous Mode */}
            <div>
              <label className="text-[#A1A1AA] block mb-1">Continuous Mode (Hands-Free)</label>
              <div className="flex items-center gap-2 mt-1">
                <input
                  type="checkbox"
                  id="continuous"
                  checked={continuousMode}
                  onChange={(e) => setContinuousMode(e.target.checked)}
                  className="rounded border-[#30203F] text-[#8B5CF6] focus:ring-[#8B5CF6]"
                />
                <label htmlFor="continuous" className="text-white cursor-pointer select-none">
                  Auto-listen after AI answers
                </label>
              </div>
            </div>

            {/* Clear Session */}
            <div>
              <label className="text-[#A1A1AA] block mb-1">Session Management</label>
              <button
                onClick={clearSession}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-[#100B18] hover:bg-[#30203F] text-[#A1A1AA] hover:text-white rounded-lg border border-[#30203F] transition-colors"
              >
                <RotateCcw className="w-3.5 h-3.5" /> Clear Context & History
              </button>
            </div>
          </div>
        </GlowCard>
      )}

      {/* Main Voice Mode Stage */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Central Voice Orb & Live Stage */}
        <div className={`space-y-6 ${showTranscript ? "lg:col-span-2" : "lg:col-span-3"}`}>
          <GlowCard glow className="relative p-8 min-h-[480px] flex flex-col items-center justify-between overflow-hidden">
            {/* Background Ambient Glow */}
            <div className="absolute inset-0 bg-radial-gradient from-[#8B5CF6]/15 via-transparent to-transparent pointer-events-none" />

            {/* Subject Context Header Badge */}
            <div className="w-full flex items-center justify-between text-xs text-[#A1A1AA] z-10">
              <span className="flex items-center gap-1.5">
                <BookOpen className="w-3.5 h-3.5 text-[#C084FC]" />
                {currentSubject ? (
                  <span>
                    Focus: <strong className="text-white">{currentSubject.name}</strong> ({currentSubject.code || "Academic"})
                  </span>
                ) : (
                  <span>Focus: <strong className="text-white">All Computer Science Subjects</strong></span>
                )}
              </span>

              <span className="flex items-center gap-2">
                <Languages className="w-3.5 h-3.5 text-[#A855F7]" />
                <span className="text-white font-medium">
                  {language === "en" ? "English" : language === "hi" ? "हिंदी (Hindi)" : "తెలుగు (Telugu)"}
                </span>
              </span>
            </div>

            {/* Central Animated Orb Visualizer (ChatGPT Voice Mode Style) */}
            <div className="relative my-auto flex items-center justify-center py-10 z-10">
              {/* Outer Pulsing Sound Waves (when speaking or listening) */}
              {(state === "listening" || state === "speaking") && (
                <>
                  <div
                    className="absolute w-64 h-64 rounded-full border border-[#8B5CF6]/30 bg-[#8B5CF6]/5 transition-transform duration-75 ease-out"
                    style={{ transform: `scale(${outerRippleScale})` }}
                  />
                  <div
                    className="absolute w-80 h-80 rounded-full border border-[#C084FC]/20 transition-transform duration-150 ease-out"
                    style={{ transform: `scale(${outerRippleScale * 1.15})` }}
                  />
                </>
              )}

              {/* Glowing Aura Filter */}
              <div
                className={`absolute w-52 h-52 rounded-full blur-2xl transition-all duration-300 ${
                  state === "listening"
                    ? "bg-cyan-500/25 scale-110"
                    : state === "thinking"
                    ? "bg-purple-600/40 animate-pulse scale-105"
                    : state === "speaking"
                    ? "bg-[#C084FC]/35 scale-125"
                    : "bg-[#8B5CF6]/15 scale-90"
                }`}
              />

              {/* The Core Interactive Orb */}
              <div
                onClick={state === "idle" ? startConversation : state === "speaking" ? interruptAi : stopConversation}
                className={`relative w-44 h-44 rounded-full cursor-pointer flex items-center justify-center shadow-2xl transition-all duration-200 select-none ${
                  state === "listening"
                    ? "bg-gradient-to-br from-[#8B5CF6] via-[#A855F7] to-cyan-400 shadow-[0_0_50px_rgba(139,92,246,0.6)]"
                    : state === "thinking"
                    ? "bg-gradient-to-tr from-[#6D28D9] via-[#8B5CF6] to-[#C084FC] animate-spin shadow-[0_0_40px_rgba(168,85,247,0.5)]"
                    : state === "speaking"
                    ? "bg-gradient-to-br from-[#7C3AED] via-[#C084FC] to-[#D8B4FE] shadow-[0_0_60px_rgba(192,132,252,0.7)]"
                    : "bg-gradient-to-br from-[#191225] to-[#30203F] border-2 border-[#8B5CF6]/40 hover:border-[#8B5CF6] shadow-[0_0_25px_rgba(139,92,246,0.2)]"
                }`}
                style={{
                  transform: state === "listening" || state === "speaking" ? `scale(${volumeScale})` : "scale(1)",
                }}
                title={
                  state === "idle"
                    ? "Click to Start Speaking"
                    : state === "speaking"
                    ? "Click to Interrupt AI"
                    : "Click to Pause"
                }
              >
                {/* Center Icon in Orb */}
                {state === "idle" && (
                  <Mic className="w-12 h-12 text-[#C084FC] transition-transform hover:scale-110" />
                )}
                {state === "listening" && (
                  <div className="flex flex-col items-center">
                    <Radio className="w-10 h-10 text-white animate-pulse" />
                    <span className="text-[11px] font-bold tracking-wider uppercase text-white mt-1">Listening</span>
                  </div>
                )}
                {state === "thinking" && (
                  <Sparkles className="w-10 h-10 text-white animate-pulse" />
                )}
                {state === "speaking" && (
                  <div className="flex flex-col items-center">
                    <Volume2 className="w-10 h-10 text-white animate-bounce" />
                    <span className="text-[11px] font-bold tracking-wider uppercase text-white mt-1">Speaking</span>
                  </div>
                )}
              </div>
            </div>

            {/* Live State Label & Action Hints */}
            <div className="w-full text-center space-y-3 z-10">
              {/* Dynamic Status Text */}
              <div className="text-sm font-semibold text-white">
                {state === "idle" && "Tap the glowing orb or microphone to start speaking"}
                {state === "listening" && "Listening to you... speak naturally"}
                {state === "thinking" && "EduPath AI is formulating your response..."}
                {state === "speaking" && "EduPath AI is speaking — tap to interrupt anytime"}
                {state === "error" && "Voice mode encountered an error. Click below to retry."}
              </div>

              {/* Real-time Subtitle / Live Transcript Display */}
              <div className="min-h-[44px] max-w-xl mx-auto px-4 py-2 rounded-xl bg-[#100B18]/80 border border-[#30203F] text-xs text-[#E4E4E7] flex items-center justify-center text-center">
                {interimTranscript ? (
                  <span className="italic text-[#C084FC] animate-pulse">
                    &ldquo;{interimTranscript}&rdquo;
                  </span>
                ) : finalTranscript ? (
                  <span className="text-[#A1A1AA]">
                    Last spoken: <strong className="text-white">&ldquo;{finalTranscript}&rdquo;</strong>
                  </span>
                ) : (
                  <span className="text-[#71717A]">
                    {state === "listening"
                      ? "Speak your question (e.g. 'Explain virtual memory' or 'Give me an example')..."
                      : "Your voice transcription will appear here in real time"}
                  </span>
                )}
              </div>

              {/* Control Action Bar */}
              <div className="flex items-center justify-center gap-3 pt-2">
                {state === "idle" ? (
                  <button
                    onClick={startConversation}
                    className="flex items-center gap-2 px-6 py-2.5 rounded-full bg-gradient-to-r from-[#8B5CF6] to-[#A855F7] text-white text-xs font-bold hover:shadow-[0_0_25px_rgba(139,92,246,0.6)] transition-all hover:scale-105"
                  >
                    <Mic className="w-4 h-4" /> Start Voice Conversation
                  </button>
                ) : (
                  <>
                    {/* Interrupt Button (Barge-in) */}
                    {state === "speaking" && (
                      <button
                        onClick={interruptAi}
                        className="flex items-center gap-1.5 px-4 py-2 rounded-full bg-amber-500/20 border border-amber-500/40 text-amber-300 text-xs font-bold hover:bg-amber-500/30 transition-all"
                        title="Interrupt AI speaking and talk immediately"
                      >
                        <Zap className="w-3.5 h-3.5 text-amber-400" /> Interrupt AI
                      </button>
                    )}

                    {/* Mute/Unmute Mic */}
                    <button
                      onClick={toggleMute}
                      className={`p-2.5 rounded-full border transition-colors ${
                        isMuted
                          ? "bg-red-500/20 border-red-500/50 text-red-300"
                          : "bg-[#191225] border-[#30203F] text-white hover:border-[#8B5CF6]"
                      }`}
                      title={isMuted ? "Unmute Microphone" : "Mute Microphone"}
                    >
                      {isMuted ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                    </button>

                    {/* Stop Conversation */}
                    <button
                      onClick={stopConversation}
                      className="flex items-center gap-1.5 px-4 py-2 rounded-full bg-red-500/20 border border-red-500/40 text-red-300 text-xs font-bold hover:bg-red-500/30 transition-all"
                    >
                      <Square className="w-3.5 h-3.5 fill-current" /> End Call
                    </button>
                  </>
                )}

                {/* Toggle Transcript Drawer Button */}
                <button
                  onClick={() => setShowTranscript(!showTranscript)}
                  className={`p-2.5 rounded-full border transition-colors ${
                    showTranscript
                      ? "bg-[#8B5CF6]/20 border-[#8B5CF6] text-white"
                      : "bg-[#191225] border-[#30203F] text-[#A1A1AA] hover:text-white"
                  }`}
                  title={showTranscript ? "Hide Conversation History" : "Show Conversation History"}
                >
                  <MessageSquare className="w-4 h-4" />
                </button>
              </div>
            </div>
          </GlowCard>

          {/* Quick Prompts to Speak */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {[
              {
                title: "Concept Explanation",
                desc: "Explain machine learning with a real-life analogy.",
              },
              {
                title: "Follow-Up Questions",
                desc: "Can you give me another example of that?",
              },
              {
                title: "Technical Interview Prep",
                desc: "Ask me an interview question on operating systems.",
              },
            ].map((p, idx) => (
              <button
                key={idx}
                onClick={() => {
                  if (state === "idle") {
                    startConversation();
                  }
                }}
                className="p-3 text-left bg-[#100B18] border border-[#30203F] hover:border-[#8B5CF6]/50 rounded-xl transition-all group"
              >
                <div className="text-xs font-bold text-white group-hover:text-[#C084FC] transition-colors flex items-center justify-between">
                  <span>{p.title}</span>
                  <ChevronRight className="w-3.5 h-3.5 text-[#71717A] group-hover:text-[#C084FC] transition-colors" />
                </div>
                <p className="text-[11px] text-[#A1A1AA] mt-1 italic">&ldquo;{p.desc}&rdquo;</p>
              </button>
            ))}
          </div>
        </div>

        {/* Live Conversation Transcript Drawer */}
        {showTranscript && (
          <GlowCard glow className="p-4 flex flex-col h-[580px] space-y-3">
            <div className="flex items-center justify-between border-b border-[#30203F] pb-2">
              <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
                <MessageSquare className="w-3.5 h-3.5 text-[#C084FC]" /> Spoken Conversation Flow
              </h3>
              <span className="text-[10px] text-[#A1A1AA] bg-[#100B18] px-2 py-0.5 rounded-full border border-[#30203F]">
                {turns.length} turns
              </span>
            </div>

            {/* Transcript Messages List */}
            <div className="flex-1 overflow-y-auto space-y-3 pr-1">
              {turns.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-center p-6 text-[#71717A] space-y-2">
                  <Headphones className="w-8 h-8 text-[#30203F]" />
                  <p className="text-xs text-[#A1A1AA]">No spoken turns yet.</p>
                  <p className="text-[11px]">Click the microphone or glowing orb and ask an academic question to start chatting!</p>
                </div>
              ) : (
                turns.map((t, idx) => (
                  <div
                    key={idx}
                    className={`p-3 rounded-xl text-xs space-y-1 ${
                      t.role === "user"
                        ? "bg-[#8B5CF6]/15 border border-[#8B5CF6]/30 ml-4 text-white"
                        : "bg-[#100B18] border border-[#30203F] mr-4 text-[#E4E4E7]"
                    }`}
                  >
                    <div className="flex items-center justify-between text-[10px] font-semibold text-[#A1A1AA]">
                      <span className={t.role === "user" ? "text-[#C084FC]" : "text-[#A855F7]"}>
                        {t.role === "user" ? "You (Spoken)" : "EduPath AI Tutor"}
                      </span>
                      <span>Turn #{idx + 1}</span>
                    </div>
                    <p className="leading-relaxed">{t.content}</p>
                  </div>
                ))
              )}
            </div>

            {/* Clear Transcript Button */}
            {turns.length > 0 && (
              <div className="pt-2 border-t border-[#30203F] flex justify-end">
                <button
                  onClick={clearSession}
                  className="text-[11px] text-[#A1A1AA] hover:text-white flex items-center gap-1 transition-colors"
                >
                  <RotateCcw className="w-3 h-3" /> Clear Conversation
                </button>
              </div>
            )}
          </GlowCard>
        )}
      </div>
    </div>
  );
}
