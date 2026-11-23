"""
EduPath AI - Career Intelligence & Job Description Analysis.
Extracts required technical skills from job descriptions, analyzes student skill gaps,
differentiates verified demonstrated vs self-reported skills, and recommends bridge projects.
"""

import re
import json
import logging
from typing import List, Dict, Any, Optional
from app.services.ai.provider import llm_provider

logger = logging.getLogger("edupath.ai.career_analyzer")

COMMON_TECH_SKILLS = [
    "Python", "JavaScript", "TypeScript", "SQL", "Java", "C++", "Go", "Rust", "C#",
    "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite", "DynamoDB", "Cassandra",
    "FastAPI", "Django", "Flask", "Node.js", "Express", "React", "Next.js", "Vue", "Angular",
    "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Terraform", "CI/CD", "Git", "Linux",
    "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "NLP", "Computer Vision",
    "Data Structures", "Algorithms", "System Design", "Microservices", "REST API", "GraphQL",
    "Cybersecurity", "Cryptography", "Network Security", "Agile", "Scrum"
]

class CareerAnalyzerService:
    async def analyze_job_description(
        self,
        job_title: str,
        job_description_text: str,
        user_skills: List[Dict[str, Any]],
        company_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Parses raw job description text and compares against persisted student skills.
        Differentiates demonstrated skills (verified by assessments) from self-reported skills.
        """
        # 1. Extract required skills from text
        extracted_skills = self._extract_skills(job_description_text)
        if not extracted_skills:
            # Fallback based on job title
            extracted_skills = self._get_fallback_skills_for_title(job_title)

        # 2. Partition user skills into demonstrated vs self-reported
        demonstrated_skill_names = set()
        self_reported_skill_names = set()

        for s in user_skills:
            name = s.get("skill_name", "").strip()
            if not name:
                continue
            is_demonstrated = s.get("is_demonstrated", False) or s.get("demonstrated_score", 0.0) >= 50.0
            if is_demonstrated:
                demonstrated_skill_names.add(name.lower())
            else:
                self_reported_skill_names.add(name.lower())

        # 3. Compute match and gap lists
        demonstrated_matches = []
        self_reported_matches = []
        missing_skills = []

        for req in extracted_skills:
            req_lower = req.lower()
            if req_lower in demonstrated_skill_names:
                demonstrated_matches.append(req)
            elif req_lower in self_reported_skill_names:
                self_reported_matches.append(req)
            else:
                missing_skills.append(req)

        total_required = max(len(extracted_skills), 1)
        total_matched = len(demonstrated_matches) + (len(self_reported_matches) * 0.5)
        overall_match = min(100.0, round((total_matched / total_required) * 100.0, 1))
        demonstrated_match = min(100.0, round((len(demonstrated_matches) / total_required) * 100.0, 1))

        if demonstrated_match >= 75.0:
            readiness = "Ready for Application"
        elif overall_match >= 60.0:
            readiness = "Near Ready (Minor Skill Gaps)"
        elif overall_match >= 35.0:
            readiness = "In Progress (Moderate Gaps)"
        else:
            readiness = "Significant Bridge Needed"

        # 4. Recommend concrete bridge projects
        bridge_projects = self._recommend_bridge_projects(job_title, missing_skills)

        # 5. Summary analysis
        summary = (
            f"Analysis of {job_title}" + (f" at {company_name}" if company_name else "") + ": "
            f"Extracted {len(extracted_skills)} core technical competencies. "
            f"You possess {len(demonstrated_matches)} verified demonstrated skills and "
            f"{len(self_reported_matches)} self-reported skills, leaving {len(missing_skills)} skill gaps. "
            f"Current verified readiness score: {demonstrated_match}%."
        )

        return {
            "job_title": job_title,
            "company_name": company_name or "Target Company",
            "extracted_required_skills": extracted_skills,
            "demonstrated_matching_skills": demonstrated_matches,
            "self_reported_matching_skills": self_reported_matches,
            "missing_skill_gaps": missing_skills,
            "overall_match_percentage": overall_match,
            "demonstrated_match_percentage": demonstrated_match,
            "readiness_status": readiness,
            "recommended_bridge_projects": bridge_projects,
            "summary_analysis": summary
        }

    def _extract_skills(self, text: str) -> List[str]:
        text_lower = text.lower()
        matched = []
        for skill in COMMON_TECH_SKILLS:
            pattern = r"\b" + re.escape(skill.lower()) + r"\b"
            if re.search(pattern, text_lower):
                matched.append(skill)
        return matched

    def _get_fallback_skills_for_title(self, title: str) -> List[str]:
        t_lower = title.lower()
        if "backend" in t_lower or "python" in t_lower:
            return ["Python", "FastAPI", "SQL", "PostgreSQL", "Docker", "Git", "REST API"]
        elif "frontend" in t_lower or "react" in t_lower:
            return ["JavaScript", "TypeScript", "React", "Next.js", "Tailwind CSS", "Git", "REST API"]
        elif "data" in t_lower or "ai" in t_lower or "machine" in t_lower:
            return ["Python", "SQL", "Machine Learning", "Deep Learning", "TensorFlow", "Pandas", "Docker"]
        elif "cloud" in t_lower or "devops" in t_lower:
            return ["Linux", "Docker", "Kubernetes", "AWS", "CI/CD", "Terraform", "Python"]
        elif "security" in t_lower or "cyber" in t_lower:
            return ["Cybersecurity", "Network Security", "Linux", "Cryptography", "Python", "SQL"]
        return ["Python", "SQL", "Git", "Data Structures", "Algorithms", "System Design"]

    def _recommend_bridge_projects(self, role_title: str, missing_skills: List[str]) -> List[Dict[str, Any]]:
        projects = []
        missing_set = set(s.lower() for s in missing_skills)

        if any(s in missing_set for s in ("docker", "kubernetes", "ci/cd", "aws")):
            projects.append({
                "title": "Cloud-Native Containerized Microservice Pipeline",
                "description": "Deploy a multi-service web application with Docker containerization, Kubernetes manifests, and automated GitHub Actions CI/CD.",
                "skills_targeted": [s for s in missing_skills if s.lower() in ("docker", "kubernetes", "ci/cd", "aws", "linux")][:3],
                "difficulty": "Intermediate"
            })

        if any(s in missing_set for s in ("postgresql", "sql", "redis", "fastapi")):
            projects.append({
                "title": "High-Throughput Distributed Cache & Persistence Engine",
                "description": "Build an asynchronous RESTful API with PostgreSQL relational models, Redis caching, and connection pooling.",
                "skills_targeted": [s for s in missing_skills if s.lower() in ("postgresql", "sql", "redis", "fastapi", "python")][:3],
                "difficulty": "Advanced"
            })

        if any(s in missing_set for s in ("react", "typescript", "next.js")):
            projects.append({
                "title": "Real-Time SaaS Collaborative Dashboard",
                "description": "Construct an interactive dashboard in Next.js and TypeScript utilizing server-sent events (SSE) and responsive Tailwind styling.",
                "skills_targeted": [s for s in missing_skills if s.lower() in ("react", "typescript", "next.js", "javascript")][:3],
                "difficulty": "Intermediate"
            })

        if not projects:
            projects.append({
                "title": "End-to-End Production Technical Showcase",
                "description": f"Build an enterprise portfolio application demonstrating core competencies for {role_title}.",
                "skills_targeted": missing_skills[:3] if missing_skills else ["System Design", "Architecture"],
                "difficulty": "Intermediate"
            })

        return projects

career_analyzer = CareerAnalyzerService()
