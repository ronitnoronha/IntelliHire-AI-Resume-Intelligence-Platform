from pydantic import BaseModel


class AIAnalysis(BaseModel):
    candidate_summary: str

    strengths: list[str]

    weaknesses: list[str]

    resume_improvements: list[str]

    technical_questions: list[str]

    behavioral_questions: list[str]

    recommendation: str
