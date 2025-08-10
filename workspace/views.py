# workspace/views.py
import requests
import json
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from problemset.models import Problem
from .models import Submission

# --- UPDATED HELPER FUNCTION TO CALL OUR OWN COMPILER ---
def call_internal_compiler(code, language, input_data):
    url = "http://web:8000/compiler/api/execute/"

    payload = {
        'code': code,
        'language': language,
        'input': input_data
    }
    headers = {
        'Content-Type': 'application/json'
    }
    try:
        # We now manually encode the payload and set the headers
        response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {'error': f'Failed to connect to compiler service: {e}'}

# The run_code view now uses our internal compiler
@csrf_exempt
def run_code(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            result_data = call_internal_compiler(
                code=data.get('code'),
                language=data.get('language'),
                input_data=data.get('input')
            )
            # We add a 'status' key to mimic Judge0's output for simplicity on the frontend
            if result_data.get('stderr') or result_data.get('error'):
                result_data['status'] = {'description': 'Error'}
            else:
                result_data['status'] = {'description': 'Accepted'}

            return JsonResponse(result_data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

# The submit_code view now uses our internal compiler
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

    submission = Submission.objects.create(user=request.user, problem=problem, code=code, language=language, status='Pending')

    for i, testcase in enumerate(hidden_testcases, 1):
        result_data = call_internal_compiler(code, language, testcase.input_data)

        if result_data.get('stderr') or result_data.get('error'):
            submission.status = 'Runtime Error' if 'stderr' in result_data else 'System Error'
            submission.output = f"Failed on Test Case #{i}: {result_data.get('stderr') or result_data.get('error')}"
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

# solve_workspace and get_submission_history views do not need any changes
def solve_workspace(request, problem_slug):
    problem = get_object_or_404(Problem, slug=problem_slug)
    sample_testcases = problem.testcases.filter(is_sample=True)
    context = { 'problem': problem, 'sample_testcases': sample_testcases }
    return render(request, 'workspace/solver.html', context)

@login_required
def get_submission_history(request, problem_slug):
    problem = get_object_or_404(Problem, slug=problem_slug)
    submissions = Submission.objects.filter(user=request.user, problem=problem).order_by('-submitted_at')
    data = [{'status': s.status, 'language': s.language, 'submitted_at': s.submitted_at.strftime('%Y-%m-%d %H:%M:%S')} for s in submissions]
    return JsonResponse(data, safe=False)