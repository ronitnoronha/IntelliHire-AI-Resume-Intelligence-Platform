import re

from ai.service import analyze_candidate
from jd_parser import extract_required_skills
from recommendation import recruiter_decision
from scoring import calculate_ats_score
from semantic import semantic_similarity
from skills import compare_skills


def rank_resumes(resumes, job_description):

    results = []
    required_skills = extract_required_skills(job_description)

    for resume in resumes:
        candidate_name = resume.name

        file_name = resume.file

        original_resume = resume.content

        score = semantic_similarity(job_description, original_resume)

        matched, missing = compare_skills(original_resume, required_skills)

        if len(required_skills) > 0:
            skill_coverage = (len(matched) / len(required_skills)) * 100
        else:
            skill_coverage = 0

        ats_score = calculate_ats_score(score, skill_coverage)

        analysis = analyze_candidate(
            original_resume,
            job_description,
            score,
            skill_coverage,
            ats_score,
            matched,
            missing,
        )

        decision = recruiter_decision(ats_score)

        email = re.findall(
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", original_resume
        )

        phone = re.findall(
            r"(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3,5}\)?[-.\s]?)\d{3,5}(?:[-.\s]?\d{3,5})?|\b\d{10}\b",
            original_resume,
        )

        result = {
            "name": candidate_name,
            "resume": file_name,
            "email": email,
            "phone": phone,
            "score": round(score, 2),
            "matched_skills": matched,
            "missing": missing,
            "skill_coverage": round(skill_coverage, 2),
            "ats_score": ats_score,
            "decision": decision,
        }

        if analysis is not None:
            result["ai"] = analysis

        results.append(result)

    results.sort(key=lambda x: x["ats_score"], reverse=True)

    return results
