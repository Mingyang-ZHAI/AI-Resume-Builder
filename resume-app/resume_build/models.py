from django.db import models
from django.contrib.auth.models import User

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes', null=True, blank=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, default='DefaultCountryName')
    city = models.CharField(max_length=100, default='DefaultCityName')
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    skills = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name or "Unnamed Resume"

class Experience(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, null=True, blank=True)
    start_year = models.IntegerField()
    start_month = models.IntegerField()
    end_year = models.IntegerField()
    end_month = models.IntegerField()
    institution_name = models.CharField(max_length=200, default='Unknown Institution')
    position = models.CharField(max_length=100, default='Unknown Position')
    department_and_role = models.TextField(default='Not Specified')  # Add a default value
    content = models.TextField(blank=True, null=True)  # Optional field
    bullet_points = models.JSONField(default=list)  # Store bullet points as a list

    def __str__(self):
        # Construct a detailed string representation
        details = (
            f"Institution: {self.institution_name}, "
            f"Position: {self.position}, "
            f"Department: {self.department_and_role}, "
            f"Period: {self.start_year}-{self.start_month} to {self.end_year}-{self.end_month}, "
            f"Content: {self.content or 'No content provided'}, "
            f"Bullet Points: {', '.join(self.bullet_points) if self.bullet_points else 'None'}"
        )
        return details

    
class Education(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, null=True, blank=True) 
    start_year = models.IntegerField()
    start_month = models.IntegerField()
    end_year = models.IntegerField()
    end_month = models.IntegerField()
    school_name = models.CharField(max_length=255, default='Unknown School')  # Default value added
    major = models.CharField(max_length=255, default='Undeclared Major')  # Default value added
    gpa = models.FloatField(null=True, blank=True)  # Optional field
    scholarships = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.school_name} ({self.start_year}-{self.start_month} to {self.end_year}-{self.end_month})"


