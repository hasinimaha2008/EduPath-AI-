from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict

# --- Auth & User Schemas ---
class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: str
    avatar_url: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# --- Subject & Topic Schemas ---
class TopicBase(BaseModel):
    name: str
    description: Optional[str] = None
    order_index: int = 0
    module_name: Optional[str] = "Module 1: Foundations"
    is_emerging: bool = False
    source_reference: Optional[str] = None
    last_updated_date: Optional[str] = None
    subtopics: List[str] = []

class TopicResponse(TopicBase):
    id: str
    subject_id: str

    model_config = ConfigDict(from_attributes=True)

class SubjectBase(BaseModel):
    name: str
    code: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = "Computer Science"
    icon_name: Optional[str] = "BookOpen"

class SubjectResponse(SubjectBase):
    id: str
    created_at: datetime
    topics: List[TopicResponse] = []

    model_config = ConfigDict(from_attributes=True)

# --- Document Schemas ---
class DocumentResponse(BaseModel):
    id: str
    user_id: str
    subject_id: Optional[str] = None
    title: str
    file_name: str
    file_size: int
    file_type: str
    status: str
    error_message: Optional[str] = None
    chunk_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- Conversation & Chat Schemas ---
class CitationItem(BaseModel):
    doc_title: str
    page_number: int
    snippet: str

class ChatMessageBase(BaseModel):
    content: str

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageResponse(BaseModel):
    id: str
    conversation_id: str
    sender_role: str
    content: str
    citations: Optional[List[CitationItem]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ConversationCreate(BaseModel):
    title: Optional[str] = "Academic Consultation"
    subject_id: Optional[str] = None
    document_id: Optional[str] = None

class ConversationResponse(BaseModel):
    id: str
    title: str
    subject_id: Optional[str] = None
    document_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessageResponse] = []

    model_config = ConfigDict(from_attributes=True)

class ConversationUpdate(BaseModel):
    title: str

# --- Notes Schemas ---
class NoteCreate(BaseModel):
    title: str
    content_markdown: str
    note_type: str = "detailed"  # short, detailed, chapter_wise, exam_oriented, revision, definitions, key_points, questions
    subject_id: Optional[str] = None
    topic_id: Optional[str] = None
    document_id: Optional[str] = None
    is_pinned: bool = False

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content_markdown: Optional[str] = None
    note_type: Optional[str] = None
    is_pinned: Optional[bool] = None

class NoteResponse(BaseModel):
    id: str
    user_id: str
    title: str
    content_markdown: str
    note_type: str
    subject_id: Optional[str] = None
    topic_id: Optional[str] = None
    document_id: Optional[str] = None
    is_pinned: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class NoteGenerateRequest(BaseModel):
    document_id: Optional[str] = None
    topic_name: Optional[str] = None
    subject_id: Optional[str] = None
    subject_name: Optional[str] = None
    unit_name: Optional[str] = None
    note_type: str = "detailed"
    explanation_style: Optional[str] = "standard"  # beginner, technical, point_wise, comparison, last_minute, standard
    language: Optional[str] = "en"

# --- Quiz Schemas ---
class QuestionOption(BaseModel):
    id: str
    text: str

class QuestionResponse(BaseModel):
    id: str
    quiz_id: str
    question_text: str
    question_type: str
    options: Optional[List[str]] = None
    points: int = 1
    code_snippet: Optional[str] = None
    test_cases: Optional[List[str]] = None
    # Notice: correct_answer and explanation are omitted for active quiz taking!

    model_config = ConfigDict(from_attributes=True)

class QuestionDetailResponse(QuestionResponse):
    correct_answer: str
    explanation: Optional[str] = None

class QuizCreateRequest(BaseModel):
    title: Optional[str] = None
    subject_id: Optional[str] = None
    topic_id: Optional[str] = None
    subtopic: Optional[str] = None
    document_id: Optional[str] = None
    note_id: Optional[str] = None
    difficulty: str = "medium"  # easy, medium, hard, mixed, beginner, intermediate, advanced
    question_count: int = 5
    question_types: List[str] = ["mcq"]

