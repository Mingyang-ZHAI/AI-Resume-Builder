import unittest
from resume_build.utils.match_score import extract_skills_from_text


class TestExtractSkillsFromText(unittest.TestCase):
    """ Test the extract_skills_from_text function. """
    def test_extract_skills_from_text(self):
        """ Test the extract_skills_from_text function. """
        # Normal Case: Text partially matches the skills list
        text = "Experienced in Python and Django development."
        skills = ["Python", "SQL", "Django"]
        result = extract_skills_from_text(text, skills)
        self.assertEqual(result, ["Python", "Django"])
        print("Normal Case: Text partially matches the skills list: pass\n")

        # Edge Case: Empty text
        text = ""
        skills = ["Python", "SQL", "Django"]
        result = extract_skills_from_text(text, skills)
        self.assertEqual(result, [])
        print("Edge Case: Empty text: pass\n")

        # Edge Case: Empty skills list
        text = "Experienced in Python and Django development."
        skills = []
        result = extract_skills_from_text(text, skills)
        self.assertEqual(result, [])
        print("Edge Case: Empty skills list: pass\n")

        # Corner Case: Text matches all skills
        text = "Expert in Python, SQL, and Django."
        skills = ["Python", "SQL", "Django"]
        result = extract_skills_from_text(text, skills)
        self.assertEqual(result, ["Python", "SQL", "Django"])
        print("Corner Case: Text matches all skills: pass\n")

        # Corner Case: Text matches no skills
        print("Corner Case: Text matches no skills")
        text = "Experienced in Java and Spring Boot."
        skills = ["Python", "SQL", "Django"]
        result = extract_skills_from_text(text, skills)
        self.assertEqual(result, [])
        print("Corner Case: Text matches no skills: pass\n")

        # Edge Case: Case insensitivity in skills matching
        text = "PYTHON sql and django are used in this project."
        skills = ["python", "SQL", "Django"]
        result = extract_skills_from_text(text, skills)
        self.assertEqual(result, ["python", "SQL", "Django"])
        print("Edge Case: Case insensitivity in skills matching: pass\n")

        # Corner Case: Skills partially overlap with words in text
        text = "Pythonic coding is different from basic Python."
        skills = ["Python", "SQL", "Django"]
        result = extract_skills_from_text(text, skills)
        self.assertEqual(result, ["Python"])
        print("Corner Case: Skills partially overlap with words in text: pass\n")


if __name__ == "__main__":
    unittest.main()
