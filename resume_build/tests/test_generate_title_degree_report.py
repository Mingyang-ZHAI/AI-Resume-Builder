import unittest
from resume_build.utils.match_score import generate_title_degree_report


class TestTitleDegreeFunctions(unittest.TestCase):
    """ Test the generate_title_degree_report function. """

    def test_generate_title_degree_report(self):
        """ Test the generate_title_degree_report function. """
        print("Testing generate_title_degree_report...")

        # Normal Case: Degree matches perfectly
        print("Normal Case: Degree matches perfectly")
        content = "I have a Master's degree."
        job = type("Job", (object,), {"job_title": "Data Engineer", "description": "Looking for a Master's degree."})()
        report = generate_title_degree_report(100, "Degree", job, content)
        self.assertEqual(report, "Great work! The degree matches your resume perfectly.")
        print("Normal Case: Degree matches perfectly: pass\n")

        # Edge Case: Degree missing from resume
        print("Edge Case: Degree missing from resume")
        content = "I have a Bachelor's degree."
        job = type("Job", (object,), {"job_title": "Data Engineer", "description": "Looking for a Master's degree or PhD."})()
        report = generate_title_degree_report(0, "Degree", job, content)
        self.assertEqual(report, "You are missing these degrees mentioned in the job description: master, phd.")
        print("Edge Case: Degree missing from resume: pass\n")

        # Corner Case: No degree requirement in job description
        print("Corner Case: No degree requirement in job description")
        content = "I have a Master's degree."
        job = type("Job", (object,), {"job_title": "Data Engineer", "description": "Experience required."})()
        report = generate_title_degree_report(0, "Degree", job, content)
        self.assertEqual(report, "No relevant degree requirements found in the job description.")
        print("Corner Case: No degree requirement in job description: pass\n")

        # Normal Case: Title matches perfectly
        print("Normal Case: Title matches perfectly")
        content = "I work as a Data Engineer."
        job = type("Job", (object,), {"job_title": "Data Engineer", "description": ""})()
        report = generate_title_degree_report(100, "Title", job, content)
        self.assertEqual(report, "Great work! The title matches your resume perfectly.")
        print("Normal Case: Title matches perfectly: pass\n")

        # Edge Case: Title missing from resume
        print("Edge Case: Title missing from resume")
        content = "I work as a Software Engineer."
        job = type("Job", (object,), {"job_title": "Data Engineer", "description": ""})()
        report = generate_title_degree_report(0, "Title", job, content)
        self.assertEqual(report, "Your resume does not include the job title 'Data Engineer'. Consider aligning your title.")
        print("Edge Case: Title missing from resume: pass\n")


if __name__ == "__main__":
    unittest.main()
