import uuid
import json
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

def get_utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    avatar_url = Column(String(512), nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now)

    # Relationships
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="user", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="user", cascade="all, delete-orphan")
    quiz_attempts = relationship("QuizAttempt", back_populates="user", cascade="all, delete-orphan")
    topic_performances = relationship("TopicPerformance", back_populates="user", cascade="all, delete-orphan")
    user_skills = relationship("UserSkill", back_populates="user", cascade="all, delete-orphan")
    career_recommendations = relationship("CareerRecommendation", back_populates="user", cascade="all, delete-orphan")
    skill_gaps = relationship("SkillGap", back_populates="user", cascade="all, delete-orphan")
    career_roadmaps = relationship("CareerRoadmap", back_populates="user", cascade="all, delete-orphan")
    study_plans = relationship("StudyPlan", back_populates="user", cascade="all, delete-orphan")
    learning_profile = relationship("LearningProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    quiz_mistakes = relationship("QuizMistake", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), unique=True, nullable=False, index=True)
    code = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), default="Computer Science")
    icon_name = Column(String(50), default="BookOpen")
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

    topics = relationship("Topic", back_populates="subject", cascade="all, delete-orphan", order_by="Topic.order_index")
    documents = relationship("Document", back_populates="subject")


class Topic(Base):
    __tablename__ = "topics"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    subject_id = Column(String(36), ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, default=0)
    module_name = Column(String(255), default="Module 1: Foundations")
    subtopics_json = Column(Text, nullable=True)  # JSON array of subtopics
    is_emerging = Column(Boolean, default=False)
    source_reference = Column(String(512), nullable=True)
    last_updated_date = Column(String(50), nullable=True)

    subject = relationship("Subject", back_populates="topics")
    topic_performances = relationship("TopicPerformance", back_populates="topic", cascade="all, delete-orphan")

    @property
    def subtopics(self) -> list:
        if self.subtopics_json:
            try:
                return json.loads(self.subtopics_json)
            except Exception:
                return []
        return []


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(String(36), ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, docx
    status = Column(String(50), default="processing")  # processing, ready, failed
    error_message = Column(Text, nullable=True)
    chunk_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

    user = relationship("User", back_populates="documents")
    subject = relationship("Subject", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    page_number = Column(Integer, default=1)
    token_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

    document = relationship("Document", back_populates="chunks")
    embeddings = relationship("DocumentEmbedding", back_populates="chunk", cascade="all, delete-orphan")


class DocumentEmbedding(Base):
    __tablename__ = "document_embeddings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    chunk_id = Column(String(36), ForeignKey("document_chunks.id", ondelete="CASCADE"), nullable=False, index=True)
    embedding_json = Column(Text, nullable=False)  # JSON serialized vector representation
    model_name = Column(String(100), default="gemini-embedding-001")
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

    chunk = relationship("DocumentChunk", back_populates="embeddings")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(String(36), ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), default="Academic Consultation")
    created_at = Column(DateTime(timezone=True), default=get_utc_now)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now)

    user = relationship("User", back_populates="conversations")
    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan", order_by="ChatMessage.created_at")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_role = Column(String(20), nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    citations_json = Column(Text, nullable=True)  # JSON list of citations: [{doc_title, page, snippet}]
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

    conversation = relationship("Conversation", back_populates="messages")


