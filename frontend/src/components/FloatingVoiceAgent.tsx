"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Mic,
  MicOff,
  Square,
  Sparkles,
  Volume2,
  X,
  Maximize2,
  Radio,
  Zap,
  Languages,
  RotateCcw
} from "lucide-react";
import { useVoiceAgent, SupportedLanguage } from "@/lib/useVoiceAgent";

export const FloatingVoiceAgent: React.FC = () => {
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);

  const {
    state,
    errorMessage,
    language,
    setLanguage,
    interimTranscript,
    finalTranscript,
    turns,
    audioVolume,
    isMuted,
    startConversation,
    stopConversation,
    toggleMute,
    interruptAi,
    clearSession,
  } = useVoiceAgent();

  // If user is already on the dedicated /dashboard/voice page, don't show the duplicate floating modal
  if (pathname === "/dashboard/voice") {
    return null;
  }

  const volumeScale = 1 + (audioVolume / 100) * 0.35;

  return (
    <div className="fixed bottom-6 right-6 z-50 select-none">
      {!isOpen ? (
        /* Minimized Floating Trigger Button */
        <button
          onClick={() => {
            setIsOpen(true);
            if (state === "idle") {
              startConversation();
            }
          }}
          className="relative group p-4 rounded-full bg-gradient-to-r from-[#8B5CF6] to-[#A855F7] text-white shadow-[0_0_25px_rgba(139,92,246,0.6)] hover:shadow-[0_0_35px_rgba(168,85,247,0.8)] transition-all hover:scale-105 active:scale-95"
          title="Start AI Voice Conversation"
        >
          {/* Subtle Outer Ping */}
          <span className="absolute inset-0 rounded-full bg-[#A855F7] opacity-40 animate-ping pointer-events-none" />
          <Mic className="w-6 h-6" />

          {/* Hover Tooltip */}
          <span className="absolute bottom-full right-0 mb-2 px-3 py-1 bg-[#191225] border border-[#30203F] text-white text-xs font-medium rounded-lg whitespace-nowrap shadow-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
            Voice AI Tutor (Talk Naturally)
          </span>
        </button>
      ) : (
        /* Floating Glassmorphic Voice Widget Modal */
        <div className="w-80 sm:w-96 rounded-2xl bg-[#100B18]/95 backdrop-blur-xl border border-[#30203F] shadow-[0_10px_40px_rgba(0,0,0,0.8),0_0_30px_rgba(139,92,246,0.25)] p-4 space-y-4 animate-in fade-in slide-in-from-bottom-5 duration-200">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-[#30203F] pb-2.5">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-[#A855F7] animate-pulse" />
              <h4 className="text-xs font-bold text-white uppercase tracking-wider">Voice AI Assistant</h4>
            </div>

            <div className="flex items-center gap-1">
              {/* Language Switcher */}
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value as SupportedLanguage)}
                className="bg-[#191225] text-[11px] text-[#C084FC] border border-[#30203F] rounded-lg px-2 py-0.5 focus:outline-none"
              >
                <option value="en">EN</option>
                <option value="en-IN">EN-IN</option>
                <option value="te">TE</option>
                <option value="hi">HI</option>
                <option value="ta">TA</option>
                <option value="kn">KN</option>
                <option value="ml">ML</option>
                <option value="bn">BN</option>
                <option value="mr">MR</option>
                <option value="ur">UR</option>
                <option value="es">ES</option>
                <option value="fr">FR</option>
                <option value="de">DE</option>
                <option value="ja">JA</option>
                <option value="zh">ZH</option>
              </select>

              {/* Expand to Fullpage */}
              <Link
                href="/dashboard/voice"
                onClick={() => setIsOpen(false)}
                className="p-1.5 text-[#A1A1AA] hover:text-white rounded-lg hover:bg-[#191225] transition-colors"
                title="Open Fullscreen Voice Mode"
              >
                <Maximize2 className="w-3.5 h-3.5" />
              </Link>

              {/* Close / Minimize */}
              <button
                onClick={() => {
                  stopConversation();
                  setIsOpen(false);
                }}
                className="p-1.5 text-[#A1A1AA] hover:text-white rounded-lg hover:bg-[#191225] transition-colors"
                title="Close"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Central Mini Animated Orb */}
          <div className="flex flex-col items-center justify-center py-4 space-y-3">
            <div
              onClick={state === "idle" ? startConversation : state === "speaking" ? interruptAi : stopConversation}
              className={`relative w-24 h-24 rounded-full cursor-pointer flex items-center justify-center transition-all duration-200 ${
                state === "listening"
                  ? "bg-gradient-to-br from-[#8B5CF6] via-[#A855F7] to-cyan-400 shadow-[0_0_30px_rgba(139,92,246,0.5)]"
                  : state === "thinking"
                  ? "bg-gradient-to-tr from-[#6D28D9] via-[#8B5CF6] to-[#C084FC] animate-spin shadow-[0_0_25px_rgba(168,85,247,0.4)]"
                  : state === "speaking"
                  ? "bg-gradient-to-br from-[#7C3AED] via-[#C084FC] to-[#D8B4FE] shadow-[0_0_35px_rgba(192,132,252,0.6)]"
                  : "bg-[#191225] border-2 border-[#8B5CF6]/40 hover:border-[#8B5CF6]"
              }`}
              style={{
                transform: state === "listening" || state === "speaking" ? `scale(${volumeScale})` : "scale(1)",
              }}
            >
              {state === "idle" && <Mic className="w-8 h-8 text-[#C084FC]" />}
              {state === "listening" && <Radio className="w-8 h-8 text-white animate-pulse" />}
              {state === "thinking" && <Sparkles className="w-8 h-8 text-white animate-pulse" />}
              {state === "speaking" && <Volume2 className="w-8 h-8 text-white animate-bounce" />}
            </div>

            <p className="text-[11px] font-medium text-white text-center">
              {state === "idle" && "Tap orb or mic to speak"}
              {state === "listening" && "Listening to you..."}
              {state === "thinking" && "EduPath AI is thinking..."}
              {state === "speaking" && "Speaking — tap to interrupt"}
              {state === "error" && "Microphone or network error"}
            </p>
          </div>

          {/* Live Subtitle Transcript Banner */}
          <div className="min-h-[38px] p-2 rounded-xl bg-[#191225] border border-[#30203F] text-[11px] text-center text-[#E4E4E7] flex items-center justify-center">
            {interimTranscript ? (
              <span className="italic text-[#C084FC] line-clamp-2">&ldquo;{interimTranscript}&rdquo;</span>
            ) : finalTranscript ? (
              <span className="line-clamp-2 text-[#A1A1AA]">
                You: <strong className="text-white">&ldquo;{finalTranscript}&rdquo;</strong>
              </span>
            ) : turns.length > 0 && turns[turns.length - 1].role === "assistant" ? (
              <span className="line-clamp-2 text-[#C084FC]">
                AI: {turns[turns.length - 1].content}
              </span>
            ) : (
              <span className="text-[#71717A]">Speak naturally...</span>
            )}
          </div>

          {/* Controls Footer */}
          <div className="flex items-center justify-between pt-1 text-xs">
            {state === "idle" ? (
              <button
                onClick={startConversation}
                className="w-full flex items-center justify-center gap-1.5 py-2 rounded-xl bg-gradient-to-r from-[#8B5CF6] to-[#A855F7] text-white font-bold transition-transform active:scale-95"
              >
                <Mic className="w-3.5 h-3.5" /> Start Speaking
              </button>
            ) : (
              <div className="w-full flex items-center justify-between gap-2">
                {state === "speaking" && (
                  <button
                    onClick={interruptAi}
                    className="flex-1 flex items-center justify-center gap-1 py-1.5 rounded-xl bg-amber-500/20 border border-amber-500/40 text-amber-300 font-medium text-[11px]"
                  >
                    <Zap className="w-3 h-3 text-amber-400" /> Interrupt
                  </button>
                )}

                <button
                  onClick={toggleMute}
                  className={`p-2 rounded-xl border ${
                    isMuted
                      ? "bg-red-500/20 border-red-500/40 text-red-300"
                      : "bg-[#191225] border-[#30203F] text-white"
                  }`}
                  title={isMuted ? "Unmute" : "Mute"}
                >
                  {isMuted ? <MicOff className="w-3.5 h-3.5" /> : <Mic className="w-3.5 h-3.5" />}
                </button>

                <button
                  onClick={stopConversation}
                  className="flex-1 flex items-center justify-center gap-1 py-1.5 rounded-xl bg-red-500/20 border border-red-500/40 text-red-300 font-medium text-[11px]"
                >
                  <Square className="w-3 h-3 fill-current" /> Stop
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
