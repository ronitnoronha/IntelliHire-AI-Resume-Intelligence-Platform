import json

from ai.schemas import AIAnalysis


def parse_response(content):

    content = content.strip()
    content = content.replace("```json", "").replace("```", "").strip()

    start = content.find("{")
    end = content.rfind("}")
    if start != -1 and end != -1:
        content = content[start : end + 1]

    data = json.loads(content)
    return AIAnalysis(**data)
