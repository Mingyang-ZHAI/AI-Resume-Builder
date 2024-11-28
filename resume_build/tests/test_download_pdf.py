from django.test import TestCase, RequestFactory
from unittest.mock import patch, MagicMock
from resume_build.models import User
from resume_build.views import download_pdf
from io import BytesIO
from django.http import HttpResponse

"""
Function Explanation:
This test suite validates the `download_pdf` function. It ensures the function generates and serves a PDF
of the rewritten resume for download, handling different scenarios gracefully.

Parameter Explanation:
- `request`: A Django HTTP request object containing user session data.
"""

class DownloadPDFTests(TestCase):
    def setUp(self):
        """
        Set up test data for the tests. This includes creating a test user and preparing session data.
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
        request = self.factory.get("/download_pdf/")
        request.session = session_data or {}
        return request

    @patch("resume_build.views.render_to_string")
    @patch("resume_build.views.pisa.CreatePDF")
    def test_normal_case(self, mock_create_pdf, mock_render_to_string):
        """
        Test Case: Normal Case
        - Ensure the function generates a PDF when rewritten resume data is available.
        """
        print("Normal Case: Resume partially matches job requirements")
        mock_render_to_string.return_value = "<html><body><h1>Test Resume</h1></body></html>"
        mock_create_pdf.return_value = MagicMock(err=False)

        session_data = {
            "info": {"id": self.user.id},
            "rewritten_resume": "<h1>Test Resume</h1>",
        }
        request = self._setup_request(session_data)

        response = download_pdf(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment; filename="resume.pdf"', response['Content-Disposition'])
        print("Normal Case: Resume partially matches job requirements: pass\n")

    @patch("resume_build.views.render_to_string")
    def test_edge_case_no_rewritten_resume(self, mock_render_to_string):
        """
        Test Case: Edge Case
        - Ensure the function handles cases where no rewritten resume is available.
        """
        print("Edge Case: No rewritten resume available")
        mock_render_to_string.return_value = ""

        session_data = {
            "info": {"id": self.user.id},
            "rewritten_resume": None,  # No rewritten resume in session
        }
        request = self._setup_request(session_data)

        response = download_pdf(request)

        self.assertEqual(response.status_code, 404)
        self.assertIn("No rewritten resume available", response.content.decode('utf-8'))
        print("Edge Case: No rewritten resume available: pass\n")

    @patch("resume_build.views.render_to_string")
    @patch("resume_build.views.pisa.CreatePDF")
    def test_corner_case_pdf_generation_error(self, mock_create_pdf, mock_render_to_string):
        """
        Test Case: Corner Case
        - Ensure the function handles errors during PDF generation gracefully.
        """
        print("Corner Case: PDF generation error")
        mock_render_to_string.return_value = "<html><body><h1>Test Resume</h1></body></html>"
        mock_create_pdf.return_value = MagicMock(err=True)  # Simulate PDF generation error

        session_data = {
            "info": {"id": self.user.id},
            "rewritten_resume": "<h1>Test Resume</h1>",
        }
        request = self._setup_request(session_data)

        response = download_pdf(request)

        self.assertEqual(response.status_code, 500)
        self.assertIn("Error generating PDF", response.content.decode('utf-8'))
        print("Corner Case: PDF generation error: pass\n")

    def test_corner_case_no_user_session(self):
        """
        Test Case: Corner Case
        - Ensure the function handles cases where the user session is missing.
        """
        print("Corner Case: Missing user session")
        request = self._setup_request(session_data={})  # Empty session

        with self.assertRaises(KeyError):
            download_pdf(request)
        print("Corner Case: Missing user session: pass\n")


if __name__ == "__main__":
    """
    Main entry point for executing the test file.
    """
    import unittest
    unittest.main()
