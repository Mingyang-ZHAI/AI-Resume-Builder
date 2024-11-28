import unittest
from resume_build.utils.match_score import (
    calculate_category_match,
    extract_skills_from_text,
    calculate_skill_scores
)


class TestCalculateSkillScores(unittest.TestCase):
    """
    Test the calculate_skill_scores function.
    """
    def test_calculate_skill_scores(self):
        """
        Test the calculate_skill_scores function.
        """
        # Mock objects and data
        job = type("Job", (object,), {"description": "Expert in Python and SQL"})()  # Mock object
        
        # Predefined skill categories
        global HARD_SKILLS, SOFT_SKILLS, OTHER_KEYWORDS
        HARD_SKILLS = ["Python", "SQL", "Django"]
        SOFT_SKILLS = ["Communication", "Teamwork"]
        OTHER_KEYWORDS = ["Data Analysis", "Machine Learning"]

        # Inject mock functions
        global extract_skills_from_text, calculate_category_match

        # Mock implementations of helper functions
        def extract_skills_from_text(text, skills):
            return [skill for skill in skills if skill.lower() in text.lower()]

        def calculate_category_match(job_skills, content):
            if not content:
                return 0.0
            matches = [skill for skill in job_skills if skill.lower() in content.lower()]
            return len(matches) / len(job_skills) * 100 if job_skills else 0.0

        # Normal Case: Resume partially matches job requirements
        raw_content = "Experienced in Python and Django development."
        processed_content = "Experienced in Python and Django."
        scores = calculate_skill_scores(job, raw_content, processed_content)
        self.assertAlmostEqual(scores["Hard Skills"]["processed_score"], 70.71, places=2)
        self.assertAlmostEqual(scores["Hard Skills"]["raw_score"], 70.71, places=2)
        self.assertEqual(scores["Hard Skills"]["processed_report"], "You are missing 1 hard skills: SQL.")
        print("Normal Case: Resume partially matches job requirements: pass")

        # Edge Case: Empty resume content
        raw_content = ""
        processed_content = ""
        scores = calculate_skill_scores(job, raw_content, processed_content)
        # print(scores)
        # print(scores["Hard Skills"])
        self.assertEqual(scores["Hard Skills"]["processed_score"], 0.0)
        self.assertAlmostEqual(scores["Hard Skills"]["raw_score"], 0.0)
        self.assertEqual(scores["Soft Skills"]["raw_report"], "No soft skills extracted from the job description.")
        print("Edge Case: Empty resume content: pass")

        # Edge Case: No skills in job description
        job_empty = type("Job", (object,), {"description": ""})()
        scores = calculate_skill_scores(job_empty, raw_content, processed_content)
        self.assertEqual(scores["Hard Skills"]["raw_score"], 0.0)
        self.assertEqual(scores["Hard Skills"]["raw_report"], "No hard skills extracted from the job description.")
        print("Edge Case: No skills in job description: pass")

        # Corner Case: Resume matches all job requirements
        raw_content = "Expert in Python, SQL, and Django."
        processed_content = "Expert in Python, SQL, and Django."
        scores = calculate_skill_scores(job, raw_content, processed_content)
        self.assertEqual(scores["Hard Skills"]["processed_score"], 100.0)
        self.assertEqual(scores["Hard Skills"]["raw_score"], 100.0)
        self.assertEqual(scores["Hard Skills"]["processed_report"], "Great work! You have most of the hard skills required for this job.")
        print("Corner Case: Resume matches all job requirements: pass")

        # Corner Case: Job description has no overlap with resume
        raw_content = "Experienced in Java and Spring Boot."
        processed_content = "Experienced in Java and Spring Boot."
        scores = calculate_skill_scores(job, raw_content, processed_content)
        self.assertEqual(scores["Hard Skills"]["processed_score"], 0.0)
        self.assertEqual(scores["Hard Skills"]["raw_report"], "You are missing 2 hard skills: Python, SQL.")
        print("Corner Case: Job description has no overlap with resume: pass")

if __name__ == "__main__":
    unittest.main()
