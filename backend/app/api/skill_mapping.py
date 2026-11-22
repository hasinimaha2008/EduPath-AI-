from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.models.models import Subject, Topic, Skill, CareerRole, SubjectSkillMapping
from app.schemas.schemas import SubjectResponse, SkillResponse, SubjectSkillMappingResponse

router = APIRouter(prefix="/skills", tags=["Academic-to-Industry Skill Mapping"])

@router.get("/subjects", response_model=List[SubjectResponse])
async def list_subjects(session: AsyncSession = Depends(get_db)):
    stmt = select(Subject).options(selectinload(Subject.topics)).order_by(Subject.name)
    res = await session.execute(stmt)
    subjects = res.scalars().all()
    return [SubjectResponse.model_validate(s) for s in subjects]

@router.get("/catalog", response_model=List[SkillResponse])
async def list_skills(session: AsyncSession = Depends(get_db)):
    stmt = select(Skill).order_by(Skill.category, Skill.name)
    res = await session.execute(stmt)
    skills = res.scalars().all()
    return [SkillResponse.model_validate(s) for s in skills]

@router.get("/mappings", response_model=List[SubjectSkillMappingResponse])
async def list_subject_skill_mappings(session: AsyncSession = Depends(get_db)):
    """
    Returns the complete Academic Subject -> Topic -> Industry Competency -> Skill -> Career Role graph.
    """
    stmt = select(
        SubjectSkillMapping.id,
        Subject.name.label("subject_name"),
        Topic.name.label("topic_name"),
        SubjectSkillMapping.competency_name,
        Skill.name.label("skill_name"),
        CareerRole.title.label("career_role_title")
    ).join(
        Subject, SubjectSkillMapping.subject_id == Subject.id
    ).join(
        Topic, SubjectSkillMapping.topic_id == Topic.id
    ).join(
        Skill, SubjectSkillMapping.skill_id == Skill.id
    ).join(
        CareerRole, SubjectSkillMapping.career_role_id == CareerRole.id
    ).order_by(Subject.name, Topic.name)

    res = await session.execute(stmt)
    rows = res.all()

    APPLICATION_KNOWLEDGE_MAP = {
        "SQL Querying": {
            "app": "In production software systems, relational data modeling and complex SQL queries enforce ACID transactional integrity and eliminate redundancy across financial ledgers, inventory trackers, and customer records.",
            "proj": "Architecting an e-commerce multi-tenant PostgreSQL relational schema with window functions for revenue cohort analysis and automated partition management."
        },
        "Database Design & Normalization": {
            "app": "Normalization (3NF/BCNF) prevents update, insertion, and deletion anomalies, safeguarding multi-user enterprise applications against corrupted or orphan records during high-concurrency writes.",
            "proj": "Refactoring an unnormalized monolithic billing table into 3NF decoupled entities with composite foreign key integrity and immutable audit triggers."
        },
        "Query Optimization": {
            "app": "Query optimization and index tuning (B+ Trees, GiST) reduce database IOPS, lowering p99 response times from 800ms to sub-5ms under high concurrent query loads.",
            "proj": "Optimizing a high-volume product catalog search using compound B-Tree indexes, partial indexing, and EXPLAIN ANALYZE profiling."
        },
        "Operating System Architecture": {
            "app": "Concurrency synchronization primitives (mutexes, semaphores, condition variables) prevent race conditions and data corruption in high-throughput multithreaded servers and cloud container runtimes.",
            "proj": "Building a thread-safe asynchronous connection pool and background worker queue with deadlock detection and backpressure management."
        },
        "Network Protocol Analysis": {
            "app": "Transport security (TLS 1.3) and protocol multiplexing (HTTP/2, HTTP/3) ensure zero-trust data protection and low-latency client-server handshakes across global cloud edge nodes.",
            "proj": "Configuring a reverse proxy gateway with automated TLS certificate rotation, HTTP/2 multiplexing, and mutual authentication."
        },
        "Algorithms & Optimization": {
            "app": "Graph traversal, topological sorting, and shortest-path algorithms power route optimization in logistics, dependency graph resolution in build systems, and recommendation engines.",
            "proj": "Developing an automated package dependency resolver and cycle detector using Tarjan's strongly connected components algorithm."
        },
        "Python Programming": {
            "app": "Asynchronous event loops (AsyncIO) and robust type hinting allow rapid development of high-throughput microservices, data ingest pipelines, and AI agent orchestrators.",
            "proj": "Building an asynchronous background task queue with Redis Streams, exponential backoff retries, and dead-letter queue routing."
        },
        "Machine Learning & Predictive Modeling": {
            "app": "Supervised and unsupervised statistical learning models automate fraud detection, credit risk scoring, user churn forecasting, and demand planning at enterprise scale.",
            "proj": "Deploying a real-time transaction fraud classification API with Scikit-learn, MLflow tracking, and SHAP explainability reports."
        },
        "Deep Learning & Transformers": {
            "app": "Attention mechanisms and Transformer architectures power enterprise semantic search, conversational AI agents, document question-answering, and autonomous multimodal assistants.",
            "proj": "Constructing an enterprise RAG retrieval pipeline combining dense vector embeddings with cross-encoder reranking and streaming LLM responses."
        },
        "Cloud Architecture & DevOps": {
            "app": "Infrastructure as Code (Terraform) and container orchestration (Kubernetes) enable automated zero-downtime rolling deployments, self-healing, and elastic auto-scaling.",
            "proj": "Provisioning a multi-AZ Kubernetes cluster with automated GitOps continuous deployment using ArgoCD and Prometheus monitoring."
        },
        "Cybersecurity & Defensive Controls": {
            "app": "Defensive controls and secure coding practices mitigate OWASP Top 10 vulnerabilities (SQLi, XSS, SSRF), protecting enterprise assets from malicious intrusion and data exfiltration.",
            "proj": "Building an automated web application vulnerability scanner and packet inspection utility using Python and Scapy."
        },
        "Modern React & Web Engineering": {
            "app": "Component-driven reactive architectures with optimistic UI updates and accessibility standards deliver responsive, accessible, and high-performance digital interfaces across devices.",
            "proj": "Developing a real-time collaborative workspace with Next.js 14, WebSockets, optimistic UI updates, and WCAG AAA compliance."
        }
    }

    output = []
    for r in rows:
        mapping_info = APPLICATION_KNOWLEDGE_MAP.get(r.skill_name, {
            "app": f"Knowledge of {r.topic_name} ({r.competency_name}) underpins reliable engineering decisions and scalable architecture in {r.career_role_title} production systems.",
            "proj": f"Designing and evaluating an end-to-end practical implementation module applying {r.competency_name} to production user workflows."
        })

        output.append(
            SubjectSkillMappingResponse(
                id=r.id,
                subject_name=r.subject_name,
                topic_name=r.topic_name,
                competency_name=r.competency_name,
                skill_name=r.skill_name,
                career_role_title=r.career_role_title,
                industry_application=mapping_info["app"],
                practical_project_example=mapping_info["proj"]
            )
        )

    return output
