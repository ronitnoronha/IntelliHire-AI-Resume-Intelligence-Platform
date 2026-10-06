import sys
import unittest
from pathlib import Path

# Add mutants directory (for mutated modules under test)
mutants_dir = Path(__file__).resolve().parent.parent
if str(mutants_dir) not in sys.path:
    sys.path.insert(0, str(mutants_dir))

# Add main project root (for unmutated dependencies)
project_dir = Path("/Users/ronitnoronha/Downloads/Resume_Screener")
if str(project_dir) not in sys.path:
    sys.path.append(str(project_dir))


from jd_parser import extract_required_skills
from recommendation import recruiter_decision
from scoring import calculate_ats_score
from skills import compare_skills, normalize



class TestPureUnits(unittest.TestCase):
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
        score = calculate_ats_score(80, 100)
        self.assertEqual(score, 86.0)
        # Test exact rounding to 2 decimal places with multi-decimal inputs
        self.assertEqual(calculate_ats_score(77.3333, 88.5555), 80.7)
        self.assertEqual(calculate_ats_score(71.234, 50.123), 64.9)
        # Test boundary and weights
        self.assertEqual(calculate_ats_score(0, 0), 0.0)
        self.assertEqual(calculate_ats_score(100, 100), 100.0)

    def test_recruiter_decision(self):
        # Exact boundary threshold and return string assertions
        self.assertEqual(recruiter_decision(80), "⭐⭐⭐⭐⭐ Strongly Recommend Interview")
        self.assertEqual(recruiter_decision(85), "⭐⭐⭐⭐⭐ Strongly Recommend Interview")
        self.assertEqual(recruiter_decision(65), "⭐⭐⭐⭐ Recommend Interview")
        self.assertEqual(recruiter_decision(79.9), "⭐⭐⭐⭐ Recommend Interview")
        self.assertEqual(recruiter_decision(50), "⭐⭐⭐ Consider Interview")
        self.assertEqual(recruiter_decision(64.9), "⭐⭐⭐ Consider Interview")
        self.assertEqual(recruiter_decision(35), "⭐⭐ Needs Improvement")
        self.assertEqual(recruiter_decision(49.9), "⭐⭐ Needs Improvement")
        self.assertEqual(recruiter_decision(34.9), "❌ Not Recommended")
        self.assertEqual(recruiter_decision(0), "❌ Not Recommended")



if __name__ == "__main__":
    unittest.main()
