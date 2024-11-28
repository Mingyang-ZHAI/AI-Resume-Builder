from django.test import TestCase, RequestFactory
from resume_build.models import User, Experience
from resume_build.views import fetch_resume_content

"""
Function Explanation:
This test suite validates the `fetch_resume_content` function. The function fetches raw and processed
resume content for a given user, combining all their experiences. It also checks for rewritten content 
stored in the session.

Parameter Explanation:
- `request`: A Django HTTP request object, including session data.
- `user`: A `User` instance for which the resume content is being fetched.
"""

class FetchResumeContentTests(TestCase):
    def setUp(self):
        """
        Set up test data for the tests. This includes creating a test user and sample experiences.
        """
        self.user = User.objects.create(
            id=1,
            name="Test User",
            username="testuser",
            country="Testland",
            city="Test City",
            phone="1234567890",
            email="testuser@test.com"
        )
        self.factory = RequestFactory()

    def _setup_request(self, session_data=None):
        """
        Helper function to create a request with session data.

        Args:
            session_data (dict): Session data to attach to the request.

        Returns:
            HttpRequest: A simulated Django request with session data.
        """
        request = self.factory.get("/fetch_resume/")
        request.session = session_data or {}
        return request

    def test_normal_case(self):
        """
        Test Case: Normal Case
        - Ensure the function correctly fetches combined raw content when experiences exist.
        """
        print("Normal Case: Resume contains multiple experiences")
        Experience.objects.create(user_id=self.user, description="Experience 1 content.")
        Experience.objects.create(user_id=self.user, description="Experience 2 content.")

        request = self._setup_request()
        raw_content, processed_content = fetch_resume_content(request, self.user)

        self.assertEqual(raw_content, "Experience 1 content. Experience 2 content.")
        self.assertEqual(processed_content, "Experience 1 content. Experience 2 content.")
        print("Normal Case: Resume contains multiple experiences: pass\n")

    def test_edge_case_empty_experiences(self):
        """
        Test Case: Edge Case
        - Ensure the function handles users with no experiences.
        """
        print("Edge Case: No experiences for the user")
        request = self._setup_request()
        raw_content, processed_content = fetch_resume_content(request, self.user)

        self.assertEqual(raw_content, "")
        self.assertEqual(processed_content, "")
        print("Edge Case: No experiences for the user: pass\n")

    def test_corner_case_rewritten_resume_in_session(self):
        """
        Test Case: Corner Case
        - Ensure the function prioritizes rewritten content in the session over raw experiences.
        """
        print("Corner Case: Rewritten resume stored in the session")
        # Use the correct field name for the ForeignKey
        Experience.objects.create(user_id=self.user, description="Experience 1 content.")

        # Session contains rewritten resume content
        session_data = {"rewritten_resume": "Rewritten resume content."}

        request = self._setup_request(session_data)
        raw_content, processed_content = fetch_resume_content(request, self.user)

        self.assertEqual(raw_content, "Experience 1 content.")
        self.assertEqual(processed_content, "Rewritten resume content.")
        print("Corner Case: Rewritten resume stored in the session: pass\n")


    def test_corner_case_partial_session_data(self):
        """
        Test Case: Corner Case
        - Ensure the function gracefully handles an empty or malformed session.
        """
        print("Corner Case: Empty or malformed session data")
        Experience.objects.create(user_id=self.user, description="Experience 1 content.")

        # Simulate empty session
        request = self._setup_request(session_data={})
        raw_content, processed_content = fetch_resume_content(request, self.user)

        self.assertEqual(raw_content, "Experience 1 content.")
        self.assertEqual(processed_content, "Experience 1 content.")
        print("Corner Case: Empty or malformed session data: pass\n")


if __name__ == "__main__":
    """
    Main entry point for executing the test file.
    """
    import unittest
    unittest.main()
