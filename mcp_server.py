"""
Model Context Protocol (MCP) Server for Resume Screener & ATS.
Compatible with MCP 2.x specification (Claude Desktop, Cursor, Antigravity).
"""

import glob
import json
import logging
import os
from pathlib import Path

from mcp.server.mcpserver import MCPServer

logger = logging.getLogger(__name__)

from extractor import extract_name
from jd_parser import extract_required_skills
from models import Resume
from nlp import preprocess_text
from parser import clean_resume_text, extract_text_from_pdf
from ranking import rank_resumes
from resume_parser import extract_sections

# Initialize the MCP Server
mcp = MCPServer(
    name="resume-screener",
    title="Resume Screener & ATS Agent Server",
    version="2.0.0",
    description="Enterprise ATS screener tool providing automated resume ranking, skill gap detection, and AI interview preparation.",
)


def _process_pdf_path(pdf_path: str) -> Resume:
    """Helper to load and process a single PDF into a Resume model."""
    with open(pdf_path, "rb") as f:
        file_bytes = f.read()

    text = extract_text_from_pdf(file_bytes)
    text = clean_resume_text(text)
    processed = preprocess_text(text)
    name = extract_name(file_bytes)
    sections = extract_sections(text)

    return Resume(
        name=name,
        file=Path(pdf_path).name,
        content=text,
        processed_content=processed,
        education=sections.get("education", ""),
        experience=sections.get("experience", ""),
        projects=sections.get("projects", ""),
        skills=sections.get("skills", ""),
        certifications=sections.get("certifications", ""),
    )


@mcp.tool(
    description="Screens and ranks all PDF resumes in a directory against a target job description."
)
def screen_resumes_directory(directory_path: str, job_description: str) -> str:
    """
    Scans a local folder containing PDF resumes, analyzes them against the job description,
    and returns a ranked leaderboard with ATS scores, skill coverage, and recruiter recommendations.
    """
    if not os.path.isdir(directory_path):
        return f"Error: Directory '{directory_path}' does not exist."

    pdf_files = glob.glob(os.path.join(directory_path, "*.pdf"))
    if not pdf_files:
        return f"No PDF files found in directory '{directory_path}'."

    resumes = []
    for pdf_path in pdf_files:
        try:
            resumes.append(_process_pdf_path(pdf_path))
        except Exception as e:  # noqa: BLE001
            logger.warning("Failed to process %s: %s", pdf_path, e)
            continue

    if not resumes:
        return "Failed to parse any resumes in the directory."

    results = rank_resumes(resumes, job_description)

    # Format into structured JSON output
    clean_results = []
    for r in results:
        entry = {
            "rank": len(clean_results) + 1,
            "name": r["name"],
            "file": r["resume"],
            "ats_score": r["ats_score"],
            "semantic_score": r["score"],
            "skill_coverage": f"{r['skill_coverage']}%",
            "decision": r["decision"],
            "matched_skills": r["matched_skills"],
            "missing_skills": r["missing"],
            "email": r["email"][0] if r["email"] else None,
            "phone": r["phone"][0] if r["phone"] else None,
        }
        if "ai" in r and r["ai"] is not None:
            ai_data = r["ai"]
            entry["ai_summary"] = ai_data.candidate_summary
            entry["strengths"] = ai_data.strengths
            entry["weaknesses"] = ai_data.weaknesses
            entry["technical_questions"] = ai_data.technical_questions
        clean_results.append(entry)

    return json.dumps(clean_results, indent=2)


@mcp.tool(
    description="Performs an in-depth ATS evaluation on a single resume PDF file."
)
def screen_single_resume(pdf_path: str, job_description: str) -> str:
    """
    Evaluates a single candidate PDF against a job description, returning full section extractions,
    ATS score calculation, matched/missing skill gap analysis, and interview guide.
    """
    if not os.path.exists(pdf_path):
        return f"Error: File '{pdf_path}' not found."

    resume_obj = _process_pdf_path(pdf_path)
    results = rank_resumes([resume_obj], job_description)
    if not results:
        return "Failed to score candidate."

    candidate = results[0]
    payload = {
        "candidate_name": candidate["name"],
        "filename": candidate["resume"],
        "ats_score": candidate["ats_score"],
        "semantic_similarity": candidate["score"],
        "skill_coverage": candidate["skill_coverage"],
        "recommendation": candidate["decision"],
        "matched_skills": candidate["matched_skills"],
        "missing_skills": candidate["missing"],
        "contact": {
            "email": candidate["email"][0] if candidate["email"] else "Not found",
            "phone": candidate["phone"][0] if candidate["phone"] else "Not found",
        },
        "sections": {
            "skills": resume_obj.skills.strip(),
            "experience": resume_obj.experience.strip()[:600],
            "education": resume_obj.education.strip(),
        },
    }
    if "ai" in candidate and candidate["ai"] is not None:
        ai_data = candidate["ai"]
        payload["ai_insights"] = {
            "summary": ai_data.candidate_summary,
            "strengths": ai_data.strengths,
            "weaknesses": ai_data.weaknesses,
            "resume_improvements": ai_data.resume_improvements,
            "technical_interview_questions": ai_data.technical_questions,
            "behavioral_interview_questions": ai_data.behavioral_questions,
        }

    return json.dumps(payload, indent=2)


@mcp.tool(
    description="Extracts all technical skills detected in a job description text."
)
def extract_skills_from_jd(job_description: str) -> list[str]:
    """Parses a job description and returns an array of recognized technical skills."""
    return extract_required_skills(job_description)


@mcp.resource(
    "sample://resume",
    description="Sample resume included with the repository for testing.",
)
def get_sample_resume() -> str:
    """Returns the parsed text of the included sample resume."""
    sample_path = os.path.join(
        os.path.dirname(__file__), "sample_resumes", "sample_resume.pdf"
    )
    if os.path.exists(sample_path):
        with open(sample_path, "rb") as f:
            return clean_resume_text(extract_text_from_pdf(f.read()))
    return "Sample resume file not found."


@mcp.prompt(
    description="Template for conducting a fair, blind evaluation of a candidate without demographic bias."
)
def blind_evaluation_prompt(candidate_experience: str, job_description: str) -> str:
    return f"""You are an objective, unbiased ATS recruiter evaluator.
Evaluate the candidate's core technical experience and deliverables against the job description below.
Do not make assumptions based on name, gender, location, or school prestige.

JOB DESCRIPTION:
{job_description}

CANDIDATE EXPERIENCE:
{candidate_experience}

Please evaluate:
1. Relevance of past projects to key deliverables.
2. Depth of technical competency in required stack.
3. Quantifiable impact and outcomes achieved.
4. Specific gap areas to investigate during the interview.
"""


if __name__ == "__main__":
    mcp.run()
