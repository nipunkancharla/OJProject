# problemset/admin.py
from django.contrib import admin
from .models import Problem, TestCase

class TestCaseInline(admin.TabularInline):
    model = TestCase
    extra = 1 # Show 1 extra empty form for a new test case

class ProblemAdmin(admin.ModelAdmin):
    inlines = [TestCaseInline]
    list_display = ('title', 'difficulty', 'created_at')
    list_filter = ('difficulty',)
    # Prepopulate the slug field automatically from the title in the admin
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(Problem, ProblemAdmin)