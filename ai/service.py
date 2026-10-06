import logging

from ai.llm import MODEL, get_client
from ai.parser import parse_response
from ai.prompts import build_analysis_prompt

logger = logging.getLogger(__name__)


def analyze_candidate(
    resume, job_description, semantic_score, skill_coverage, ats_score, matched, missing
):

    prompt = build_analysis_prompt(
        resume,
        job_description,
        semantic_score,
        skill_coverage,
        ats_score,
        matched,
        missing,
    )

    client = get_client()

    if client is None:
        return None

    try:
        response = client.chat.completions.create(
            model=MODEL, messages=[{"role": "user", "content": prompt}], temperature=0.2
        )

        return parse_response(response.choices[0].message.content)
    except Exception as e:  # noqa: BLE001
        logger.warning("AI candidate analysis failed with model %s: %s", MODEL, e)
        # AI insights are supplementary; ranking must still work if the
        # credential, network, or provider response is unavailable.
        return None
