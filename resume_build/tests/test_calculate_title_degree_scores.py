import unittest
from resume_build.utils.match_score import calculate_title_degree_scores


class TestTitleDegreeFunctions(unittest.TestCase):
    """ Test the calculate_title_degree_scores function. """
    def test_calculate_title_degree_scores(self):
        """ Test the calculate_title_degree_scores function. """

        # Normal Case: Resume and job description match degrees and title
        content = "I have a Master's degree and work as a Data Engineer."
        job = type("Job", (object,), {"job_title": "Data Engineer", "description": "Looking for a Master degree holder."})()
        degree_score, title_score = calculate_title_degree_scores(content, job)
        self.assertEqual(degree_score, 100)
        self.assertEqual(title_score, 100)
        print("Normal Case: Resume and job description match degrees and title: pass\n")

        # Edge Case: Job description mentions a degree not in resume
        content = "I have a Bachelor's degree."
        job = type("Job", (object,), {"job_title": "Data Engineer", "description": "Looking for a Master's degree."})()
        degree_score, title_score = calculate_title_degree_scores(content, job)
        self.assertEqual(degree_score, 0)
        self.assertEqual(title_score, 0)
        print("Edge Case: Job description mentions a degree not in resume: pass\n")

        # Corner Case: Resume matches title but job description has no degree requirement
        content = "I work as a Data Engineer."
        job = type("Job", (object,), {"job_title": "Data Engineer", "description": "Experience required."})()
        degree_score, title_score = calculate_title_degree_scores(content, job)
        self.assertEqual(degree_score, 0)
        self.assertEqual(title_score, 100)
        print("Corner Case: Resume matches title but job description has no degree requirement: pass\n")

        # Edge Case: Title does not match
        content = "I have a Master's degree."
        job = type("Job", (object,), {"job_title": "Software Engineer", "description": "Looking for a Master's degree."})()
        degree_score, title_score = calculate_title_degree_scores(content, job)
        self.assertEqual(degree_score, 100)
        self.assertEqual(title_score, 0)
        print("Edge Case: Title does not match: pass\n")

        # Corner Case: No title or degree in resume or job description
        content = "I have extensive experience."
        job = type("Job", (object,), {"job_title": "", "description": ""})()

        with self.assertRaises(ValueError) as context:
            degree_score, title_score = calculate_title_degree_scores(content, job)

        self.assertEqual(str(context.exception), "Job title cannot be empty.")
        print("Corner Case: No title or degree in resume or job description: pass\n")



if __name__ == "__main__":
    unittest.main()
