def recruiter_decision(score):

    if score >= 80:
        return "⭐⭐⭐⭐⭐ Strongly Recommend Interview"

    elif score >= 65:
        return "⭐⭐⭐⭐ Recommend Interview"

    elif score >= 50:
        return "⭐⭐⭐ Consider Interview"

    elif score >= 35:
        return "⭐⭐ Needs Improvement"

    else:
        return "❌ Not Recommended"