class Note(Base):
    __tablename__ = "notes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(String(36), ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True)
    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="SET NULL"), nullable=True)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    note_type = Column(String(50), nullable=False, default="detailed") 
    # short, detailed, chapter_wise, exam_oriented, revision, definitions, key_points, questions
    title = Column(String(255), nullable=False)
    content_markdown = Column(Text, nullable=False)
    is_pinned = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=get_utc_now)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now)

    user = relationship("User", back_populates="notes")


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(String(36), ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True)
    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="SET NULL"), nullable=True)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    note_id = Column(String(36), ForeignKey("notes.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    difficulty = Column(String(20), default="medium")  # easy, medium, hard, mixed
    total_questions = Column(Integer, default=5)
    time_limit_mins = Column(Integer, default=15)
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

    user = relationship("User", back_populates="quizzes")
    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan", order_by="Question.id")
    attempts = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    quiz_id = Column(String(36), ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False, index=True)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), default="mcq")  # mcq, multiple_select, short_answer, long_answer, technical_interview, programming, scenario_based, application_oriented
    options_json = Column(Text, nullable=True)  # JSON array of options
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)
    points = Column(Integer, default=1)
    code_snippet = Column(Text, nullable=True)
    test_cases_json = Column(Text, nullable=True)
    quiz = relationship("Quiz", back_populates="questions")

    @property
    def options(self) -> list:
        if self.options_json:
            try:
                return json.loads(self.options_json)
            except Exception:
                return []
        return []

    @property
    def test_cases(self) -> list:
        if self.test_cases_json:
            try:
                return json.loads(self.test_cases_json)
            except Exception:
                return []
        return []


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    quiz_id = Column(String(36), ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False, index=True)
    score = Column(Float, nullable=False)
    max_score = Column(Float, nullable=False)
    percentage = Column(Float, nullable=False)
    time_taken_seconds = Column(Integer, default=0)
    completed_at = Column(DateTime(timezone=True), default=get_utc_now)

    user = relationship("User", back_populates="quiz_attempts")
    quiz = relationship("Quiz", back_populates="attempts")
    answers = relationship("UserAnswer", back_populates="attempt", cascade="all, delete-orphan")


