from django.db import models


class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(verbose_name="username", max_length=32)
    password = models.CharField(verbose_name="password", max_length=64)
    name = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, default='DefaultCountryName')
    city = models.CharField(max_length=100, default='DefaultCityName')
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    skills = models.JSONField(default=list)

    def __str__(self):
        return self.username


class Experience(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    start_year = models.IntegerField(null=True, blank=True)  # Allow null for "Present"
    end_year = models.IntegerField(null=True, blank=True)  # Allow null for "Present"
    institution_name = models.CharField(max_length=200, default='Unknown Company')
    position = models.CharField(max_length=100, default='Unknown Position')
    description = models.TextField(blank=True, null=True)  # Description for the experience
    ongoing = models.BooleanField(default=False)  # If the job is ongoing

    def __str__(self):
        end_year_display = self.end_year if not self.ongoing else "Present"
        return f"{self.position} at {self.institution_name} ({self.start_year} - {end_year_display})"


class Education(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    start_year = models.IntegerField(null=True, blank=True)  # Allow null for missing year
    end_year = models.IntegerField(null=True, blank=True)  # Allow null for "Present"
    school_name = models.CharField(max_length=255, default='Unknown School')
    degree = models.CharField(max_length=255, default='Unknown Degree')  # Degree field added
    major = models.CharField(max_length=255, default='Undeclared Major')
    gpa = models.FloatField(null=True, blank=True)  # Optional GPA field
    ongoing = models.BooleanField(default=False)  # If the education is ongoing

    def __str__(self):
        end_year_display = self.end_year if not self.ongoing else "Present"
        return f"{self.degree} at {self.school_name} ({self.start_year} - {end_year_display})"



class Job(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    job_title = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    response = models.JSONField(blank=True, null=True)
