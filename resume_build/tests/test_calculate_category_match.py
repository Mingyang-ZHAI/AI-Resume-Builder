import unittest
from sklearn.feature_extraction.text import CountVectorizer
from resume_build.utils.match_score import calculate_category_match


class TestCalculateCategoryMatch(unittest.TestCase):
    """ Test the calculate_category_match function. """
    def test_calculate_category_match(self):
        """ Test the calculate_category_match function. """
        # Normal Case: Resume partially matches job requirements
        category_keywords = ["Python", "SQL", "Django"]
        content = "Experienced in Python and Django development."
        score = calculate_category_match(category_keywords, content)
        self.assertAlmostEqual(score, 81.65, places=2)
        print("Normal Case: Resume partially matches job requirements: pass\n")

        # Edge Case: Empty content
        category_keywords = ["Python", "SQL", "Django"]
        content = ""
        score = calculate_category_match(category_keywords, content)
        self.assertEqual(score, 0.0)
        print("Edge Case: Empty content: pass\n")

        # Edge Case: Empty keywords list
        category_keywords = []
        content = "Experienced in Python and Django development."
        score = calculate_category_match(category_keywords, content)
        self.assertEqual(score, 0.0)
        print("Edge Case: Empty keywords list: pass\n")

        # Corner Case: Content matches all keywords perfectly
        category_keywords = ["Python", "SQL", "Django"]
        content = "Python SQL Django"
        score = calculate_category_match(category_keywords, content)
        self.assertEqual(score, 100.0)
        print("Corner Case: Content matches all keywords perfectly: pass\n")

        # Corner Case: Content has no overlap with keywords
        category_keywords = ["Python", "SQL", "Django"]
        content = "Experienced in Java and Spring Boot development."
        score = calculate_category_match(category_keywords, content)
        self.assertEqual(score, 0.0)
        print("Corner Case: Content has no overlap with keywords: pass\n")

        # Edge Case: Content and keywords are case-insensitive matches
        category_keywords = ["python", "sql", "django"]
        content = "PYTHON SQL django"
        score = calculate_category_match(category_keywords, content)
        self.assertEqual(score, 100.0)
        print("Edge Case: Content and keywords are case-insensitive matches: pass\n")

        # Corner Case: Content has repeated keywords
        category_keywords = ["Python", "SQL", "Django"]
        content = "Python Python Django SQL SQL"
        score = calculate_category_match(category_keywords, content)
        self.assertEqual(score, 100.0)
        print("Corner Case: Content has repeated keywords: pass\n")

        # Edge Case: Content includes extra, unrelated words
        category_keywords = ["Python", "SQL", "Django"]
        content = "Python and Django are great. SQL is essential for databases."
        score = calculate_category_match(category_keywords, content)
        self.assertAlmostEqual(score, 100.0, places=2)
        print("Edge Case: Content includes extra, unrelated words: pass\n")


if __name__ == "__main__":
    unittest.main()
