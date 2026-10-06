from pydantic import BaseModel


class ContactInfo(BaseModel):
    email: str | None = None
    phone: str | None = None


class AIInsights(BaseModel):
    candidate_summary: str
    strengths: list[str]
    weaknesses: list[str]
    resume_improvements: list[str]
    technical_questions: list[str]
    behavioral_questions: list[str]
    recommendation: str


class CandidateResult(BaseModel):
    rank: int
    name: str
    filename: str
    ats_score: float
    semantic_score: float
    skill_coverage: float
    decision: str
    matched_skills: list[str]
    missing_skills: list[str]
    contact: ContactInfo
    ai: AIInsights | None = None


class ScreenResponse(BaseModel):
    job_description_skills: list[str]
    total_candidates: int
    candidates: list[CandidateResult]


class ResumeExtractResponse(BaseModel):
    filename: str
    name: str
    contact: ContactInfo
    sections: dict[str, str]
    detected_skills: list[str]
    preview_text: str


class HealthResponse(BaseModel):
    status: str
    embedding_model: str
    llm_configured: bool
    total_skills_tracked: int