class UserAnswer(Base):
    __tablename__ = "user_answers"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    attempt_id = Column(String(36), ForeignKey("quiz_attempts.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(String(36), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    user_response = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    score_awarded = Column(Float, default=0.0)
    feedback = Column(Text, nullable=True)

    attempt = relationship("QuizAttempt", back_populates="answers")
    question = relationship("Question")


class TopicPerformance(Base):
    __tablename__ = "topic_performances"
    __table_args__ = (
        UniqueConstraint("user_id", "topic_id", name="uq_user_topic_performance"),
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(String(36), ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    total_attempts = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    incorrect_answers = Column(Integer, default=0)
    accuracy_percentage = Column(Float, default=0.0)
    mastery_status = Column(String(30), default="needs_practice")  # needs_practice, developing, proficient, mastered
    last_practiced_at = Column(DateTime(timezone=True), default=get_utc_now)

    user = relationship("User", back_populates="topic_performances")
    subject = relationship("Subject")
    topic = relationship("Topic", back_populates="topic_performances")


class CareerRole(Base):
    __tablename__ = "career_roles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), unique=True, nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)
    salary_range = Column(String(100), nullable=True)
    industry_demand = Column(String(50), default="High")
    icon_name = Column(String(50), default="Briefcase")

    skill_requirements = relationship("CareerSkillRequirement", back_populates="career_role", cascade="all, delete-orphan")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), unique=True, nullable=False, index=True)
    category = Column(String(100), default="Technical")
    description = Column(Text, nullable=True)


class SubjectSkillMapping(Base):
    __tablename__ = "subject_skill_mappings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    subject_id = Column(String(36), ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    competency_name = Column(String(255), nullable=False)
    skill_id = Column(String(36), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)
    career_role_id = Column(String(36), ForeignKey("career_roles.id", ondelete="CASCADE"), nullable=False, index=True)

    subject = relationship("Subject")
    topic = relationship("Topic")
    skill = relationship("Skill")
    career_role = relationship("CareerRole")


class CareerSkillRequirement(Base):
    __tablename__ = "career_skill_requirements"
    __table_args__ = (
        UniqueConstraint("career_role_id", "skill_id", name="uq_career_role_skill_req"),
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    career_role_id = Column(String(36), ForeignKey("career_roles.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(String(36), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)
    importance_level = Column(String(50), default="Core")  # Core, Secondary, Advanced
    min_proficiency = Column(Float, default=70.0)  # Percentage score threshold

    career_role = relationship("CareerRole", back_populates="skill_requirements")
    skill = relationship("Skill")


class UserSkill(Base):
    __tablename__ = "user_skills"
    __table_args__ = (
        UniqueConstraint("user_id", "skill_id", name="uq_user_skill"),
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(String(36), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)
    proficiency_level = Column(Float, default=0.0)  # 0 to 100
    source = Column(String(50), default="demonstrated")  # demonstrated, self_reported
    evidence_notes = Column(Text, nullable=True)
    verified = Column(Boolean, default=False)
    last_evaluated_at = Column(DateTime(timezone=True), default=get_utc_now)

    user = relationship("User", back_populates="user_skills")
    skill = relationship("Skill")


class CareerRecommendation(Base):
    __tablename__ = "career_recommendations"
    __table_args__ = (
        UniqueConstraint("user_id", "career_role_id", name="uq_user_career_recommendation"),
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    career_role_id = Column(String(36), ForeignKey("career_roles.id", ondelete="CASCADE"), nullable=False, index=True)
    match_score = Column(Float, nullable=False)  # 0 to 100
    rationale = Column(Text, nullable=False)
    missing_skills_count = Column(Integer, default=0)
    recommended_at = Column(DateTime(timezone=True), default=get_utc_now)

    user = relationship("User", back_populates="career_recommendations")
    career_role = relationship("CareerRole")


class SkillGap(Base):
    __tablename__ = "skill_gaps"
    __table_args__ = (
        UniqueConstraint("user_id", "career_role_id", "skill_id", name="uq_user_career_skill_gap"),
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    career_role_id = Column(String(36), ForeignKey("career_roles.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(String(36), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), default="missing")  # existing, missing, needs_improvement
    priority = Column(String(20), default="High")  # High, Medium, Low
    learning_recommendation = Column(Text, nullable=True)

    user = relationship("User", back_populates="skill_gaps")
    career_role = relationship("CareerRole")
    skill = relationship("Skill")


class CareerRoadmap(Base):
    __tablename__ = "career_roadmaps"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    career_role_id = Column(String(36), ForeignKey("career_roles.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    target_timeline_months = Column(Integer, default=6)
    progress_percentage = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=get_utc_now)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now)

    user = relationship("User", back_populates="career_roadmaps")
    career_role = relationship("CareerRole")
    milestones = relationship("RoadmapMilestone", back_populates="roadmap", cascade="all, delete-orphan", order_by="RoadmapMilestone.order_index")


class RoadmapMilestone(Base):
    __tablename__ = "roadmap_milestones"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    roadmap_id = Column(String(36), ForeignKey("career_roadmaps.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    order_index = Column(Integer, default=0)
    is_completed = Column(Boolean, default=False)
    target_date = Column(String(50), nullable=True)
    suggested_projects_json = Column(Text, nullable=True)  # JSON array of project titles & descriptions
    practice_activities_json = Column(Text, nullable=True)  # JSON array of activities

    roadmap = relationship("CareerRoadmap", back_populates="milestones")


class StudyPlan(Base):
    __tablename__ = "study_plans"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    start_date = Column(DateTime(timezone=True), default=get_utc_now)
    end_date = Column(DateTime(timezone=True), nullable=True)
    daily_hours_target = Column(Float, default=2.0)
    status = Column(String(30), default="active")  # active, completed, archived
    exam_date = Column(String(30), nullable=True)  # YYYY-MM-DD
    learning_priority = Column(String(50), default="balanced")  # weak_topics_first, exam_prep, career_skills, balanced
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

    user = relationship("User", back_populates="study_plans")
    tasks = relationship("StudyTask", back_populates="study_plan", cascade="all, delete-orphan", order_by="StudyTask.scheduled_date")


class StudyTask(Base):
    __tablename__ = "study_tasks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    study_plan_id = Column(String(36), ForeignKey("study_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    scheduled_date = Column(String(30), nullable=False)  # YYYY-MM-DD
    duration_minutes = Column(Integer, default=45)
    priority = Column(String(20), default="Medium")  # High, Medium, Low
    task_type = Column(String(50), default="study")  # study, revision, quiz, career_project, exam_prep
    difficulty_level = Column(String(30), default="medium")  # easy, medium, hard
    action_url = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    study_plan = relationship("StudyPlan", back_populates="tasks")
    topic = relationship("Topic")


class LearningProfile(Base):
    __tablename__ = "learning_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    preferred_language = Column(String(20), default="en")  # en, te, hi, ta, kn, ml, bn, mr, ur, es, fr, de, ja, zh
    explanation_style = Column(String(50), default="step_by_step")  # beginner, intermediate, advanced, step_by_step, real_world, exam_oriented
    daily_goal_minutes = Column(Integer, default=45)
    target_career_id = Column(String(36), ForeignKey("career_roles.id", ondelete="SET NULL"), nullable=True)
    learning_preferences_json = Column(Text, nullable=True)  # JSON object with user preferences
    created_at = Column(DateTime(timezone=True), default=get_utc_now)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now)

    user = relationship("User", back_populates="learning_profile")
    target_career = relationship("CareerRole")

    @property
    def preferences(self) -> dict:
        if self.learning_preferences_json:
            try:
                return json.loads(self.learning_preferences_json)
            except Exception:
                return {}
        return {}


class QuizMistake(Base):
    __tablename__ = "quiz_mistakes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    quiz_attempt_id = Column(String(36), ForeignKey("quiz_attempts.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(String(36), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="SET NULL"), nullable=True, index=True)
    error_category = Column(String(60), nullable=False, default="conceptual_misunderstanding")
    # conceptual_misunderstanding, incorrect_application, calculation_error, misinterpretation, knowledge_gap, unclassified
    user_response = Column(Text, nullable=False)
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text, nullable=False)
    suggested_fix = Column(Text, nullable=True)
    repeated_count = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

    user = relationship("User", back_populates="quiz_mistakes")
    quiz_attempt = relationship("QuizAttempt")
    question = relationship("Question")
    topic = relationship("Topic")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False, default="task_reminder")
    # revision_due, task_reminder, weak_topic_alert, career_milestone, quiz_feedback
    is_read = Column(Boolean, default=False)
    action_url = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

    user = relationship("User", back_populates="notifications")


class CareerProject(Base):
    __tablename__ = "career_projects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    career_role_id = Column(String(36), ForeignKey("career_roles.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    objective = Column(Text, nullable=False)
    difficulty = Column(String(50), default="Intermediate")  # Beginner, Intermediate, Advanced
    required_skills_json = Column(Text, nullable=False)  # JSON array
    tools_json = Column(Text, nullable=False)  # JSON array
    steps_json = Column(Text, nullable=False)  # JSON array of implementation steps
    expected_outcome = Column(Text, nullable=False)
    competency_focus = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

    career_role = relationship("CareerRole")

    @property
    def required_skills(self) -> list:
        try:
            return json.loads(self.required_skills_json) if self.required_skills_json else []
        except Exception:
            return []

    @property
    def tools(self) -> list:
        try:
            return json.loads(self.tools_json) if self.tools_json else []
        except Exception:
            return []

    @property
    def steps(self) -> list:
        try:
            return json.loads(self.steps_json) if self.steps_json else []
        except Exception:
            return []


class CareerPathway(Base):
    __tablename__ = "career_pathways"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    from_role_id = Column(String(36), ForeignKey("career_roles.id", ondelete="CASCADE"), nullable=False, index=True)
    to_role_id = Column(String(36), ForeignKey("career_roles.id", ondelete="CASCADE"), nullable=False, index=True)
    transition_difficulty = Column(String(50), default="Moderate")  # Smooth, Moderate, Challenging
    bridge_skills_json = Column(Text, nullable=False)  # JSON array
    guidance = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

    from_role = relationship("CareerRole", foreign_keys=[from_role_id])
    to_role = relationship("CareerRole", foreign_keys=[to_role_id])

    @property
    def bridge_skills(self) -> list:
        try:
            return json.loads(self.bridge_skills_json) if self.bridge_skills_json else []
        except Exception:
            return []


import os
from sqlalchemy import event

@event.listens_for(Document, "after_delete")
def cleanup_document_file_after_delete(mapper, connection, target):
    """
    Guarantees physical file cleanup when Document records are deleted directly
    or through cascade deletions when parent Users are removed.
    """
    if target and getattr(target, "file_path", None) and os.path.exists(target.file_path):
        try:
            os.remove(target.file_path)
        except Exception:
            pass


