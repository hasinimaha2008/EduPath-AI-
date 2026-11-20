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
  topics: Topic[];
}

export interface Topic {
  id: string;
  subject_id: string;
  name: string;
  description?: string;
  order_index: number;
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
  question_type: string;
  options?: string[];
  points: number;
}

export interface Quiz {
  id: string;
  title: string;
  difficulty: "easy" | "medium" | "hard";
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
