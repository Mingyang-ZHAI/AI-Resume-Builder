import json
from django.test import TestCase
from unittest.mock import patch, MagicMock
from resume_build.models import User, Education, Experience
from resume_build.views import rewrite_resume

"""
Function Explanation:
This test suite validates the `rewrite_resume` function. It ensures the function correctly generates 
a professionally rewritten resume using AI while handling different user data scenarios.

Parameter Explanation:
- `user_id` (int): The ID of the user whose resume is being rewritten.
- `job_title` (str): The title of the job for which the resume is being tailored.
- `job_description` (str): The description of the job for which the resume is being tailored.
"""

class RewriteResumeTests(TestCase):
    """ Test cases for the `rewrite_resume` function. """
    def setUp(self):
        """
        Set up test data for the tests. This includes creating a test user with education and experience.
        """
        self.user = User.objects.create(
            id=1,
            name="Test User",
            email="testuser@test.com",
            phone="1234567890",
            city="Test City",
            country="Testland",
            skills=["Python", "Django", "SQL"]
        )
        Education.objects.create(
            user_id=self.user,  # Use the correct field name
            school_name="Test University",
            degree="Bachelor's",
            major="Computer Science",
            start_year=2015,
            end_year=2019,
            gpa=3.8
        )
        Experience.objects.create(
            user_id=self.user,  # Use the correct field name
            position="Software Engineer",
            institution_name="Tech Corp",
            start_year=2019,
            end_year=2022,
            description="Developed software applications using Python and Django."
        )
        self.job_title = "Data Engineer"
        self.job_description = "Looking for a candidate with experience in Python, SQL, and cloud technologies."

    @patch("resume_build.views.OpenAI")  # Mock the OpenAI client
    def test_normal_case(self, mock_openai):
        """
        Test Case: Normal Case
        - Ensure the function generates a resume when the user has valid data.
        """
        print("Normal Case: Resume partially matches job requirements")
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value.to_json.return_value = json.dumps({
            "choices": [{
                "message": {
                    "content": "<h2>Rewritten Resume</h2>"
                }
            }]
        })
        mock_openai.return_value = mock_client

        result = rewrite_resume(self.user.id, self.job_title, self.job_description)
        self.assertIn("<h2>Rewritten Resume</h2>", result)
        print("Normal Case: Resume partially matches job requirements: pass\n")

    @patch("resume_build.views.OpenAI")
    def test_edge_case_empty_education_and_experience(self, mock_openai):
        """
        Test Case: Edge Case
        - Ensure the function handles users with no education or experience.
        """
        print("Edge Case: User has no education or experience")

        # Use the correct field name for filtering
        Education.objects.filter(user_id=self.user.id).delete()
        Experience.objects.filter(user_id=self.user.id).delete()

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value.to_json.return_value = json.dumps({
            "choices": [{
                "message": {
                    "content": "<h2>Rewritten Resume</h2>"
                }
            }]
        })
        mock_openai.return_value = mock_client

        result = rewrite_resume(self.user.id, self.job_title, self.job_description)
        self.assertIn("<h2>Rewritten Resume</h2>", result)
        print("Edge Case: User has no education or experience: pass\n")


    @patch("resume_build.views.OpenAI")
    def test_corner_case_no_skills(self, mock_openai):
        """
        Test Case: Corner Case
        - Ensure the function handles users with no skills listed.
        """
        print("Corner Case: User has no skills listed")
        self.user.skills = ""  # Use an empty string instead of None
        self.user.save()

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value.to_json.return_value = json.dumps({
            "choices": [{
                "message": {
                    "content": "<h2>Rewritten Resume</h2>"
                }
            }]
        })
        mock_openai.return_value = mock_client

        result = rewrite_resume(self.user.id, self.job_title, self.job_description)
        self.assertIn("<h2>Rewritten Resume</h2>", result)
        print("Corner Case: User has no skills listed: pass\n")


    @patch("resume_build.views.OpenAI")
    def test_corner_case_api_error(self, mock_openai):
        """
        Test Case: Corner Case
        - Ensure the function gracefully handles API errors.
        """
        print("Corner Case: API error during resume generation")
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API error")
        mock_openai.return_value = mock_client

        result = rewrite_resume(self.user.id, self.job_title, self.job_description)
        self.assertIn("<p>An error occurred while rewriting the resume.</p>", result)
        print("Corner Case: API error during resume generation: pass\n")


if __name__ == "__main__":
    """
    Main entry point for executing the test file.
    """
    import unittest
    unittest.main()
