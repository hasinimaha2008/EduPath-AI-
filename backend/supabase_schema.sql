-- ==============================================================================
-- EDUPATH AI – POSTGRESQL & SUPABASE PRODUCTION DDL
-- Intelligent Learning & Career Ecosystem
-- Includes: pgvector, 24 normalized tables, foreign keys, indexes, and RLS policies
-- ==============================================================================

-- 1. Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- 2. Users / Profiles
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    avatar_url VARCHAR(512),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- 3. Academic Subjects
CREATE TABLE IF NOT EXISTS subjects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) UNIQUE NOT NULL,
    code VARCHAR(50),
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Academic Topics
CREATE TABLE IF NOT EXISTS topics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subject_id UUID NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    order_index INT DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_topics_subject ON topics(subject_id);

-- 5. Uploaded Documents
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject_id UUID REFERENCES subjects(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(512) NOT NULL,
    file_size INT NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'processing',
    error_message TEXT,
    chunk_count INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_documents_user ON documents(user_id);

-- 6. Document Chunks
CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INT NOT NULL,
    content TEXT NOT NULL,
    page_number INT DEFAULT 1,
    token_count INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_document_chunks_doc ON document_chunks(document_id);

-- 7. Document Embeddings with pgvector
CREATE TABLE IF NOT EXISTS document_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chunk_id UUID NOT NULL REFERENCES document_chunks(id) ON DELETE CASCADE,
    embedding vector(768), -- Gemini 768-dim embeddings
    model_name VARCHAR(100) DEFAULT 'models/text-embedding-004',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_doc_embeddings_chunk ON document_embeddings(chunk_id);

-- 8. Conversations & Chat History
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject_id UUID REFERENCES subjects(id) ON DELETE SET NULL,
    document_id UUID REFERENCES documents(id) ON DELETE SET NULL,
    title VARCHAR(255) DEFAULT 'Academic Consultation',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_conversations_user ON conversations(user_id);

-- 9. Chat Messages
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    sender_role VARCHAR(20) NOT NULL, -- 'user' or 'assistant'
    content TEXT NOT NULL,
    citations_json JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_chat_messages_conv ON chat_messages(conversation_id);

-- 10. Smart Notes
CREATE TABLE IF NOT EXISTS notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject_id UUID REFERENCES subjects(id) ON DELETE SET NULL,
    topic_id UUID REFERENCES topics(id) ON DELETE SET NULL,
    document_id UUID REFERENCES documents(id) ON DELETE SET NULL,
    note_type VARCHAR(50) NOT NULL DEFAULT 'detailed',
    title VARCHAR(255) NOT NULL,
    content_markdown TEXT NOT NULL,
    is_pinned BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_notes_user ON notes(user_id);

-- 11. AI Quizzes
CREATE TABLE IF NOT EXISTS quizzes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject_id UUID REFERENCES subjects(id) ON DELETE SET NULL,
    topic_id UUID REFERENCES topics(id) ON DELETE SET NULL,
    document_id UUID REFERENCES documents(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    difficulty VARCHAR(20) DEFAULT 'medium',
    total_questions INT DEFAULT 5,
    time_limit_mins INT DEFAULT 15,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_quizzes_user ON quizzes(user_id);

-- 12. Quiz Questions
CREATE TABLE IF NOT EXISTS questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quiz_id UUID NOT NULL REFERENCES quizzes(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    question_type VARCHAR(20) DEFAULT 'mcq',
    options_json JSONB,
    correct_answer TEXT NOT NULL,
    explanation TEXT,
    points INT DEFAULT 1
);
CREATE INDEX IF NOT EXISTS idx_questions_quiz ON questions(quiz_id);

-- 13. Quiz Attempts
CREATE TABLE IF NOT EXISTS quiz_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    quiz_id UUID NOT NULL REFERENCES quizzes(id) ON DELETE CASCADE,
    score FLOAT NOT NULL,
    max_score FLOAT NOT NULL,
    percentage FLOAT NOT NULL,
    time_taken_seconds INT DEFAULT 0,
    completed_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_quiz_attempts_user ON quiz_attempts(user_id);

-- 14. User Answers
CREATE TABLE IF NOT EXISTS user_answers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    attempt_id UUID NOT NULL REFERENCES quiz_attempts(id) ON DELETE CASCADE,
    question_id UUID NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    user_response TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL,
    score_awarded FLOAT DEFAULT 0.0,
    feedback TEXT
);

-- 15. Topic Performance (Central Evidence Engine)
CREATE TABLE IF NOT EXISTS topic_performances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject_id UUID NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    topic_id UUID NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    total_attempts INT DEFAULT 0,
    correct_answers INT DEFAULT 0,
    incorrect_answers INT DEFAULT 0,
    accuracy_percentage FLOAT DEFAULT 0.0,
    mastery_status VARCHAR(30) DEFAULT 'needs_practice',
    last_practiced_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_user_topic UNIQUE(user_id, topic_id)
);
CREATE INDEX IF NOT EXISTS idx_topic_perf_user ON topic_performances(user_id);