class QuizResponse(BaseModel):
    id: str
    title: str
    difficulty: str
    total_questions: int
    time_limit_mins: int
    subject_id: Optional[str] = None
    topic_id: Optional[str] = None
    document_id: Optional[str] = None
    note_id: Optional[str] = None
    created_at: datetime
    questions: List[QuestionResponse] = []

    model_config = ConfigDict(from_attributes=True)

class AnswerSubmission(BaseModel):
    question_id: str
    user_response: str

class QuizSubmitRequest(BaseModel):
    time_taken_seconds: int = 0
    answers: List[AnswerSubmission]

class UserAnswerResult(BaseModel):
    question_id: str
    question_text: str
    user_response: str
    correct_answer: str
    is_correct: bool
    score_awarded: float
    explanation: Optional[str] = None

class QuizResultResponse(BaseModel):
    attempt_id: str
    quiz_id: str
    score: float
    max_score: float
    percentage: float
    time_taken_seconds: int
    completed_at: datetime
    answers: List[UserAnswerResult]
    mastery_status: Optional[str] = None
    topic_breakdown: Optional[Dict[str, Any]] = None
    recommended_revision_topics: Optional[List[str]] = None
    mistakes_recorded: Optional[List[Dict[str, Any]]] = None

class QuizAttemptHistoryItem(BaseModel):
    id: str
    quiz_id: str
    quiz_title: str
    score: float
    max_score: float
    percentage: float
    time_taken_seconds: int
    completed_at: datetime

# --- Topic Performance Schemas ---
class TopicPerformanceResponse(BaseModel):
    id: str
    subject_name: str
    topic_name: str
    topic_id: str
    total_attempts: int
    correct_answers: int
    incorrect_answers: int
    accuracy_percentage: float
    mastery_status: str  # needs_practice, developing, proficient, mastered
    last_practiced_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- Analytics Schemas ---
class ActivityDay(BaseModel):
    date: str
    quiz_count: int
    questions_solved: int

class SubjectPerformanceItem(BaseModel):
    subject_id: Optional[str] = None
    subject_name: str
    quizzes_count: int
    topics_practiced: int
    average_accuracy: float

class QuizScoreTrendItem(BaseModel):
    attempt_id: str
    quiz_title: str
    percentage: float
    completed_at: str
    score: float
    max_score: float

class TopicCompletionStats(BaseModel):
    total_practiced: int
    mastered_count: int
    proficient_count: int
    developing_count: int
    needs_practice_count: int

class IntelligentInsightItem(BaseModel):
    category: str  # "attention" | "improvement" | "difficulty" | "revision"
    title: str
    message: str
    severity: str  # "info" | "warning" | "success"

class AnalyticsDashboardResponse(BaseModel):
    total_quizzes_attempted: int
    average_quiz_score: float
    highest_quiz_score: float = 0.0
    learning_streak_days: int
    total_study_hours: float
    study_consistency_percentage: float = 0.0
    strong_topics: List[TopicPerformanceResponse]
    weak_topics: List[TopicPerformanceResponse]
    recent_activity: List[ActivityDay]
    subject_performances: List[SubjectPerformanceItem] = []
    quiz_score_trends: List[QuizScoreTrendItem] = []
    topic_completion_stats: Optional[TopicCompletionStats] = None
    intelligent_insights: List[IntelligentInsightItem] = []
    revision_recommendations: List[str]
    personalized_recommendation: Optional[str] = None

# --- Career & Skill Schemas ---
class CareerRoleResponse(BaseModel):
    id: str
    title: str
    slug: str
    description: str
    salary_range: Optional[str] = None
    industry_demand: str
    icon_name: str

    model_config = ConfigDict(from_attributes=True)

class SkillResponse(BaseModel):
    id: str
    name: str
    category: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class SubjectSkillMappingResponse(BaseModel):
    id: str
    subject_name: str
    topic_name: str
    competency_name: str
    skill_name: str
    career_role_title: str
    industry_application: Optional[str] = None
    practical_project_example: Optional[str] = None

class CareerRecommendationResponse(BaseModel):
    id: str
    career_role: CareerRoleResponse
    domain: str = "Technology"
    match_score: float
    demonstrated_match_score: float = 0.0
    self_reported_match_score: float = 0.0
    rationale: str
    missing_skills_count: int
    matching_skills: List[str]
    missing_skills: List[str]
    recommended_projects: List[Dict[str, Any]] = []
    recommended_at: datetime

