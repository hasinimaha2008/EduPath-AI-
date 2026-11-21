"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { api } from "./api";
import { VoiceChatTurn, VoiceInfo } from "./types";

export type VoiceState = "idle" | "listening" | "thinking" | "speaking" | "error";
export type SupportedLanguage = string;

export const LANGUAGE_BCP47: Record<string, string> = {
  en: "en-US",
  "en-IN": "en-IN",
  te: "te-IN",
  hi: "hi-IN",
  ta: "ta-IN",
  kn: "kn-IN",
  ml: "ml-IN",
  bn: "bn-IN",
  mr: "mr-IN",
  ur: "ur-IN",
  es: "es-ES",
  fr: "fr-FR",
  de: "de-DE",
  ja: "ja-JP",
  zh: "zh-CN"
};

export interface UseVoiceAgentOptions {
  initialSubjectId?: string;
  initialLanguage?: SupportedLanguage;
  continuousMode?: boolean;
}

export function useVoiceAgent(options: UseVoiceAgentOptions = {}) {
  const [state, setState] = useState<VoiceState>("idle");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [language, setLanguage] = useState<SupportedLanguage>(options.initialLanguage || "en");
  const [selectedSubjectId, setSelectedSubjectId] = useState<string | null>(options.initialSubjectId || null);
  const [continuousMode, setContinuousMode] = useState<boolean>(options.continuousMode ?? true);
  
  // Audio & Transcript States
  const [interimTranscript, setInterimTranscript] = useState<string>("");
  const [finalTranscript, setFinalTranscript] = useState<string>("");
  const [turns, setTurns] = useState<VoiceChatTurn[]>([]);
  const [audioVolume, setAudioVolume] = useState<number>(0);
  const [isMuted, setIsMuted] = useState<boolean>(false);
  const [availableVoices, setAvailableVoices] = useState<VoiceInfo[]>([]);
  const [selectedVoiceId, setSelectedVoiceId] = useState<string>("");

  // Refs for audio elements, recognition, and analyzers
  const recognitionRef = useRef<any>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const activeAudioRef = useRef<HTMLAudioElement | null>(null);
  const silenceTimerRef = useRef<NodeJS.Timeout | null>(null);
  const animFrameRef = useRef<number | null>(null);
  const isAiSpeakingRef = useRef<boolean>(false);
  const speechAccumulatorRef = useRef<string>("");
  const turnsRef = useRef<VoiceChatTurn[]>([]);
  const stateRef = useRef<VoiceState>("idle");

  // Keep ref synchronized with state
  useEffect(() => {
    turnsRef.current = turns;
  }, [turns]);

  useEffect(() => {
    stateRef.current = state;
  }, [state]);

  // Load available voices on mount
  useEffect(() => {
    async function loadVoices() {
      try {
        const vList = await api.getVoices();
        setAvailableVoices(vList);
        if (vList.length > 0) {
          const defaultV = vList.find((v) => v.language === language) || vList[0];
          setSelectedVoiceId(defaultV.id);
        }
      } catch (err) {
        console.warn("Could not load backend voices list:", err);
      }
    }
    loadVoices();
  }, [language]);

  // Audio level analysis loop
  const updateAudioLevels = useCallback(() => {
    if (!analyserRef.current) return;
    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
    analyserRef.current.getByteFrequencyData(dataArray);

    let sum = 0;
    for (let i = 0; i < dataArray.length; i++) {
      sum += dataArray[i];
    }
    const avg = sum / dataArray.length;
    // Normalize to 0-100 range
    setAudioVolume(Math.min(100, Math.round((avg / 128) * 100)));

    animFrameRef.current = requestAnimationFrame(updateAudioLevels);
  }, []);

  // Initialize Microphone & Web Audio Analyzer
  const initAudioStream = useCallback(async () => {
    if (mediaStreamRef.current) return mediaStreamRef.current;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });
      mediaStreamRef.current = stream;

      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      if (AudioCtx) {
        const ctx = new AudioCtx();
        audioContextRef.current = ctx;
        const source = ctx.createMediaStreamSource(stream);
        const analyser = ctx.createAnalyser();
        analyser.fftSize = 64;
        source.connect(analyser);
        analyserRef.current = analyser;
        updateAudioLevels();
      }
      return stream;
    } catch (err: any) {
      console.error("Microphone access error:", err);
      if (err.name === "NotAllowedError" || err.name === "PermissionDeniedError") {
        setErrorMessage("Microphone access was denied. Please allow microphone permissions in your browser.");
      } else {
        setErrorMessage("Could not connect to microphone. Please check your audio settings.");
      }
      setState("error");
      return null;
    }
  }, [updateAudioLevels]);

  // Stop Audio and AudioContext
  const cleanupAudio = useCallback(() => {
    if (animFrameRef.current) {
      cancelAnimationFrame(animFrameRef.current);
    }
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      mediaStreamRef.current = null;
    }
    if (audioContextRef.current && audioContextRef.current.state !== "closed") {
      audioContextRef.current.close().catch(() => {});
      audioContextRef.current = null;
    }
    analyserRef.current = null;
    setAudioVolume(0);
  }, []);

  // Interruption / Barge-in Handler
  const interruptAi = useCallback(() => {
    // Immediately stop active audio
    if (activeAudioRef.current) {
      activeAudioRef.current.pause();
      activeAudioRef.current.currentTime = 0;
      activeAudioRef.current = null;
    }
    // Cancel browser speech synthesis if active
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }
    isAiSpeakingRef.current = false;
  }, []);

  // Send student speech to AI and process spoken response
  const sendStudentMessage = useCallback(
    async (textToSend: string) => {
      if (!textToSend || !textToSend.trim()) return;

      const userText = textToSend.trim();
      setInterimTranscript("");
      setFinalTranscript(userText);
      speechAccumulatorRef.current = "";

      // Add student turn
      const updatedTurns = [...turnsRef.current, { role: "user" as const, content: userText }];
      setTurns(updatedTurns);
      setState("thinking");

      try {
        const response = await api.voiceChat({
          message: userText,
          conversation_id: conversationId || undefined,
          subject_id: selectedSubjectId || undefined,
          language,
          voice: selectedVoiceId || undefined,
          synthesize_audio: true,
          history: updatedTurns,
        });

        if (!conversationId && response.conversation_id) {
          setConversationId(response.conversation_id);
        }

        const aiReply = response.reply_text;
        const finalTurnList = [...updatedTurns, { role: "assistant" as const, content: aiReply }];
        setTurns(finalTurnList);

        // Play Spoken Audio
        setState("speaking");
        isAiSpeakingRef.current = true;

        if (response.audio_base64) {
          const audio = new Audio("data:audio/mp3;base64," + response.audio_base64);
          activeAudioRef.current = audio;

          audio.onended = () => {
            isAiSpeakingRef.current = false;
            activeAudioRef.current = null;
            if (continuousMode && stateRef.current !== "idle") {
              setState("listening");
            } else {
              setState("idle");
            }
          };

          audio.onerror = () => {
            console.warn("Base64 audio playback failed, falling back to Web Speech Synthesis");
            fallbackBrowserTts(aiReply, language, () => {
              isAiSpeakingRef.current = false;
              if (continuousMode && stateRef.current !== "idle") {
                setState("listening");
              } else {
                setState("idle");
              }
            });
          };

          await audio.play();
        } else {
          // Fallback to browser SpeechSynthesis
          fallbackBrowserTts(aiReply, language, () => {
            isAiSpeakingRef.current = false;
            if (continuousMode && stateRef.current !== "idle") {
              setState("listening");
            } else {
              setState("idle");
            }
          });
        }
      } catch (err: any) {
        console.error("Voice chat error:", err);
        setErrorMessage("Could not get AI response. Please check your connection and try speaking again.");
        setState("error");
        isAiSpeakingRef.current = false;
      }
    },
    [conversationId, selectedSubjectId, language, selectedVoiceId, continuousMode]
  );

  // Fallback browser speech synthesis
  const fallbackBrowserTts = (text: string, lang: SupportedLanguage, onDone: () => void) => {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) {
      onDone();
      return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = lang === "hi" ? "hi-IN" : lang === "te" ? "te-IN" : "en-US";
    utterance.rate = 1.0;
    utterance.pitch = 1.0;

    utterance.onend = () => {
      onDone();
    };
    utterance.onerror = () => {
      onDone();
    };

    window.speechSynthesis.speak(utterance);
  };

  // Setup SpeechRecognition
  useEffect(() => {
    if (typeof window === "undefined") return;

    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setErrorMessage("Web Speech API is not supported in this browser. Please use Google Chrome or Microsoft Edge for voice mode.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;
    recognition.lang = LANGUAGE_BCP47[language] || "en-US";

    recognition.onresult = (event: any) => {
      // If AI is currently speaking, user speech triggers BARGE-IN INTERRUPTION!
      if (isAiSpeakingRef.current) {
        interruptAi();
        setState("listening");
      }

      let currentInterim = "";
      let newFinal = "";

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        const transcriptChunk = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          newFinal += transcriptChunk;
        } else {
          currentInterim += transcriptChunk;
        }
      }

      if (currentInterim) {
        setInterimTranscript(currentInterim);
        setState("listening");
      }

      if (newFinal) {
        speechAccumulatorRef.current = (speechAccumulatorRef.current + " " + newFinal).trim();
        setFinalTranscript(speechAccumulatorRef.current);
      }

      // Voice Activity Detection (VAD) silence trigger:
      // When user stops speaking for 1200ms after giving words, automatically commit!
      if (silenceTimerRef.current) {
        clearTimeout(silenceTimerRef.current);
      }

      const activeText = (speechAccumulatorRef.current + " " + currentInterim).trim();
      if (activeText.length > 2) {
        silenceTimerRef.current = setTimeout(() => {
          if (!isAiSpeakingRef.current && stateRef.current === "listening") {
            const finalQuery = speechAccumulatorRef.current || currentInterim;
            if (finalQuery.trim()) {
              sendStudentMessage(finalQuery);
            }
          }
        }, 1200);
      }
    };

    recognition.onerror = (event: any) => {
      console.warn("Speech recognition notice:", event.error);
      if (event.error === "not-allowed") {
        setErrorMessage("Microphone permission denied. Please allow microphone permissions.");
        setState("error");
      } else if (event.error === "network") {
        setErrorMessage("Speech recognition network error. Please verify your internet connection.");
      }
      // "no-speech" is normal when student pauses; keep listening in continuous mode
    };

    recognition.onend = () => {
      // In continuous mode, if we are still supposed to be active, automatically restart
      if (stateRef.current === "listening" && !isMuted) {
        try {
          recognition.start();
        } catch (e) {
          // Already active or restarting
        }
      }
    };

    recognitionRef.current = recognition;

    return () => {
      try {
        recognition.stop();
      } catch (e) {}
      if (silenceTimerRef.current) {
        clearTimeout(silenceTimerRef.current);
      }
    };
  }, [language, isMuted, interruptAi, sendStudentMessage]);

  // Start Voice Mode
  const startConversation = useCallback(async () => {
    setErrorMessage(null);
    interruptAi();

    const stream = await initAudioStream();
    if (!stream) return;

    if (recognitionRef.current) {
      try {
        recognitionRef.current.lang = language === "hi" ? "hi-IN" : language === "te" ? "te-IN" : "en-US";
        recognitionRef.current.start();
      } catch (err) {
        // Recognition might already be running
      }
    }

    setState("listening");
    setIsMuted(false);
  }, [initAudioStream, interruptAi, language]);

  // Stop / End Conversation
  const stopConversation = useCallback(() => {
    interruptAi();
    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current);
    }
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (err) {}
    }
    cleanupAudio();
    setState("idle");
    setInterimTranscript("");
  }, [cleanupAudio, interruptAi]);

  // Toggle Mute
  const toggleMute = useCallback(() => {
    if (isMuted) {
      setIsMuted(false);
      if (recognitionRef.current) {
        try {
          recognitionRef.current.start();
        } catch (e) {}
      }
      setState("listening");
    } else {
      setIsMuted(true);
      interruptAi();
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (e) {}
      }
      setState("idle");
    }
  }, [isMuted, interruptAi]);

  // Clear session
  const clearSession = useCallback(() => {
    stopConversation();
    setConversationId(null);
    setTurns([]);
    setInterimTranscript("");
    setFinalTranscript("");
    setErrorMessage(null);
  }, [stopConversation]);

  return {
    state,
    errorMessage,
    conversationId,
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
    sendStudentMessage,
  };
}
