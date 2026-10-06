import re

SECTION_HEADERS = {
    "education": ["education", "academic background"],
    "experience": [
        "experience",
        "work experience",
        "employment",
        "positions of responsibility",
        "position of responsibility",
    ],
    "projects": ["projects", "project"],
    "skills": ["skills", "technical skills", "technicalskills"],
    "certifications": ["certifications", "certification"],
}


def normalize(text):

    text = text.lower()

    text = re.sub(r"[^a-z0-9]", "", text)

    return text


def extract_sections(text):

    sections = {
        "education": "",
        "experience": "",
        "projects": "",
        "skills": "",
        "certifications": "",
    }

    current = None

    lines = text.split("\n")

    for line in lines:
        cleaned = normalize(line)

        found = False

        for section, headers in SECTION_HEADERS.items():
            for header in headers:
                if normalize(header) == cleaned:
                    current = section
                    found = True
                    break

            if found:
                break

        if current and not found:
            sections[current] += line + "\n"

    return sections
