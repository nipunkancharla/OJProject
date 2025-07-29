# workspace/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import requests
import json
import time
from problemset.models import Problem
from .models import Submission
from django.conf import settings

# --- REFACTORED HELPER FUNCTION ---
def call_judge0_api(code, language, input_data):
    """A helper function to call the Judge0 API and poll for results."""
    api_url = 'https://judge0-ce.p.rapidapi.com/submissions'
    
    # Get the key from Django's settings, not a hardcoded variable
    api_key = settings.RAPIDAPI_KEY

    if not api_key:
        # Return an error if the API key is not set in the .env file
        return {'error': 'API key not configured in environment.'}

    payload = {
        "source_code": code,
        "language_id": get_language_id(language),
        "stdin": input_data
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com",
        "X-RapidAPI-Key": api_key
    }

    try:
        # Create the submission
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        submission_token = response.json().get('token')

        if not submission_token:
            return {'error': 'Failed to create submission on judge.'}

        # Poll for the result
        result_url = f"{api_url}/{submission_token}"
        while True:
            result_response = requests.get(result_url, headers=headers)
            result_response.raise_for_status()
            result_data = result_response.json()
            if result_data.get('status', {}).get('id', 0) > 2: # Status > 2 means it's finished
                return result_data
            time.sleep(0.25)
    except requests.exceptions.RequestException as e:
        # Handle network errors or bad responses from the API
        return {'error': f'API request failed: {e}'}


# This view displays the main solver page (no changes)
def solve_workspace(request, problem_slug):
    # ... (code is the same as before)
    problem = get_object_or_404(Problem, slug=problem_slug)
    sample_testcases = problem.testcases.filter(is_sample=True)
    context = { 'problem': problem, 'sample_testcases': sample_testcases }
    return render(request, 'workspace/solver.html', context)

# This view now uses the helper function
@csrf_exempt
def run_code(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            result_data = call_judge0_api(
                code=data.get('code'),
                language=data.get('language'),
                input_data=data.get('input')
            )
            return JsonResponse(result_data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

# This view also uses the helper function
@login_required
@csrf_exempt
def submit_code(request, problem_slug):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    problem = get_object_or_404(Problem, slug=problem_slug)
    hidden_testcases = problem.testcases.filter(is_sample=False)

    try:
        data = json.loads(request.body)
        code = data.get('code')
        language = data.get('language')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    submission = Submission.objects.create(
        user=request.user, problem=problem, code=code, language=language, status='Pending'
    )

    for i, testcase in enumerate(hidden_testcases, 1):
        result_data = call_judge0_api(code, language, testcase.input_data)

        if 'error' in result_data:
            submission.status = 'System Error'
            submission.output = result_data['error']
            submission.save()
            return JsonResponse({'status': submission.status, 'message': submission.output})

        status_desc = result_data.get('status', {}).get('description', 'Error')

        if status_desc != 'Accepted':
            submission.status = status_desc
            submission.output = f"Failed on Test Case #{i}: {result_data.get('stderr') or result_data.get('compile_output', '')}"
            submission.save()
            return JsonResponse({'status': submission.status, 'message': submission.output})

        actual_output = result_data.get('stdout', '').strip()
        expected_output = testcase.expected_output.strip()

        if actual_output != expected_output:
            submission.status = 'Wrong Answer'
            submission.output = f"Wrong Answer on Test Case #{i}"
            submission.save()
            return JsonResponse({'status': submission.status, 'message': submission.output})

    submission.status = 'Accepted'
    submission.output = f"Passed all {len(hidden_testcases)} test cases."
    submission.save()
    return JsonResponse({'status': 'Accepted', 'message': submission.output})

# --- History View and get_language_id (no changes) ---
@login_required
def get_submission_history(request, problem_slug):
    # ... (code is the same as before)
    problem = get_object_or_404(Problem, slug=problem_slug)
    submissions = Submission.objects.filter(user=request.user, problem=problem).order_by('-submitted_at')
    data = [{'status': s.status, 'language': s.language, 'submitted_at': s.submitted_at.strftime('%Y-%m-%d %H:%M:%S')} for s in submissions]
    return JsonResponse(data, safe=False)

def get_language_id(language):
    # ... (code is the same as before)
    if language == 'python': return 71
    elif language == 'cpp': return 54
    elif language == 'java': return 62
    return 71
