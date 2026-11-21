export interface User {
  id: string;
  email: string;
  full_name: string;
  avatar_url?: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Subject {
  id: string;
  name: string;
  code?: string;
  description?: string;
  category?: string;
  icon_name?: string;
  topics: Topic[];
}

export interface Topic {
  id: string;
  subject_id: string;
  name: string;
  description?: string;
  order_index: number;
  module_name?: string;
  subtopics?: string[];
  is_emerging?: boolean;
  source_reference?: string;
  last_updated_date?: string;
}

export interface DocumentItem {
  id: string;
  user_id: string;
  subject_id?: string;
  title: string;
  file_name: string;
  file_size: number;
  file_type: string;
  status: "processing" | "ready" | "failed";
  error_message?: string;
  chunk_count: number;
  created_at: string;
}

export interface Citation {
  doc_title: string;
  page_number: number;
  snippet: string;
}

export interface ChatMessage {
  id: string;
  conversation_id: string;
  sender_role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  created_at: string;
}

export interface Conversation {
  id: string;
  title: string;
  subject_id?: string;
  document_id?: string;
  created_at: string;
  updated_at: string;
  messages: ChatMessage[];
}

export interface Note {
  id: string;
  user_id: string;
  title: string;
  content_markdown: string;
  note_type: string;
  subject_id?: string;
  topic_id?: string;
  document_id?: string;
  is_pinned: boolean;
  created_at: string;
  updated_at: string;
}

export interface Question {
  id: string;
  quiz_id: string;
  question_text: string;
  question_type: "mcq" | "multiple_select" | "short_answer" | "long_answer" | "technical_interview" | "programming" | "scenario_based" | "application_oriented" | string;
  options?: string[];
  points: number;
  code_snippet?: string;
  test_cases?: string[];
}

export interface Quiz {
  id: string;
  title: string;
  difficulty: "beginner" | "intermediate" | "advanced" | "easy" | "medium" | "hard" | string;
  total_questions: number;
  time_limit_mins: number;
  subject_id?: string;
  topic_id?: string;
  document_id?: string;
  created_at: string;
  questions: Question[];
}

export interface UserAnswerResult {
  question_id: string;
  question_text: string;
  user_response: string;
  correct_answer: string;
  is_correct: boolean;
  score_awarded: number;
  explanation?: string;
}

export interface QuizResult {
  attempt_id: string;
  quiz_id: string;
  score: number;
  max_score: number;
  percentage: number;
  time_taken_seconds: number;
  completed_at: string;
  answers: UserAnswerResult[];
}

export interface QuizAttemptHistory {
  id: string;
  quiz_id: string;
  quiz_title: string;
  score: number;
  max_score: number;
  percentage: number;
  time_taken_seconds: number;
  completed_at: string;
}

export interface TopicPerformance {
  id: string;
  subject_name: string;
  topic_name: string;
  topic_id: string;
  total_attempts: number;
  correct_answers: number;
  incorrect_answers: number;
  accuracy_percentage: number;
  mastery_status: "needs_practice" | "developing" | "proficient" | "mastered";
  last_practiced_at: string;
}

export interface ActivityDay {
  date: string;
  quiz_count: number;
  questions_solved: number;
}

export interface AnalyticsDashboard {
  total_quizzes_attempted: number;
  average_quiz_score: number;
  learning_streak_days: number;
  total_study_hours: number;
  strong_topics: TopicPerformance[];
  weak_topics: TopicPerformance[];
  recent_activity: ActivityDay[];
  revision_recommendations: string[];
}

export interface CareerRole {
  id: string;
  title: string;
  slug: string;
  description: string;
  salary_range?: string;
  industry_demand: string;
  icon_name: string;
}

export interface Skill {
  id: string;
  name: string;
  category: string;
  description?: string;
}

export interface SubjectSkillMapping {
  id: string;
  subject_name: string;
  topic_name: string;
  competency_name: string;
  skill_name: string;
  career_role_title: string;
}

export interface CareerRecommendation {
  id: string;
  career_role: CareerRole;
  match_score: number;
  rationale: string;
  missing_skills_count: number;
  matching_skills: string[];
  missing_skills: string[];
  recommended_at: string;
}

export interface SkillGapItem {
  skill_name: string;
  category: string;
  status: "existing" | "missing" | "needs_improvement";
  priority: "High" | "Medium" | "Low";
  proficiency: number;
  evidence_source: "demonstrated" | "self_reported" | "missing";
  learning_recommendation?: string;
}

export interface SkillGapResponse {
  career_role: CareerRole;
  overall_readiness: number;
  gaps: SkillGapItem[];
}

export interface RoadmapMilestone {
  id: string;
  title: string;
  description: string;
  order_index: number;
  is_completed: boolean;
  target_date?: string;
  suggested_projects: string[];
  practice_activities: string[];
}

export interface CareerRoadmap {
  id: string;
  career_role: CareerRole;
  title: string;
  target_timeline_months: number;
  progress_percentage: number;
  milestones: RoadmapMilestone[];
  created_at: string;
  updated_at: string;
}

export interface StudyTask {
  id: string;
  study_plan_id: string;
  topic_id?: string;
  topic_name?: string;
  title: string;
  description?: string;
  scheduled_date: string;
  duration_minutes: number;
  priority: "High" | "Medium" | "Low";
  is_completed: boolean;
  completed_at?: string;
}

export interface StudyPlan {
  id: string;
  title: string;
  start_date: string;
  end_date?: string;
  daily_hours_target: number;
  status: string;
  tasks: StudyTask[];
  created_at: string;
}

// --- Conversational AI Voice Agent Interfaces ---
export interface VoiceInfo {
  id: string;
  name: string;
  language: string;
  gender: string;
}

export interface VoiceChatTurn {
  role: "user" | "assistant";
  content: string;
}

export interface VoiceChatRequest {
  message: string;
  conversation_id?: string;
  subject_id?: string;
  language: string;
  voice?: string;
  synthesize_audio?: boolean;
  history?: VoiceChatTurn[];
}

export interface VoiceChatResponse {
  conversation_id: string;
  reply_text: string;
  language: string;
  voice: string;
  audio_base64?: string;
  audio_stream_url: string;
}

export interface LanguageInfo {
  code: string;
  name: string;
  native: string;
}

// --- EduPath AI 2.0 Extensions ---

export interface LearningProfile {
  id: string;
  user_id: string;
  preferred_language: string;
  explanation_style: string;
  daily_goal_minutes: number;
  target_career_id?: string;
  target_career_title?: string;
  learning_preferences: Record<string, any>;
  created_at?: string;
  updated_at?: string;
}

export interface QuizMistakeItem {
  id: string;
  topic_name: string;
  question_text: string;
  error_category: "conceptual_misunderstanding" | "incorrect_application" | "calculation_error" | "misinterpretation" | "knowledge_gap" | "unclassified";
  user_response: string;
  correct_answer: string;
  explanation: string;
  suggested_fix?: string;
  repeated_count: number;
  created_at: string;
}

export interface MistakeInsights {
  total_mistakes: number;
  repeated_mistakes_count: number;
  improvement_rate: number;
  category_distribution: { category: string; label: string; count: number }[];
  repeated_mistakes: QuizMistakeItem[];
  recent_mistakes: QuizMistakeItem[];
  actionable_advice: string;
}

export interface NotificationItem {
  id: string;
  title: string;
  message: string;
  notification_type: "revision_due" | "task_reminder" | "weak_topic_alert" | "career_milestone" | "quiz_feedback";
  is_read: boolean;
  action_url?: string;
  created_at: string;
}

export interface NotificationListResponse {
  unread_count: number;
  notifications: NotificationItem[];
}

export interface TopicWorkspaceData {
  topic: {
    id: string;
    name: string;
    description?: string;
    module_name?: string;
    subtopics?: string[];
    is_emerging?: boolean;
    source_reference?: string;
    subject_id?: string;
    subject_name?: string;
  };
  performance: {
    total_attempts: number;
    correct_answers: number;
    incorrect_answers: number;
    accuracy_percentage: number;
    mastery_status: string;
    last_practiced_at?: string;
  };
  notes: {
    id: string;
    title: string;
    note_type: string;
    content_preview: string;
    created_at: string;
  }[];
  documents: {
    id: string;
    title: string;
    status: string;
    file_type: string;
    created_at: string;
  }[];
  quiz_attempts: {
    attempt_id: string;
    quiz_title: string;
    score: number;
    max_score: number;
    percentage: number;
    completed_at: string;
  }[];
  revision_tasks: {
    id: string;
    title: string;
    description: string;
    scheduled_date: string;
    is_due: boolean;
    priority: string;
  }[];
}

export interface ExplanationModeResponse {
  mode: string;
  mode_title: string;
  concept: string;
  topic_name: string;
  content: string;
}

export interface CareerProjectItem {
  id: string;
  title: string;
  objective: string;
  difficulty: "Beginner" | "Intermediate" | "Advanced";
  required_skills: string[];
  tools: string[];
  steps: string[];
  expected_outcome: string;
  competency_focus: string;
}

export interface CareerPathwayItem {
  id: string;
  target_role_id: string;
  target_role_title: string;
  transition_difficulty: string;
  bridge_skills: string[];
  guidance: string;
}

export interface CareerComparisonRole {
  id: string;
  title: string;
  slug: string;
  salary_range: string;
  industry_demand: string;
  icon_name: string;
  readiness_score: number;
  demonstrated_skills: { skill: string; proficiency: number; target: number }[];
  in_progress_skills: { skill: string; proficiency: number; target: number }[];
  missing_skills: { skill: string; proficiency: number; target: number }[];
}

export interface CareerComparisonResponse {
  compared_roles: CareerComparisonRole[];
  shared_skills: string[];
  comparison_count: number;
}

