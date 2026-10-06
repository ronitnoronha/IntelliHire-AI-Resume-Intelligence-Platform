from skills import has_skill, skills_db


def extract_required_skills(job_description):
    """
    Extract only the skills that appear in the job description using word-boundary matching.
    """

    required_skills = []

    for skill in skills_db:
        if has_skill(skill, job_description):
            required_skills.append(skill)

    return required_skills
