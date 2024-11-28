from django.test import TestCase, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.models import AnonymousUser
from resume_build.models import User, Job, Education, Experience
from resume_build.views import match_score_page

"""
Function Explanation:
This test file validates the `match_score_page` function, ensuring it correctly calculates and renders 
match scores for resumes against job descriptions. The tests cover normal, edge, and corner cases.

Parameter Explanation:
- `request`: A Django HTTP request object containing user session data.
- `User`: The user model storing basic user information.
- `Job`: The job model containing job descriptions and titles.
- `Experience`: The experience model storing user work history.
- `Education`: The education model storing user academic qualifications.
"""

class MatchScorePageTests(TestCase):
    def setUp(self):
        """
        Set up test data for the tests. This includes creating a test user and request factory.
        """
        # Set up a test user
        self.user = User.objects.create(
            id=1,
            name="Test User",
            username="testuser",
            country="Testland",
            city="Test City",
            phone="1234567890",
            email="testuser@test.com",
            skills=["Python", "Django", "SQL"]
        )
        # Create a request factory for simulating requests
        self.factory = RequestFactory()

    def _setup_request(self, session_data):
        """
        Helper function to create a request with session data.

        Args:
            session_data (dict): Session data to attach to the request.

        Returns:
            HttpRequest: A simulated Django request with session data.
        """
        request = self.factory.get("/match_score/")
        middleware = SessionMiddleware(lambda req: None)  # Provide a dummy callable for get_response
        middleware.process_request(request)
        request.session.update(session_data)
        request.user = AnonymousUser()
        return request

    def test_normal_case(self):
        """
        Test Case: Normal Case
        - Ensure match scores are calculated correctly when the resume partially matches job requirements.
        """
        print("Normal Case: Resume partially matches job requirements")
        job = Job.objects.create(
            user_id=self.user,
            job_title="Data Engineer",
            description="Looking for candidates with Python and SQL skills."
        )
        request = self._setup_request({"info": {"id": self.user.id}})
        response = match_score_page(request)
        print("Response status:", response.status_code)
        # print("Response content:", response.content.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Overall Match Score")
        print("Normal Case: Resume partially matches job requirements: pass\n")

    def test_corner_case_empty_resume_content(self):
        """
        Test Case: Corner Case
        - Ensure the view handles cases where the resume contains no experiences or education.
        """
        print("Corner Case: Empty resume content")
        job = Job.objects.create(
            user_id=self.user,
            job_title="Data Engineer",
            description="Looking for candidates with Python and SQL skills."
        )
        Experience.objects.filter(user_id=self.user.id).delete()
        Education.objects.filter(user_id=self.user.id).delete()

        request = self._setup_request({"info": {"id": self.user.id}})
        response = match_score_page(request)

        print("Response status:", response.status_code)
        # print("Response content:", response.content.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Overall Match Score")
        print("Corner Case: Empty resume content: pass\n")


    def test_corner_case_resume_without_relevant_skills(self):
        """
        Test Case: Corner Case
        - Ensure the view correctly processes a resume that lacks skills relevant to the job description.
        """
        print("Corner Case: Resume without relevant skills")
        job = Job.objects.create(
            user_id=self.user,
            job_title="Data Scientist",
            description="Looking for candidates with R and Machine Learning."
        )
        request = self._setup_request({"info": {"id": self.user.id}})
        response = match_score_page(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Overall Match Score")
        print("Corner Case: Resume without relevant skills: pass\n")


if __name__ == "__main__":
    """
    Main entry point for executing the test file.
    """
    import unittest
    unittest.main()
