# problemset/admin.py
from django.contrib import admin
from .models import Problem

class ProblemAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty', 'created_at')
    list_filter = ('difficulty',)

admin.site.register(Problem, ProblemAdmin)