-- 16. Career Roles
CREATE TABLE IF NOT EXISTS career_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) UNIQUE NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT NOT NULL,
    salary_range VARCHAR(100),
    industry_demand VARCHAR(50) DEFAULT 'High',
    icon_name VARCHAR(50) DEFAULT 'Briefcase'
);

-- 17. Skills Catalog
CREATE TABLE IF NOT EXISTS skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) UNIQUE NOT NULL,
    category VARCHAR(100) DEFAULT 'Technical',
    description TEXT
);

-- 18. Academic-to-Industry Subject Skill Mappings
CREATE TABLE IF NOT EXISTS subject_skill_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subject_id UUID NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    topic_id UUID NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    competency_name VARCHAR(255) NOT NULL,
    skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    career_role_id UUID NOT NULL REFERENCES career_roles(id) ON DELETE CASCADE
);

-- 19. Career Skill Requirements
CREATE TABLE IF NOT EXISTS career_skill_requirements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    career_role_id UUID NOT NULL REFERENCES career_roles(id) ON DELETE CASCADE,
    skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    importance_level VARCHAR(50) DEFAULT 'Core',
    min_proficiency FLOAT DEFAULT 70.0
);

-- 20. User Skills
CREATE TABLE IF NOT EXISTS user_skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    proficiency_level FLOAT DEFAULT 0.0,
    source VARCHAR(50) DEFAULT 'demonstrated',
    evidence_notes TEXT,
    verified BOOLEAN DEFAULT FALSE,
    last_evaluated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_user_skill UNIQUE(user_id, skill_id)
);

-- 21. Career Recommendations
CREATE TABLE IF NOT EXISTS career_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    career_role_id UUID NOT NULL REFERENCES career_roles(id) ON DELETE CASCADE,
    match_score FLOAT NOT NULL,
    rationale TEXT NOT NULL,
    missing_skills_count INT DEFAULT 0,
    recommended_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_user_role_rec UNIQUE(user_id, career_role_id)
);

-- 22. Skill Gaps
CREATE TABLE IF NOT EXISTS skill_gaps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    career_role_id UUID NOT NULL REFERENCES career_roles(id) ON DELETE CASCADE,
    skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'missing',
    priority VARCHAR(20) DEFAULT 'High',
    learning_recommendation TEXT,
    CONSTRAINT unique_user_role_gap UNIQUE(user_id, career_role_id, skill_id)
);

-- 23. Career Roadmaps & Milestones
CREATE TABLE IF NOT EXISTS career_roadmaps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    career_role_id UUID NOT NULL REFERENCES career_roles(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    target_timeline_months INT DEFAULT 6,
    progress_percentage FLOAT DEFAULT 0.0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS roadmap_milestones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    roadmap_id UUID NOT NULL REFERENCES career_roadmaps(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    order_index INT DEFAULT 0,
    is_completed BOOLEAN DEFAULT FALSE,
    target_date VARCHAR(50),
    suggested_projects_json JSONB,
    practice_activities_json JSONB
);

-- 24. Study Plans & Tasks
CREATE TABLE IF NOT EXISTS study_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    start_date TIMESTAMPTZ DEFAULT NOW(),
    end_date TIMESTAMPTZ,
    daily_hours_target FLOAT DEFAULT 2.0,
    status VARCHAR(30) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS study_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    study_plan_id UUID NOT NULL REFERENCES study_plans(id) ON DELETE CASCADE,
    topic_id UUID REFERENCES topics(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    scheduled_date VARCHAR(30) NOT NULL,
    duration_minutes INT DEFAULT 45,
    priority VARCHAR(20) DEFAULT 'Medium',
    is_completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMPTZ
);

-- ==============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- Ensures users can only access their own educational artifacts
-- ==============================================================================
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE quizzes ENABLE ROW LEVEL SECURITY;
ALTER TABLE quiz_attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE topic_performances ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE career_recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE skill_gaps ENABLE ROW LEVEL SECURITY;
ALTER TABLE career_roadmaps ENABLE ROW LEVEL SECURITY;
ALTER TABLE study_plans ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage their own documents" ON documents
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can manage their own notes" ON notes
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can manage their own quizzes" ON quizzes
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can manage their own quiz attempts" ON quiz_attempts
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can manage their own study plans" ON study_plans
    FOR ALL USING (auth.uid() = user_id);
