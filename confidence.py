def combine_scores(llm_score: float, stylometric_score: float) -> float:
    combined = (0.60 * llm_score) + (0.40 * stylometric_score)
    return round(combined, 3)


def classify_from_score(score: float) -> str:
    if score >= 0.70:
        return "likely_ai"

    if score <= 0.35:
        return "likely_human"

    return "uncertain"