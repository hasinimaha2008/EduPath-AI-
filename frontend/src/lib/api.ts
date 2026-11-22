import {
  AuthResponse, User, DocumentItem, ChatMessage, Conversation,
  Note, Quiz, QuizResult, QuizAttemptHistory, TopicPerformance,
  AnalyticsDashboard, CareerRole, Skill, SubjectSkillMapping,
  CareerRecommendation, SkillGapResponse, CareerRoadmap, StudyPlan, Subject, Topic,
  VoiceInfo, VoiceChatRequest, VoiceChatResponse,
  LanguageInfo, LearningProfile, MistakeInsights, NotificationListResponse,
  TopicWorkspaceData, ExplanationModeResponse, CareerComparisonResponse,
  CareerProjectItem, CareerPathwayItem
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

class ApiClient {
  private getToken(): string | null {
    if (typeof window !== "undefined") {
      return localStorage.getItem("edupath_token");
    }
    return null;
  }

  public setToken(token: string) {
    if (typeof window !== "undefined") {
      localStorage.setItem("edupath_token", token);
    }
  }

  public clearToken() {
    if (typeof window !== "undefined") {
      localStorage.removeItem("edupath_token");
    }
  }

  public setUser(user: User) {
    if (typeof window !== "undefined") {
      localStorage.setItem("edupath_user", JSON.stringify(user));
    }
  }

  public getUser(): User | null {
    if (typeof window !== "undefined") {
      const u = localStorage.getItem("edupath_user");
      if (u) {
        try {
          return JSON.parse(u);
        } catch {
          // ignore parsing error
        }
      }
    }
    return null;
  }

  public clearAuth() {
    if (typeof window !== "undefined") {
      localStorage.removeItem("edupath_token");
      localStorage.removeItem("edupath_user");
    }
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = this.getToken();
    const headers: Record<string, string> = {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers as Record<string, string> || {}),
    };

    if (!(options.body instanceof FormData) && !headers["Content-Type"]) {
      headers["Content-Type"] = "application/json";
    }

    const res = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    if (!res.ok) {
      if (res.status === 401 && typeof window !== "undefined" && !endpoint.includes("/auth/login") && !endpoint.includes("/auth/register") && !endpoint.includes("/auth/demo-login")) {
        this.clearAuth();
        if (window.location.pathname.startsWith("/dashboard")) {
          window.location.href = "/login";
        }
      }
      let errorMsg = `HTTP Error ${res.status}`;
      try {
        const errorJson = await res.json();
        errorMsg = errorJson.detail || errorMsg;
      } catch {
        // use fallback
      }
      throw new Error(errorMsg);
    }

    return res.json();
  }

  // Auth
  async register(data: { email: string; password: string; full_name: string }): Promise<AuthResponse> {
    const res = await this.request<AuthResponse>("/api/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    });
    this.setToken(res.access_token);
    this.setUser(res.user);
    return res;
  }

  async login(data: { email: string; password: string }): Promise<AuthResponse> {
    const res = await this.request<AuthResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    });
    this.setToken(res.access_token);
    this.setUser(res.user);
    return res;
  }

  async demoLogin(): Promise<AuthResponse> {
    const res = await this.request<AuthResponse>("/api/auth/demo-login");
    this.setToken(res.access_token);
    this.setUser(res.user);
    return res;
  }

  async getMe(): Promise<User> {
    return this.request<User>("/api/auth/me");
  }

  // Documents
  async uploadDocument(file: File, title?: string, subjectId?: string): Promise<DocumentItem> {
    const formData = new FormData();
    formData.append("file", file);
    if (title) formData.append("title", title);
    if (subjectId) formData.append("subject_id", subjectId);

    return this.request<DocumentItem>("/api/documents/upload", {
      method: "POST",
      body: formData,
    });
  }

  async listDocuments(): Promise<DocumentItem[]> {
    return this.request<DocumentItem[]>("/api/documents");
  }

  async deleteDocument(id: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/api/documents/${id}`, {
      method: "DELETE",
    });
  }

  async previewDocument(id: string): Promise<any> {
    return this.request(`/api/documents/${id}/preview`);
  }

  async askDocument(id: string, question: string, language?: string): Promise<{
    answer: string;
    found_in_document: boolean;
    citations: Array<{ doc_title: string; page_number: number; snippet: string }>;
  }> {
    return this.request(`/api/documents/${id}/ask`, {
      method: "POST",
      body: JSON.stringify({ question, language }),
    });
  }

  async getDocumentNotes(id: string): Promise<any> {
    return this.request(`/api/documents/${id}/notes`);
  }

  async getDocumentExamPrep(id: string): Promise<any> {
    return this.request(`/api/documents/${id}/exam-prep`);
  }

  async getDocumentDefinitionsAndFormulas(id: string): Promise<any> {
    return this.request(`/api/documents/${id}/definitions-formulas`);
  }

  async getDocumentImportantTopics(id: string): Promise<any> {
    return this.request(`/api/documents/${id}/important-topics`);
  }

  async getDocumentRevisionKit(id: string): Promise<any> {
    return this.request(`/api/documents/${id}/revision-kit`);
  }

  async explainDocumentTopic(id: string, topic: string): Promise<{
    topic: string;
    explanation: string;
    citations: Array<{ doc_title: string; page_number: number; snippet: string }>;
  }> {
    return this.request(`/api/documents/${id}/explain-topic`, {
      method: "POST",
      body: JSON.stringify({ topic }),
    });
  }

  async askAssistant(data: {
    question: string;
    conversation_id?: string;
    document_id?: string;
    subject_id?: string;
    language?: string;
  }): Promise<{
    conversation_id: string;
    user_message: ChatMessage;
    assistant_message: ChatMessage;
  }> {
    return this.request("/api/assistant/ask", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async regenerateAssistant(conversationId: string): Promise<{
    conversation_id: string;
    assistant_message: ChatMessage;
  }> {
    return this.request("/api/assistant/regenerate", {
      method: "POST",
      body: JSON.stringify({ conversation_id: conversationId }),
    });
  }

  async chatStreamAssistant(
    data: {
      question: string;
      conversation_id?: string;
      document_id?: string;
      subject_id?: string;
      language?: string;
    },
    callbacks: {
      onMeta?: (meta: { conversation_id: string; title: string; user_message: ChatMessage; citations?: any[] }) => void;
      onToken?: (token: string) => void;
      onDone?: (doneData: { assistant_message: ChatMessage }) => void;
      onError?: (err: string) => void;
    },
    signal?: AbortSignal
  ): Promise<void> {
    const token = this.getToken();
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };

    const res = await fetch(`${API_BASE}/api/assistant/chat-stream`, {
      method: "POST",
      headers,
      body: JSON.stringify(data),
      signal,
    });

    if (!res.ok) {
      let errText = `Stream error ${res.status}`;
      try {
        const j = await res.json();
        errText = j.detail || errText;
      } catch {}
      if (callbacks.onError) callbacks.onError(errText);
      throw new Error(errText);
    }

    if (!res.body) throw new Error("No response body available for streaming.");

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    try {
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed.startsWith("data: ")) {
            const rawJson = trimmed.slice(6);
            try {
              const parsed = JSON.parse(rawJson);
              if (parsed.type === "meta" && callbacks.onMeta) {
                callbacks.onMeta(parsed);
              } else if (parsed.type === "token" && callbacks.onToken) {
                callbacks.onToken(parsed.content);
              } else if (parsed.type === "done" && callbacks.onDone) {
                callbacks.onDone(parsed);
              }
            } catch (pErr) {
              console.warn("Failed to parse SSE chunk:", rawJson);
            }
          }
        }
      }
    } catch (readErr: any) {
      if (readErr.name === "AbortError") {
        console.log("Chat stream was aborted by user.");
      } else {
        if (callbacks.onError) callbacks.onError(readErr.message);
        throw readErr;
      }
    }
  }

  async getAssistantStatus(): Promise<{
    is_configured: boolean;
    model_name: string;
    provider: string;
    streaming_supported: boolean;
    multilingual_supported: string[];
  }> {
    return this.request("/api/assistant/status");
  }

  async configureAssistantKey(apiKey: string): Promise<{
    success: boolean;
    configured: boolean;
    model: string;
    message: string;
  }> {
    return this.request("/api/assistant/configure-key", {
      method: "POST",
      body: JSON.stringify({ api_key: apiKey }),
    });
  }

  // Notes
  async generateNotes(data: {
    topic_name?: string;
    note_type: string;
    document_id?: string;
  }): Promise<Note> {
    return this.request<Note>("/api/notes/generate", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async listNotes(noteType?: string): Promise<Note[]> {
    const query = noteType ? `?note_type=${encodeURIComponent(noteType)}` : "";
    return this.request<Note[]>(`/api/notes${query}`);
  }

  async updateNote(id: string, data: Partial<Note>): Promise<Note> {
    return this.request<Note>(`/api/notes/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async deleteNote(id: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/api/notes/${id}`, {
      method: "DELETE",
    });
  }

  // Quizzes
  async generateQuiz(data: {
    title?: string;
    subject_id?: string;
    topic_id?: string;
    subtopic?: string;
    document_id?: string;
    difficulty?: string;
    question_count?: number;
    question_types?: string[];
  }): Promise<Quiz> {
    return this.request<Quiz>("/api/quizzes/generate", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getQuiz(quizId: string): Promise<Quiz> {
    return this.request<Quiz>(`/api/quizzes/${quizId}`);
  }

  async submitQuiz(quizId: string, data: { time_taken_seconds: number; answers: { question_id: string; user_response: string }[] }): Promise<QuizResult> {
    return this.request<QuizResult>(`/api/quizzes/${quizId}/submit`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getQuizHistory(): Promise<QuizAttemptHistory[]> {
    return this.request<QuizAttemptHistory[]>("/api/quizzes/history/attempts");
  }

  // Analytics & Topics
  async getDashboardAnalytics(): Promise<AnalyticsDashboard> {
    return this.request<AnalyticsDashboard>("/api/analytics/dashboard");
  }

  async getTopicPerformance(): Promise<TopicPerformance[]> {
    return this.request<TopicPerformance[]>("/api/topics/performance");
  }

  // Careers & Skills
  async getCareerRoles(): Promise<CareerRole[]> {
    return this.request<CareerRole[]>("/api/careers/roles");
  }

  async getCareerRecommendations(): Promise<CareerRecommendation[]> {
    return this.request<CareerRecommendation[]>("/api/careers/recommendations");
  }

  async getSubjects(category?: string): Promise<Subject[]> {
    const query = category ? `?category=${encodeURIComponent(category)}` : "";
    return this.request<Subject[]>(`/api/subjects${query}`);
  }

  async getSubjectDetail(subjectId: string): Promise<Subject> {
    return this.request<Subject>(`/api/subjects/${subjectId}`);
  }

  async getSubjectTopics(subjectId: string, onlyEmerging?: boolean): Promise<Topic[]> {
    const query = onlyEmerging !== undefined ? `?only_emerging=${onlyEmerging}` : "";
    return this.request<Topic[]>(`/api/subjects/${subjectId}/topics${query}`);
  }

  async getSkillsCatalog(): Promise<Skill[]> {
    return this.request<Skill[]>("/api/skills/catalog");
  }

  async getSkillMappings(): Promise<SubjectSkillMapping[]> {
    return this.request<SubjectSkillMapping[]>("/api/skills/mappings");
  }

  async getSkillGaps(roleId: string): Promise<SkillGapResponse> {
    return this.request<SkillGapResponse>(`/api/skills/gaps/${roleId}`);
  }

  // Roadmaps
  async generateRoadmap(roleId: string, timelineMonths: number = 6): Promise<CareerRoadmap> {
    return this.request<CareerRoadmap>("/api/roadmaps/generate", {
      method: "POST",
      body: JSON.stringify({ career_role_id: roleId, target_timeline_months: timelineMonths }),
    });
  }

  async listRoadmaps(): Promise<CareerRoadmap[]> {
    return this.request<CareerRoadmap[]>("/api/roadmaps");
  }

  async toggleMilestone(milestoneId: string): Promise<{ milestone_id: string; is_completed: boolean; roadmap_progress: number }> {
    return this.request(`/api/roadmaps/milestones/${milestoneId}/toggle`, {
      method: "POST",
    });
  }

  // Study Planner
  async getActiveStudyPlan(): Promise<StudyPlan> {
    return this.request<StudyPlan>("/api/study-planner/active");
  }

  async generateStudyPlan(data: { title?: string; daily_hours_target?: number; days_duration?: number }): Promise<StudyPlan> {
    return this.request<StudyPlan>("/api/study-planner/generate", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async toggleTask(taskId: string): Promise<{ task_id: string; is_completed: boolean }> {
    return this.request(`/api/study-planner/tasks/${taskId}/toggle`, {
      method: "POST",
    });
  }

  async rescheduleTask(taskId: string, newDate: string): Promise<{ task_id: string; new_date: string }> {
    return this.request(`/api/study-planner/tasks/${taskId}/reschedule?new_date=${encodeURIComponent(newDate)}`, {
      method: "POST",
    });
  }

  // Chat History
  async listConversations(): Promise<Conversation[]> {
    return this.request<Conversation[]>("/api/chat-history");
  }

  async getConversation(id: string): Promise<Conversation> {
    return this.request<Conversation>(`/api/chat-history/${id}`);
  }

  async renameConversation(id: string, title: string): Promise<Conversation> {
    return this.request<Conversation>(`/api/chat-history/${id}`, {
      method: "PUT",
      body: JSON.stringify({ title }),
    });
  }

  async deleteConversation(id: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/api/chat-history/${id}`, {
      method: "DELETE",
    });
  }

  // Conversational AI Voice Agent
  async voiceChat(req: VoiceChatRequest): Promise<VoiceChatResponse> {
    return this.request<VoiceChatResponse>("/api/voice/chat", {
      method: "POST",
      body: JSON.stringify(req),
    });
  }

  async getVoices(): Promise<VoiceInfo[]> {
    return this.request<VoiceInfo[]>("/api/voice/voices");
  }

  async getLanguages(): Promise<LanguageInfo[]> {
    return this.request<LanguageInfo[]>("/api/voice/languages");
  }

  // --- AI Learning Insights & Mistake Analysis (Upgrade 5) ---
  async getMistakes(): Promise<MistakeInsights> {
    return this.request<MistakeInsights>("/api/insights/mistakes");
  }

  async getInsightsSummary(): Promise<any> {
    return this.request<any>("/api/insights/summary");
  }

  // --- Interactive Learning Workspace (Upgrade 7) ---
  async getTopicWorkspace(topicId: string): Promise<TopicWorkspaceData> {
    return this.request<TopicWorkspaceData>(`/api/workspace/topic/${topicId}`);
  }

  async explainConcept(data: {
    topic_name: string;
    concept_name?: string;
    mode?: string;
    subject_name?: string;
    context_notes?: string;
  }): Promise<ExplanationModeResponse> {
    return this.request<ExplanationModeResponse>("/api/workspace/explain", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // --- Smart Notifications (Upgrade 8) ---
  async listNotifications(): Promise<NotificationListResponse> {
    return this.request<NotificationListResponse>("/api/notifications");
  }

  async markNotificationRead(id: string): Promise<any> {
    return this.request<any>(`/api/notifications/${id}/read`, {
      method: "PUT",
    });
  }

  async markAllNotificationsRead(): Promise<any> {
    return this.request<any>("/api/notifications/read-all", {
      method: "PUT",
    });
  }

  async triggerReminders(): Promise<any> {
    return this.request<any>("/api/notifications/trigger-reminders", {
      method: "POST",
    });
  }

  // --- Student Learning Profile (Upgrade 2) ---
  async getLearningProfile(): Promise<LearningProfile> {
    return this.request<LearningProfile>("/api/profile/learning");
  }

  async updateLearningProfile(data: Partial<LearningProfile>): Promise<LearningProfile> {
    return this.request<LearningProfile>("/api/profile/learning", {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  // --- Career Intelligence 2.0 (Upgrade 6) ---
  async compareCareers(roleIds: string[]): Promise<CareerComparisonResponse> {
    return this.request<CareerComparisonResponse>(`/api/careers/compare?role_ids=${roleIds.join(",")}`);
  }

  async getCareerProjects(careerId: string): Promise<CareerProjectItem[]> {
    return this.request<CareerProjectItem[]>(`/api/careers/${careerId}/projects`);
  }

  async getCareerPathways(careerId: string): Promise<{ outbound_pathways: CareerPathwayItem[] }> {
    return this.request<{ outbound_pathways: CareerPathwayItem[] }>(`/api/careers/${careerId}/pathways`);
  }

  // --- Adaptive Quiz Generation (Upgrade 2) ---
  async generateAdaptiveQuiz(data: { topic_id: string; difficulty?: string; question_count?: number }): Promise<Quiz> {
    return this.request<Quiz>("/api/quizzes/generate-adaptive", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // --- Document Intelligence 2.0 (Upgrade 4) ---
  async getDocumentSummary(documentId: string): Promise<any> {
    return this.request<any>(`/api/documents/${documentId}/summary`);
  }

  async getDocumentConcepts(documentId: string): Promise<any> {
    return this.request<any>(`/api/documents/${documentId}/concepts`);
  }

  async generateDocumentQuestions(documentId: string, count: number = 5): Promise<any> {
    return this.request<any>(`/api/documents/${documentId}/generate-questions?count=${count}`, {
      method: "POST",
    });
  }
}

export const api = new ApiClient();

