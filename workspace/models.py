# workspace/models.py
from django.db import models
from django.conf import settings
from problemset.models import Problem
import uuid
import os

# This helper function will create a unique path for each submission file
def get_submission_path(instance, filename):
    # e.g., submissions/user_1/problem_5/abc-123.py
    return os.path.join(
        'submissions', 
        f'user_{instance.user.id}', 
        f'problem_{instance.problem.id}', 
        f'{uuid.uuid4()}.{instance.language}'
    )

class Submission(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Wrong Answer', 'Wrong Answer'),
        ('Time Limit Exceeded', 'Time Limit Exceeded'),
        ('Compilation Error', 'Compilation Error'),
        ('Runtime Error', 'Runtime Error'),
        ('System Error', 'System Error'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    # --- FIELD CHANGE HERE ---
    # The 'code' field is now a FileField
    code = models.FileField(upload_to=get_submission_path)
    language = models.CharField(max_length=50)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    output = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Submission by {self.user.username} for {self.problem.title} at {self.submitted_at}"