class SkillGapItem(BaseModel):
    skill_name: str
    category: str
    status: str  # existing, missing, needs_improvement
    priority: str  # High, Medium, Low
    proficiency: float
    evidence_source: str  # demonstrated, self_reported, missing
    is_verified: bool = False
    learning_recommendation: Optional[str] = None
    learning_resources: List[str] = []
    suggested_projects: List[str] = []
    job_market_importance: str = "Essential Core"

class SkillGapResponse(BaseModel):
    career_role: CareerRoleResponse
    overall_readiness: float
    gaps: List[SkillGapItem]

# --- Student Profile Schemas (Phase 6) ---
class ProjectExperienceItem(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    technologies: List[str] = []
    link: Optional[str] = None

class StudentCareerProfileResponse(BaseModel):
    user_id: str
    full_name: str
    email: str
    interests: List[str] = []
    preferred_domains: List[str] = []
    career_goals: Optional[Union[str, List[str]]] = None
    self_reported_skills: List[str] = []
    demonstrated_skills: List[Dict[str, Any]] = []
    projects_and_experience: List[ProjectExperienceItem] = []
    learning_progress: Dict[str, Any] = {}
    target_career_id: Optional[str] = None
    target_career_title: Optional[str] = None
    preferred_language: str = "en"
    explanation_style: str = "step_by_step"
    daily_goal_minutes: int = 45

class StudentProfileUpdateRequest(BaseModel):
    interests: Optional[List[str]] = None
    preferred_domains: Optional[List[str]] = None
    career_goals: Optional[Union[str, List[str]]] = None
    self_reported_skills: Optional[List[str]] = None
    projects_and_experience: Optional[List[ProjectExperienceItem]] = None
    target_career_id: Optional[str] = None
    preferred_language: Optional[str] = None
    explanation_style: Optional[str] = None
    daily_goal_minutes: Optional[int] = None

# --- Career Roadmap Schemas ---
class RoadmapMilestoneResponse(BaseModel):
    id: str
    stage: str = "intermediate"  # beginner, intermediate, advanced, capstone
    title: str
    description: str
    order_index: int
    is_completed: bool
    target_date: Optional[str] = None
    suggested_projects: List[str] = []
    learning_resources: List[str] = []
    practice_activities: List[str] = []

class CareerRoadmapResponse(BaseModel):
    id: str
    career_role: CareerRoleResponse
    title: str
    target_timeline_months: int
    progress_percentage: float
    milestones: List[RoadmapMilestoneResponse] = []
    created_at: datetime
    updated_at: datetime

class RoadmapGenerateRequest(BaseModel):
    career_role_id: str
    target_timeline_months: int = 6

# --- Study Planner Schemas (Phase 7: Intelligent Adaptive Planner) ---
class StudyTaskResponse(BaseModel):
    id: str
    study_plan_id: str
    topic_id: Optional[str] = None
    topic_name: Optional[str] = None
    title: str
    description: Optional[str] = None
    scheduled_date: str
    duration_minutes: int
    priority: str
    task_type: str = "study"  # study, revision, quiz, career_project, exam_prep
    difficulty_level: str = "medium"  # easy, medium, hard
    action_url: Optional[str] = None
    notes: Optional[str] = None
    is_completed: bool
    completed_at: Optional[datetime] = None
    is_overdue: bool = False

    model_config = ConfigDict(from_attributes=True)

class StudyPlanResponse(BaseModel):
    id: str
    title: str
    start_date: datetime
    end_date: Optional[datetime] = None
    daily_hours_target: float
    status: str
    exam_date: Optional[str] = None
    learning_priority: str = "balanced"
    total_tasks: int = 0
    completed_tasks: int = 0
    overdue_tasks: int = 0
    adherence_rate: float = 0.0
    tasks: List[StudyTaskResponse] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class StudyPlanGenerateRequest(BaseModel):
    title: Optional[str] = "Personalized Adaptive Study Plan"
    daily_hours_target: float = 2.0
    days_duration: int = 14
    focus_weak_topics: bool = True
    subject_ids: Optional[List[str]] = None
    topic_ids: Optional[List[str]] = None
    exam_date: Optional[str] = None  # YYYY-MM-DD
    learning_priority: Optional[str] = "balanced"  # weak_topics_first, exam_prep, career_skills, balanced
    include_revision: bool = True
    include_quizzes: bool = True

class StudyTaskCreateRequest(BaseModel):
    study_plan_id: Optional[str] = None
    topic_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    scheduled_date: str  # YYYY-MM-DD
    duration_minutes: int = 45
    priority: str = "Medium"  # High, Medium, Low
    task_type: str = "study"  # study, revision, quiz, career_project, exam_prep
    difficulty_level: str = "medium"
    notes: Optional[str] = None

class StudyTaskUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    scheduled_date: Optional[str] = None
    duration_minutes: Optional[int] = None
    priority: Optional[str] = None
    task_type: Optional[str] = None
    difficulty_level: Optional[str] = None
    notes: Optional[str] = None

class RescheduleMissedRequest(BaseModel):
    study_plan_id: Optional[str] = None
    start_from_date: Optional[str] = None  # YYYY-MM-DD, defaults to today

class AdaptiveRecommendationItem(BaseModel):
    id: str
    recommendation_type: str  # weak_topic_revision, quiz_retake, missed_tasks_rebalance, exam_pacing
    topic_id: Optional[str] = None
    topic_name: Optional[str] = None
    reason: str
    suggested_action: str
    estimated_duration_minutes: int
    priority: str = "High"

class PlannerProgressResponse(BaseModel):
    today_date: str
    today_total_tasks: int
    today_completed_tasks: int
    today_minutes_scheduled: int
    today_minutes_completed: int
    week_adherence_percentage: float
    overdue_tasks_count: int
    exam_countdown_days: Optional[int] = None
    learning_streak_days: int
    weak_topics_covered_count: int

# --- AI Intelligence & Evaluation Schemas ---
class AssistantAskRequest(BaseModel):
    question: str
    conversation_id: Optional[str] = None
    document_id: Optional[str] = None
    subject_id: Optional[str] = None
    language: Optional[str] = "auto"
    explanation_level: Optional[str] = "intermediate"  # beginner, intermediate, advanced, eli5, exam_oriented, real_world

class AssistantAskResponse(BaseModel):
    conversation_id: str
    user_message: ChatMessageResponse
    assistant_message: ChatMessageResponse

class AssistantRegenerateRequest(BaseModel):
    conversation_id: str
    explanation_level: Optional[str] = "intermediate"

class AssistantRegenerateResponse(BaseModel):
    conversation_id: str
    assistant_message: ChatMessageResponse

class AnswerEvaluationRequest(BaseModel):
    question: str
    answer: str
    context: Optional[str] = None
    criteria: Optional[List[str]] = None

class AnswerEvaluationResponse(BaseModel):
    relevance_score: float  # 0 to 10
    accuracy_score: float   # 0 to 10
    clarity_score: float    # 0 to 10
    completeness_score: float # 0 to 10
    overall_score: float    # 0 to 100
    evaluation_level: str   # Excellent, Proficient, Needs Work, Incomplete
    strengths: List[str]
    areas_for_improvement: List[str]
    actionable_feedback: str

# --- Career JD Skill Extractor Schemas ---
class JobDescriptionAnalysisRequest(BaseModel):
    job_title: Optional[str] = "Software Engineer"
    company_name: Optional[str] = None
    job_description_text: str
    target_career_id: Optional[str] = None

class JobDescriptionAnalysisResponse(BaseModel):
    job_title: str
    company_name: Optional[str] = None
    overall_match_percentage: float
    demonstrated_match_score: float
    self_reported_match_score: float
    readiness_status: str  # Ready for Applications, Minor Preparation Needed, Significant Bridge Needed
    extracted_required_skills: List[str]
    verified_demonstrated_skills: List[str]
    self_reported_skills: List[str]
    missing_skills: List[str]
    recommended_bridge_projects: List[Dict[str, Any]]
    recommended_study_topics: List[str]
    summary_analysis: str

