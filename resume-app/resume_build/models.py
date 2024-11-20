from django.db import models

class Resume(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, default='DefaultCountryName')
    city = models.CharField(max_length=100, default='DefaultCityName')
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    skills = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name or "Unnamed Resume"

class Experience(models.Model):
    resume = models.ForeignKey(Resume, related_name='experiences', on_delete=models.CASCADE)
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
        return f"{self.institution_name} - {self.position} ({self.start_year}-{self.start_month} to {self.end_year}-{self.end_month})"

class Education(models.Model):
    resume = models.ForeignKey(Resume, related_name='educations', on_delete=models.CASCADE)
    start_year = models.IntegerField()
    start_month = models.IntegerField()
    end_year = models.IntegerField()
    end_month = models.IntegerField()
    school_name = models.CharField(max_length=255, default='Unknown School')  # Default value added
    major = models.CharField(max_length=255, default='Undeclared Major')  # Default value added
    gpa = models.FloatField(null=True, blank=True)  # Optional field
    content = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.school_name} ({self.start_year}-{self.start_month} to {self.end_year}-{self.end_month})"


