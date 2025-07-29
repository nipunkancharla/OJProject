# workspace/models.py
from django.db import models
from django.conf import settings
from problemset.models import Problem

class Submission(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Wrong Answer', 'Wrong Answer'),
        ('Time Limit Exceeded', 'Time Limit Exceeded'),
        ('Compilation Error', 'Compilation Error'),
        ('Runtime Error', 'Runtime Error'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    code = models.TextField()
    language = models.CharField(max_length=50)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    output = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Submission by {self.user.username} for {self.problem.title} at {self.submitted_at}"
