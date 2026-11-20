# EduPath AI – Intelligent Learning & Career Ecosystem
> **Learn Smarter. Grow Better. Build Your Career.**

EduPath AI is an integrated platform connecting academic learning with industry skills and career preparation. Built with a **Next.js 14** frontend (styled in a **Premium Dark Black + Glowing Purple** SaaS aesthetic) and a high-performance **Python FastAPI** backend powered by **Google Gemini API**, **Retrieval-Augmented Generation (RAG)**, and **Supabase PostgreSQL with pgvector**.

---

## 🌟 The Core Differentiator: Central EduPath Intelligence Engine

Unlike disconnected standalone educational tools, EduPath AI features a unified **Intelligence Engine** connecting all learning activities into a cohesive career development lifecycle:

```
[ Upload PDF/DOCX ] 
       │
       ▼
[ AI Study Assistant (RAG + Page Citations) ] 
       │
       ▼
[ AI Quiz Generator (MCQs & Short-Answers) ] 
       │
       ▼
[ Quiz Submission & Topic Performance Tracking ] 
  (Repeated evidence standards: Needs Practice → Developing → Proficient → Mastered)
       │
       ▼
[ Academic-to-Industry Skill Mapping ] 
  (Subject → Topic → Industry Competency → Skill → Career Role)
       │
       ▼
[ Career Intelligence & Recommendations (8 Core Roles) ] 
       │
       ▼
[ Skill Gap Analysis (Demonstrated vs Self-Reported vs Missing) ] 
       │
       ▼
[ Personalized Career Roadmap (Phased Milestones & Projects) ] 
       │
       ▼
[ AI Adaptive Study Planner (Non-overlapping Daily Schedule) ]
```

---

## 🎨 Design System: Premium Dark Black + Glowing Purple

- **Main Background**: `#08060D`
- **Secondary Background**: `#100B18`
- **Sidebar**: `#120D1C`
- **Cards**: `#191225`
- **Primary Purple**: `#8B5CF6`
- **Neon Purple**: `#A855F7`
- **Bright Violet**: `#C084FC`
- **Light Purple**: `#D8B4FE`
- **Main Text**: `#FFFFFF`
- **Secondary Text**: `#A1A1AA`
- **Borders**: `#30203F`

---

## 🚀 The 12 Required Platform Features

1. **AI Study Assistant** (`/dashboard/assistant`): Academic Q&A, intuitive step-by-step explanations, grounded RAG document context, and exact page citations.
2. **Smart Notes Generator** (`/dashboard/notes`): Generate notes across 8 specialized formats (short, detailed, chapter-wise, exam-oriented, revision, definitions, key points, questions) with Markdown editing, saving, and pinning.
3. **AI Quiz Generator** (`/dashboard/quiz`): Generate MCQs (4 options) and short-answer assessments with difficulty levels. Answer keys are strictly hidden until submission, followed by detailed pedagogical explanations.
4. **Learning Analytics Dashboard** (`/dashboard/analytics`): Verified real user metrics, quiz volume trends, and weak topic alerts via Recharts.
5. **Topic-wise Performance Tracking** (`/dashboard/topics`): Tracks accuracy percentages, attempts, and mastery badges based on repeated assessment evidence.
6. **Career Intelligence & Recommendations** (`/dashboard/careers`): Evaluates 8 core tech roles (Python Dev, Data Analyst, Data Scientist, Web Dev, Backend Dev, Database Dev, ML Engineer, Cybersecurity Analyst) with objective readiness rationales and no false employment guarantees.
7. **Academic-to-Industry Skill Mapping** (`/dashboard/skill-mapping`): Structured taxonomy graph mapping course topics to industry competencies, verified skills, and career roles.
8. **Skill Gap Identification** (`/dashboard/skill-gaps`): Compares career skill requirements against verified student evidence, distinguishing demonstrated skills from self-reported skills.
9. **Personalized Career Roadmap** (`/dashboard/roadmaps`): Generates sequenced milestone phases, suggested portfolio projects, practice activities, and milestone completion tracking.
10. **AI Study Planner** (`/dashboard/study-planner`): Adaptive daily and weekly task schedules prioritizing weak topics, with non-overlapping tasks and rescheduling capabilities.
11. **Document Upload & Management** (`/dashboard/documents`): Secure upload of PDF/DOCX files, extraction via PyMuPDF/python-docx, semantic chunking, and pgvector embeddings.
12. **AI Chat History** (`/dashboard/chat-history`): Persisted chat sessions, transcript inspection, conversation renaming, and continuation.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | Next.js 14, React 18, TypeScript, Tailwind CSS, Recharts, Lucide React |
| **Backend** | Python 3.11+, FastAPI, Pydantic V2, SQLAlchemy (Async), Uvicorn |
| **Database** | PostgreSQL / Supabase, pgvector extension, SQLite fallback |
| **AI / RAG** | Google Gemini API (`gemini-1.5-flash`), Semantic Chunking & Vector Retrieval |
| **Document Processing** | PyMuPDF (fitz), python-docx |
| **Security** | JWT (HS256), bcrypt password hashing, Row Level Security (RLS) policies |

---

## 📦 Getting Started

### 1. Prerequisites
- Python 3.11+
- Node.js 18+ (Node 24 supported)
- npm 9+

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.\.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# (Optional) Configure environment
cp .env.example .env
# Edit .env with your GEMINI_API_KEY and DATABASE_URL if using Supabase

# Initialize Database & Taxonomy Seed Data
python -m app.core.init_db

# Run Backend Server
uvicorn app.main:app --reload --port 8000
```
Backend API docs will be live at: `http://127.0.0.1:8000/docs`

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Run Frontend Development Server
npm run dev
```
Frontend application will be live at: `http://localhost:3000`

---

## 🧪 Automated Testing

### Backend Test Suite
Run the automated pytest test suite covering authentication, RAG, quizzes, and intelligence engine recalculation:
```bash
cd backend
.\.venv\Scripts\pytest -v
```

All 5 test suites verify:
- Health and Root endpoints
- JWT registration and demo login
- Academic-to-industry taxonomy mapping
- AI Quiz generation with masked answer keys and evaluation
- Study assistant citations and note generation

---

## 🔒 Security Architecture
- All AI keys and database secrets reside securely on the backend.
- Prompts include anti-injection defenses treating uploaded documents as untrusted input.
- Quiz answer keys are strictly hidden until submission.
- Complete Row Level Security (RLS) policies are provided in `backend/supabase_schema.sql`.

---

## 📄 License
MIT License. Built for EduPath AI – Intelligent Learning & Career Ecosystem.
