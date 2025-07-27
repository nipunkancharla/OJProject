# problemset/views.py
from django.shortcuts import render
from .models import Problem

def problem_list(request):
    # Fetch all Problem objects from the database
    problems = Problem.objects.all()
    # Pass the list of problems to the template
    context = {
        'problems': problems
    }
    return render(request, 'problemset/problem_list.html', context)