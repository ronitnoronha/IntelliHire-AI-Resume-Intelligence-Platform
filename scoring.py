def calculate_ats_score(semantic_score, skill_coverage):
    """
    Weighted ATS Score
    """

    ats = semantic_score * 0.70 + skill_coverage * 0.30

    return round(ats, 2)
