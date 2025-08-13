# problemset/models.py
from django.db import models
from django.utils.text import slugify
import uuid
import os

# This helper function will create a unique path for the JSON file
def get_testcase_json_path(instance, filename):
    # e.g., testcases/problem_5/abc-123.json
    return os.path.join('testcases', f'problem_{instance.id}', f'{uuid.uuid4()}.json')

class Problem(models.Model):
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ]

    title = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    slug = models.SlugField(unique=True, blank=True)
    # --- NEW FIELD ---
    test_case_file = models.FileField(upload_to=get_testcase_json_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title