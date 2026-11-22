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
  question_type: "mcq" | "true_false" | "fill_in_the_blank" | "short_answer" | "multiple_select" | "long_answer" | "technical_interview" | "programming" | "scenario_based" | "application_oriented" | string;
  options?: string[];
  points: number;
  code_snippet?: string;
  test_cases?: string[];
}

export interface Quiz {
  id: string;
  title: string;
  difficulty: "beginner" | "intermediate" | "advanced" | "easy" | "medium" | "hard" | "mixed" | string;
  total_questions: number;
  time_limit_mins: number;
  subject_id?: string;
  topic_id?: string;
  document_id?: string;
  note_id?: string;
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
  mastery_status?: string;
  topic_breakdown?: {
    topic_name: string;
    total_questions: number;
    correct_count: number;
    accuracy: number;
    mastery_status: string;
  };
  recommended_revision_topics?: string[];
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

export interface SubjectPerformanceItem {
  subject_id?: string;
  subject_name: string;
  quizzes_count: number;
  topics_practiced: number;
  average_accuracy: number;
}

export interface QuizScoreTrendItem {
  attempt_id: string;
  quiz_title: string;
  percentage: number;
  completed_at: string;
  score: number;
  max_score: number;
}

export interface TopicCompletionStats {
  total_practiced: number;
  mastered_count: number;
  proficient_count: number;
  developing_count: number;
  needs_practice_count: number;
}

export interface IntelligentInsightItem {
  category: "attention" | "improvement" | "difficulty" | "revision" | string;
  title: string;
  message: string;
  severity: "info" | "warning" | "success" | string;
}

export interface AnalyticsDashboard {
  total_quizzes_attempted: number;
  average_quiz_score: number;
  highest_quiz_score?: number;
  learning_streak_days: number;
  total_study_hours: number;
  study_consistency_percentage?: number;
  strong_topics: TopicPerformance[];
  weak_topics: TopicPerformance[];
  recent_activity: ActivityDay[];
  subject_performances?: SubjectPerformanceItem[];
  quiz_score_trends?: QuizScoreTrendItem[];
  topic_completion_stats?: TopicCompletionStats;
  intelligent_insights?: IntelligentInsightItem[];
  revision_recommendations: string[];
  personalized_recommendation?: string;
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
  industry_application?: string;
  practical_project_example?: string;
}

export interface CareerRecommendation {
  id: string;
  career_role: CareerRole;
  domain?: string;
  match_score: number;
  demonstrated_match_score?: number;
  self_reported_match_score?: number;
  rationale: string;
  missing_skills_count: number;
  matching_skills: string[];
  missing_skills: string[];
  recommended_projects?: Array<{
    title: string;
    objective: string;
    difficulty: string;
    tools: string[];
  }>;
  recommended_at: string;
}

export interface SkillGapItem {
  skill_name: string;
  category: string;
  status: "existing" | "missing" | "needs_improvement";
  priority: "High" | "Medium" | "Low";
  proficiency: number;
  evidence_source: "demonstrated" | "self_reported" | "missing";
  is_verified?: boolean;
  learning_recommendation?: string;
  learning_resources?: string[];
  suggested_projects?: string[];
  job_market_importance?: string;
}

export interface SkillGapResponse {
  career_role: CareerRole;
  overall_readiness: number;
  gaps: SkillGapItem[];
}

export interface ProjectExperienceItem {
  id?: string;
  title: string;
  description: string;
  technologies: string[];
  link?: string;
}

export interface StudentCareerProfile {
  user_id: string;
  full_name: string;
  email: string;
  interests: string[];
  preferred_domains: string[];
  career_goals?: string;
  self_reported_skills: string[];
  demonstrated_skills: Array<{
    skill_name: string;
    proficiency: number;
    evidence_notes?: string;
  }>;
  projects_and_experience: ProjectExperienceItem[];
  learning_progress: {
    total_quizzes_attempted: number;
    average_quiz_score: number;
    study_hours: number;
    mastered_topics_count: number;
  };
  target_career_id?: string;
  target_career_title?: string;
  preferred_language: string;
  explanation_style: string;
  daily_goal_minutes: number;
}

export interface StudentProfileUpdateRequest {
  interests?: string[];
  preferred_domains?: string[];
  career_goals?: string;
  self_reported_skills?: string[];
  projects_and_experience?: ProjectExperienceItem[];
  target_career_id?: string;
  preferred_language?: string;
  explanation_style?: string;
  daily_goal_minutes?: number;
}

export interface RoadmapMilestone {
  id: string;
  stage?: "beginner" | "intermediate" | "advanced" | "capstone" | string;
  title: string;
  description: string;
  order_index: number;
  is_completed: boolean;
  target_date?: string;
  suggested_projects: string[];
  learning_resources?: string[];
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
  priority: "High" | "Medium" | "Low" | string;
  task_type?: "study" | "revision" | "quiz" | "career_project" | "exam_prep" | string;
  difficulty_level?: "easy" | "medium" | "hard" | string;
  action_url?: string;
  notes?: string;
  is_completed: boolean;
  completed_at?: string;
  is_overdue?: boolean;
}

export interface StudyPlan {
  id: string;
  title: string;
  start_date: string;
  end_date?: string;
  daily_hours_target: number;
  status: string;
  exam_date?: string;
  learning_priority?: string;
  total_tasks?: number;
  completed_tasks?: number;
  overdue_tasks?: number;
  adherence_rate?: number;
  tasks: StudyTask[];
  created_at: string;
}

export interface StudyPlanGenerateOptions {
  title?: string;
  daily_hours_target?: number;
  days_duration?: number;
  focus_weak_topics?: boolean;
  subject_ids?: string[];
  topic_ids?: string[];
  exam_date?: string;
  learning_priority?: "weak_topics_first" | "exam_prep" | "career_skills" | "balanced" | string;
  include_revision?: boolean;
  include_quizzes?: boolean;
}

export interface StudyTaskCreateInput {
  study_plan_id?: string;
  topic_id?: string;
  title: string;
  description?: string;
  scheduled_date: string;
  duration_minutes?: number;
  priority?: "High" | "Medium" | "Low" | string;
  task_type?: "study" | "revision" | "quiz" | "career_project" | "exam_prep" | string;
  difficulty_level?: "easy" | "medium" | "hard" | string;
  notes?: string;
}

export interface StudyTaskUpdateInput {
  title?: string;
  description?: string;
  scheduled_date?: string;
  duration_minutes?: number;
  priority?: "High" | "Medium" | "Low" | string;
  task_type?: string;
  difficulty_level?: string;
  notes?: string;
}

export interface AdaptiveRecommendationItem {
  id: string;
  recommendation_type: string;
  topic_id?: string;
  topic_name?: string;
  reason: string;
  suggested_action: string;
  estimated_duration_minutes: number;
  priority: string;
}

export interface PlannerProgress {
  today_date: string;
  today_total_tasks: number;
  today_completed_tasks: number;
  today_minutes_scheduled: number;
  today_minutes_completed: number;
  week_adherence_percentage: number;
  overdue_tasks_count: number;
  exam_countdown_days?: number | null;
  learning_streak_days: number;
  weak_topics_covered_count: number;
}

export interface RescheduleMissedResponse {
  rescheduled_count: number;
  message: string;
  rescheduled_tasks?: Array<{
    task_id: string;
    title: string;
    previous_date: string;
    new_date: string;
  }>;
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

export interface EcosystemRecommendation {
  source: string;
  category: string;
  title: string;
  action_url: string;
  action_label: string;
  priority: string;
}

export interface EcosystemSummaryResponse {
  user_id: string;
  user_name: string;
  target_career: {
    id: string | null;
    title: string;
    readiness_score: number;
    missing_skills: string[];
  };
  documents_summary: {
    total_documents: number;
    recent_documents: {
      id: string;
      title: string;
      file_type: string;
      status: string;
      created_at: string;
    }[];
  };
  notes_summary: {
    total_notes: number;
    recent_notes: {
      id: string;
      title: string;
      format_type: string;
      topic_name?: string;
      created_at: string;
    }[];
  };
  quizzes_summary: {
    total_attempts: number;
    average_score: number;
    recent_quizzes: {
      id: string;
      quiz_id: string;
      title: string;
      score: number;
      max_score: number;
      percentage: number;
      completed_at: string;
    }[];
  };
  analytics_summary: {
    topics_mastered_count: number;
    topics_developing_count: number;
    weak_topics_count: number;
    weak_topics: {
      topic_id: string;
      name: string;
      accuracy: number;
      mastery: string;
    }[];
  };
  study_plan: {
    id: string;
    title: string;
    exam_date?: string;
    total_tasks: number;
    completed_tasks: number;
    pending_tasks: number;
    adherence_rate: number;
  } | null;
  today_tasks: {
    id: string;
    title: string;
    task_type: string;
    priority: string;
    duration_minutes: number;
    is_completed: boolean;
    action_url?: string;
  }[];
  career_roadmap: {
    id: string;
    title: string;
    progress_percentage: number;
    completed_milestones: number;
    total_milestones: number;
    next_milestone?: string;
  } | null;
  recommendations: EcosystemRecommendation[];
}

