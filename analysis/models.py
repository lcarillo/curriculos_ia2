from django.db import models
from django.contrib.auth.models import User
from resumes.models import Resume
from jobs.models import JobPosting


class Analysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE)
    score = models.FloatField(null=True, blank=True)
    metrics = models.JSONField(null=True, blank=True)
    suggestions = models.TextField(null=True, blank=True)
    optimized_resume = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Analyses'

    def __str__(self):
        return f"Analysis: {self.resume.file_name} ↔ {self.job.title}"