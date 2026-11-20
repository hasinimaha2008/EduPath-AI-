import {
  AuthResponse, User, DocumentItem, ChatMessage, Conversation,
  Note, Quiz, QuizResult, QuizAttemptHistory, TopicPerformance,
  AnalyticsDashboard, CareerRole, Skill, SubjectSkillMapping,
  CareerRecommendation, SkillGapResponse, CareerRoadmap, StudyPlan, Subject
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
    return res;
  }

  async login(data: { email: string; password: string }): Promise<AuthResponse> {
    const res = await this.request<AuthResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    });
    this.setToken(res.access_token);
    return res;
  }

  async demoLogin(): Promise<AuthResponse> {
    const res = await this.request<AuthResponse>("/api/auth/demo-login");
    this.setToken(res.access_token);
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

  // Assistant
  async askAssistant(data: {
    question: string;
    conversation_id?: string;
    document_id?: string;
    subject_id?: string;
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
    topic_id?: string;
    document_id?: string;
    difficulty?: string;
    question_count?: number;
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

  async getSubjects(): Promise<Subject[]> {
    return this.request<Subject[]>("/api/skills/subjects");
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
}

export const api = new ApiClient();
