# problemset/models.py
from django.db import models
from django.utils.text import slugify

class Problem(models.Model):
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ]

    title = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    # A slug is a URL-friendly version of the title
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Auto-generate slug from title if it's not set
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class TestCase(models.Model):
    problem = models.ForeignKey(Problem, related_name='testcases', on_delete=models.CASCADE)
    input_data = models.TextField()
    expected_output = models.TextField()
    is_sample = models.BooleanField(default=False, help_text="Is this a sample test case visible to the user?")

    def __str__(self):
        return f"TestCase for {self.problem.title} ({'Sample' if self.is_sample else 'Hidden'})"
