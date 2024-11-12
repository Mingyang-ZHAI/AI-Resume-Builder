from django.db import models

class Resume(models.Model):
    job_title = models.CharField(max_length=100)
    summary = models.TextField()
    # More fields to be added...
    
    def __str__(self):
        return self.job_title
