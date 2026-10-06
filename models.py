from dataclasses import dataclass


@dataclass
class Resume:
    name: str

    file: str

    content: str

    processed_content: str

    education: str

    experience: str

    projects: str

    skills: str

    certifications: str
