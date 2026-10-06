import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")


def get_client():
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return None

    return OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
