import re
import sys
import unittest
from pathlib import Path

# Ensure current directory takes import priority (crucial for mutation testing)
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

# Ensure root directory is accessible for unmutated modules when running inside mutants/
if CURRENT_DIR.name == "mutants":
    PARENT_DIR = CURRENT_DIR.parent
    if str(PARENT_DIR) not in sys.path:
        sys.path.append(str(PARENT_DIR))



import fitz


from extractor import extract_name
from jd_parser import extract_required_skills
from nlp import preprocess_text
from parser import clean_resume_text, extract_text_from_pdf
from recommendation import recruiter_decision
from resume_parser import extract_sections
from scoring import calculate_ats_score
from skills import compare_skills, normalize


class TestResumeScreener(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(normalize("Power BI"), "powerbi")
        self.assertEqual(normalize("Machine-Learning"), "machinelearning")

    def test_extract_required_skills(self):
        jd = "We need a Data Scientist skilled in Python, SQL, and Machine Learning."
        skills = extract_required_skills(jd)
        self.assertIn("python", skills)
        self.assertIn("sql", skills)
        self.assertIn("machine learning", skills)

    def test_compare_skills(self):
        resume_text = "Experienced in Python and SQL with basic AWS."
        required = ["python", "sql", "tensorflow"]
        matched, missing = compare_skills(resume_text, required)
        self.assertEqual(matched, ["python", "sql"])
        self.assertEqual(missing, ["tensorflow"])

    def test_calculate_ats_score(self):
        # 70% of 80 + 30% of 100 = 56 + 30 = 86
        score = calculate_ats_score(80, 100)
        self.assertEqual(score, 86.0)

    def test_recruiter_decision(self):
        self.assertIn("Strongly Recommend", recruiter_decision(85))
        self.assertIn("Recommend Interview", recruiter_decision(70))
        self.assertIn("Consider Interview", recruiter_decision(55))
        self.assertIn("Needs Improvement", recruiter_decision(40))
        self.assertIn("Not Recommended", recruiter_decision(20))

    def test_preprocess_text(self):
        processed = preprocess_text("Developing machine learning models with Python!")
        self.assertIn("develop", processed)
        self.assertIn("machine", processed)

    def test_extract_sections(self):
        text = "Education\nB.Tech Computer Science\nSkills\nPython, SQL"
        sections = extract_sections(text)
        self.assertIn("B.Tech", sections["education"])
        self.assertIn("Python", sections["skills"])

    def test_clean_resume_text_preserves_normal_word_spacing(self):
        cleaned = clean_resume_text("Data Scientist with Python")
        self.assertEqual(cleaned, "Data Scientist with Python")

    def test_clean_resume_text_repairs_letter_spaced_words(self):
        cleaned = clean_resume_text("J o h n D o e")
        self.assertEqual(cleaned, "John Doe")

    def test_in_memory_pdf_processing(self):
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "John Doe", fontsize=24)
        page.insert_text(
            (50, 100), "Python developer with Docker and AWS experience.", fontsize=12
        )
        pdf_bytes = doc.tobytes()
        doc.close()

        name = extract_name(pdf_bytes)
        text = extract_text_from_pdf(pdf_bytes)

        self.assertEqual(name, "John Doe")
        self.assertIn("Python developer", text)

    def test_phone_number_extraction(self):
        phone_regex = r"(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3,5}\)?[-.\s]?)\d{3,5}(?:[-.\s]?\d{3,5})?|\b\d{10}\b"
        sample_text = "Contact me at +1 (555) 123-4567, +91 83698-10061, or 9876543210."
        phones = re.findall(phone_regex, sample_text)
        self.assertIn("+1 (555) 123-4567", phones)
        self.assertIn("+91 83698-10061", phones)
        self.assertIn("9876543210", phones)

    def test_expanded_skills(self):
        jd = "Looking for a full-stack engineer with React, Node.js, Docker, and PostgreSQL."
        skills = extract_required_skills(jd)
        self.assertIn("react", skills)
        self.assertIn("node.js", skills)
        self.assertIn("docker", skills)
        self.assertIn("postgresql", skills)

    def test_chunk_text_utility(self):
        from semantic import chunk_text

        long_text = "Word " * 200
        chunks = chunk_text(long_text, max_words=50, overlap=10)
        self.assertTrue(len(chunks) > 1)
        self.assertTrue(all(len(c.split()) <= 60 for c in chunks))

    def test_modern_ai_and_cloud_skills(self):
        jd = "Seeking engineer skilled in LangChain, RAG, Qdrant, FastAPI, and Next.js."
        skills = extract_required_skills(jd)
        self.assertIn("langchain", skills)
        self.assertIn("rag", skills)
        self.assertIn("qdrant", skills)
        self.assertIn("fastapi", skills)
        self.assertIn("next.js", skills)

    def test_fastapi_health_endpoint(self):
        from starlette.testclient import TestClient

        from backend.main import app

        client = TestClient(app)
        res = client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "healthy")
        self.assertTrue(data["total_skills_tracked"] >= 70)

    def test_mcp_server_tools_registered(self):
        from mcp_server import mcp

        tool_names = [t.name for t in mcp._tool_manager.list_tools()]
        self.assertIn("screen_resumes_directory", tool_names)
        self.assertIn("screen_single_resume", tool_names)
        self.assertIn("extract_skills_from_jd", tool_names)


if __name__ == "__main__":
    unittest.main()
