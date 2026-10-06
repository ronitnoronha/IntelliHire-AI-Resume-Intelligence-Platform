def build_analysis_prompt(
    resume, job_description, semantic_score, skill_coverage, ats_score, matched, missing
):

    return f"""
You are a senior technical recruiter.

Analyze the candidate.

Return ONLY valid JSON.

Do NOT return markdown.

Do NOT return explanations.

Do NOT wrap the JSON in ```.

Every field is REQUIRED.

Use EXACTLY this schema.

{{
  "candidate_summary": "A short paragraph summarizing the candidate.",

  "strengths": [
    "Strength 1",
    "Strength 2"
  ],

  "weaknesses": [
    "Weakness 1",
    "Weakness 2"
  ],

  "resume_improvements": [
    "Suggestion 1",
    "Suggestion 2"
  ],

  "technical_questions": [
    "Question 1",
    "Question 2"
  ],

  "behavioral_questions": [
    "Question 1",
    "Question 2"
  ],

  "recommendation": "Recommend Interview"
}}

Candidate Resume

{resume}

Job Description

{job_description}

Semantic Match:
{semantic_score:.2f}

Skill Coverage:
{skill_coverage:.2f}

ATS Score:
{ats_score:.2f}

Matched Skills:
{", ".join(matched)}

Missing Skills:
{", ".join(missing)}
"""
