import re

skills_db = [
    # Core Languages
    "python",
    "sql",
    "java",
    "c++",
    "c#",
    "rust",
    "go",
    "javascript",
    "typescript",
    "r",
    "scala",
    "kotlin",
    "swift",
    "bash",
    # AI / Machine Learning & Data Science
    "machine learning",
    "deep learning",
    "natural language processing",
    "computer vision",
    "generative ai",
    "rag",
    "langchain",
    "llamaindex",
    "transformers",
    "tensorflow",
    "pytorch",
    "scikit-learn",
    "pandas",
    "numpy",
    "scipy",
    "statistics",
    "data visualization",
    "keras",
    "huggingface",
    # Data Engineering & Analytics
    "power bi",
    "tableau",
    "spark",
    "pyspark",
    "hadoop",
    "kafka",
    "airflow",
    "dbt",
    "snowflake",
    "bigquery",
    "databricks",
    "excel",
    # Cloud & DevOps
    "aws",
    "azure",
    "gcp",
    "docker",
    "kubernetes",
    "terraform",
    "ansible",
    "git",
    "github",
    "ci/cd",
    "linux",
    # Databases & Storage
    "postgresql",
    "mysql",
    "mongodb",
    "redis",
    "elasticsearch",
    "qdrant",
    "chromadb",
    "pinecone",
    # Web & Architecture
    "rest api",
    "graphql",
    "grpc",
    "microservices",
    "system design",
    "react",
    "next.js",
    "vue",
    "angular",
    "node.js",
    "flask",
    "fastapi",
    "django",
    "tailwind",
]


SKILL_PATTERNS = {
    "python": r"\bpython\b",
    "sql": r"\bsql\b",
    "java": r"\bjava\b",
    "c++": r"\b(?:c\+\+|cpp|c\s*\+\+)\b",
    "c#": r"\b(?:c#|c-sharp|c\s*#)\b",
    "rust": r"\brust\b",
    "go": r"\b(?:golang|\bgo\b)",
    "javascript": r"\b(?:javascript|js)\b",
    "typescript": r"\b(?:typescript|ts)\b",
    "r": r"\b(?:r\s+programming|r\s+language|\br\b)",
    "scala": r"\bscala\b",
    "kotlin": r"\bkotlin\b",
    "swift": r"\bswift\b",
    "bash": r"\b(?:bash|shell)\b",
    "machine learning": r"\bmachine\s+learning\b",
    "deep learning": r"\bdeep\s+learning\b",
    "natural language processing": r"\b(?:natural\s+language\s+processing|nlp)\b",
    "computer vision": r"\b(?:computer\s+vision|cv)\b",
    "generative ai": r"\b(?:generative\s+ai|genai|gen\s+ai)\b",
    "rag": r"\b(?:retrieval\s+augmented\s+generation|rag)\b",
    "langchain": r"\blangchain\b",
    "llamaindex": r"\b(?:llama\s*index|llamaindex)\b",
    "transformers": r"\btransformers\b",
    "tensorflow": r"\btensorflow\b",
    "pytorch": r"\bpytorch\b",
    "scikit-learn": r"\b(?:scikit[-_\s]*learn|sklearn)\b",
    "pandas": r"\bpandas\b",
    "numpy": r"\bnumpy\b",
    "scipy": r"\bscipy\b",
    "statistics": r"\bstatistics\b",
    "data visualization": r"\bdata\s+visualization\b",
    "keras": r"\bkeras\b",
    "huggingface": r"\b(?:hugging\s*face|huggingface)\b",
    "power bi": r"\bpower\s*bi\b",
    "tableau": r"\btableau\b",
    "spark": r"\b(?:apache\s+spark|\bspark\b)",
    "pyspark": r"\bpyspark\b",
    "hadoop": r"\bhadoop\b",
    "kafka": r"\bkafka\b",
    "airflow": r"\bairflow\b",
    "dbt": r"\bdbt\b",
    "snowflake": r"\bsnowflake\b",
    "bigquery": r"\bbigquery\b",
    "databricks": r"\bdatabricks\b",
    "excel": r"\b(?:ms\s+excel|excel)\b",
    "aws": r"\b(?:aws|amazon\s+web\s+services)\b",
    "azure": r"\bazure\b",
    "gcp": r"\b(?:gcp|google\s+cloud)\b",
    "docker": r"\bdocker\b",
    "kubernetes": r"\b(?:kubernetes|k8s)\b",
    "terraform": r"\bterraform\b",
    "ansible": r"\bansible\b",
    "git": r"\bgit\b",
    "github": r"\bgithub\b",
    "ci/cd": r"\bci\s*[\/\\]?\s*cd\b",
    "linux": r"\blinux\b",
    "postgresql": r"\b(?:postgresql|postgres)\b",
    "mysql": r"\bmysql\b",
    "mongodb": r"\bmongodb\b",
    "redis": r"\bredis\b",
    "elasticsearch": r"\b(?:elasticsearch|elastic\s+search)\b",
    "qdrant": r"\bqdrant\b",
    "chromadb": r"\b(?:chromadb|chroma)\b",
    "pinecone": r"\bpinecone\b",
    "rest api": r"\b(?:rest\s*api|restful)\b",
    "graphql": r"\bgraphql\b",
    "grpc": r"\bgrpc\b",
    "microservices": r"\bmicroservices\b",
    "system design": r"\bsystem\s+design\b",
    "react": r"\b(?:react|reactjs|react\.js)\b",
    "next.js": r"\b(?:next\.?js|nextjs)\b",
    "vue": r"\b(?:vue|vuejs|vue\.js)\b",
    "angular": r"\bangular\b",
    "node.js": r"\b(?:node\.?js|nodejs)\b",
    "flask": r"\bflask\b",
    "fastapi": r"\bfastapi\b",
    "django": r"\bdjango\b",
    "tailwind": r"\b(?:tailwind|tailwindcss)\b",
}


def normalize(text):
    """
    Convert text into a normalized format for matching.
    Example:
        'Power BI' -> 'powerbi'
        'Power-BI' -> 'powerbi'
        'Machine Learning' -> 'machinelearning'
    """

    text = text.lower()

    text = re.sub(r"[^a-z0-9]", "", text)

    return text


def has_skill(skill, text):
    """
    Check if a skill appears in the target text using exact word boundaries
    or tailored regex patterns.
    """
    if not skill or not text:
        return False

    skill_lower = skill.lower()
    pattern = SKILL_PATTERNS.get(skill_lower, r"\b" + re.escape(skill_lower) + r"\b")
    return bool(re.search(pattern, text, re.IGNORECASE))


def compare_skills(resume_text, required_skills):

    matched = []
    missing = []

    for skill in required_skills:
        if has_skill(skill, resume_text):
            matched.append(skill)
        else:
            missing.append(skill)

    return matched, missing
