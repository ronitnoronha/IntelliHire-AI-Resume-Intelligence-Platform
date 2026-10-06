import logging
import re
import sys
from pathlib import Path
from typing import Annotated

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)

from ai.llm import get_client
from backend.schemas import (
    AIInsights,
    CandidateResult,
    ContactInfo,
    HealthResponse,
    ResumeExtractResponse,
    ScreenResponse,
)
from extractor import extract_name
from jd_parser import extract_required_skills
from models import Resume
from nlp import preprocess_text
from parser import clean_resume_text, extract_text_from_pdf
from ranking import rank_resumes
from resume_parser import extract_sections
from semantic import _load_embedding_model
from skills import has_skill, skills_db

app = FastAPI(
    title="Resume Screener & ATS API",
    version="2.0.0",
    description="Modern Async REST API for Resume Screening, ATS Scoring, and Candidate Analysis",
)

# Enable CORS for local modern frontend (Vite / Next.js)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse)
def health_check():
    model = _load_embedding_model()
    model_status = (
        "SentenceTransformer (all-MiniLM-L6-v2)"
        if model
        else "TF-IDF N-Gram Vectorizer"
    )
    has_llm = get_client() is not None

    return HealthResponse(
        status="healthy",
        embedding_model=model_status,
        llm_configured=has_llm,
        total_skills_tracked=len(skills_db),
    )


@app.get("/api/skills")
def list_skills():
    """Returns the catalog of recognized skills."""
    return {"count": len(skills_db), "skills": sorted(skills_db)}


@app.post("/api/extract", response_model=ResumeExtractResponse)
async def extract_resume(file: Annotated[UploadFile, File(...)]):
    """Extracts raw content, contact info, and section breakdown from an uploaded PDF resume."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    file_bytes = await file.read()
    try:
        raw_text = extract_text_from_pdf(file_bytes)
        cleaned_text = clean_resume_text(raw_text)
        name = extract_name(file_bytes)
        sections = extract_sections(cleaned_text)

        # Detect any skills from the catalog
        detected = [skill for skill in skills_db if has_skill(skill, cleaned_text)]

        # Contact info
        emails = re.findall(
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", cleaned_text
        )
        phones = re.findall(
            r"(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3,5}\)?[-.\s]?)\d{3,5}(?:[-.\s]?\d{3,5})?|\b\d{10}\b",
            cleaned_text,
        )

        return ResumeExtractResponse(
            filename=file.filename,
            name=name,
            contact=ContactInfo(
                email=emails[0] if emails else None, phone=phones[0] if phones else None
            ),
            sections=sections,
            detected_skills=detected,
            preview_text=cleaned_text[:1200],
        )
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Failed to process resume: {e!s}")


@app.post("/api/extract-text")
async def extract_text_endpoint(file: Annotated[UploadFile, File(...)]):
    """Extracts raw cleaned text from an uploaded Job Description file (PDF, TXT, MD)."""
    file_bytes = await file.read()
    filename = file.filename.lower()
    try:
        if filename.endswith(".pdf"):
            text = clean_resume_text(extract_text_from_pdf(file_bytes))
        else:
            try:
                text = file_bytes.decode("utf-8")
            except UnicodeDecodeError:
                text = file_bytes.decode("latin-1", errors="replace")

        return {"filename": file.filename, "text": text.strip()}
    except Exception as e:  # noqa: BLE001
        raise HTTPException(
            status_code=500, detail=f"Failed to extract text from file: {e!s}"
        )


@app.post("/api/screen", response_model=ScreenResponse)
async def screen_resumes_endpoint(
    job_description: Annotated[str | None, Form()] = None,
    jd_file: Annotated[UploadFile | None, File()] = None,
    files: Annotated[list[UploadFile], File(...)] = ...,
):
    """
    Screens and ranks multiple uploaded PDF resumes against a target job description.
    Accepts job description as text or as an uploaded file (PDF/TXT/MD).
    Computes hybrid ATS scores, skill matches, and generative AI candidate insights.
    """
    final_jd = (job_description or "").strip()

    if not final_jd and jd_file:
        jd_bytes = await jd_file.read()
        if jd_file.filename.lower().endswith(".pdf"):
            final_jd = clean_resume_text(extract_text_from_pdf(jd_bytes))
        else:
            try:
                final_jd = jd_bytes.decode("utf-8").strip()
            except UnicodeDecodeError:
                final_jd = jd_bytes.decode("latin-1", errors="replace").strip()

    if not final_jd:
        raise HTTPException(
            status_code=400,
            detail="Job description must be provided either as text or as an uploaded file.",
        )

    if not files:
        raise HTTPException(
            status_code=400, detail="At least one resume PDF must be uploaded."
        )

    resumes: list[Resume] = []

    for uploaded_file in files:
        if not uploaded_file.filename.lower().endswith(".pdf"):
            continue

        file_bytes = await uploaded_file.read()
        try:
            text = extract_text_from_pdf(file_bytes)
            text = clean_resume_text(text)
            processed_text = preprocess_text(text)
            name = extract_name(file_bytes)
            sections = extract_sections(text)

            resume = Resume(
                name=name,
                file=uploaded_file.filename,
                content=text,
                processed_content=processed_text,
                education=sections.get("education", ""),
                experience=sections.get("experience", ""),
                projects=sections.get("projects", ""),
                skills=sections.get("skills", ""),
                certifications=sections.get("certifications", ""),
            )
            resumes.append(resume)
        except Exception as e:  # noqa: BLE001
            logger.warning("Could not parse resume %s: %s", uploaded_file.filename, e)
            continue

    if not resumes:
        raise HTTPException(
            status_code=400,
            detail="None of the uploaded files could be parsed as PDFs.",
        )

    # Extract required skills from the job description
    required_skills = extract_required_skills(final_jd)

    # Rank resumes
    ranked = rank_resumes(resumes, final_jd)

    candidate_results: list[CandidateResult] = []
    for rank_idx, cand in enumerate(ranked, start=1):
        ai_obj = None
        if "ai" in cand and cand["ai"] is not None:
            ai_data = cand["ai"]
            ai_obj = AIInsights(
                candidate_summary=ai_data.candidate_summary,
                strengths=ai_data.strengths,
                weaknesses=ai_data.weaknesses,
                resume_improvements=ai_data.resume_improvements,
                technical_questions=ai_data.technical_questions,
                behavioral_questions=ai_data.behavioral_questions,
                recommendation=ai_data.recommendation,
            )

        candidate_results.append(
            CandidateResult(
                rank=rank_idx,
                name=cand["name"],
                filename=cand["resume"],
                ats_score=cand["ats_score"],
                semantic_score=cand["score"],
                skill_coverage=cand["skill_coverage"],
                decision=cand["decision"],
                matched_skills=cand["matched_skills"],
                missing_skills=cand["missing"],
                contact=ContactInfo(
                    email=cand["email"][0] if cand["email"] else None,
                    phone=cand["phone"][0] if cand["phone"] else None,
                ),
                ai=ai_obj,
            )
        )

    return ScreenResponse(
        job_description_skills=required_skills,
        total_candidates=len(candidate_results),
        candidates=candidate_results,
    )
