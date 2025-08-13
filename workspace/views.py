# workspace/views.py
import json
import os
import tempfile
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from problemset.models import Problem
from .models import Submission

# Import the compiler logic directly
from compiler.views import _execute_code_in_docker

def solve_workspace(request, problem_slug):
    problem = get_object_or_404(Problem, slug=problem_slug)
    sample_testcases_content = []

    if problem.test_case_file:
        try:
            with problem.test_case_file.open('r') as f:
                data = json.load(f)
                # Get the first 2 test cases as samples
                sample_testcases_content = data.get("test_cases", [])[:2]
        except (IOError, json.JSONDecodeError):
            # Handle cases where file is missing, unreadable, or not valid JSON
            pass

    context = {
        'problem': problem,
        'sample_testcases_content': sample_testcases_content
    }
    return render(request, 'workspace/solver.html', context)

@csrf_exempt
def run_code(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code = data.get('code')
            language = data.get('language')
            input_data = data.get('input', '')

            with tempfile.NamedTemporaryFile(mode='w+', delete=False, dir='/tmp') as temp_input_file:
                temp_input_file.write(input_data)
                temp_input_file_path = temp_input_file.name

            result = {}
            try:
                result = _execute_code_in_docker(code, language, temp_input_file_path)
            finally:
                os.remove(temp_input_file_path)

            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
@csrf_exempt
def submit_code(request, problem_slug):
    problem = get_object_or_404(Problem, slug=problem_slug)
    if not problem.test_case_file:
        return JsonResponse({'status': 'System Error', 'message': 'No test cases found for this problem.'})

    try:
        data = json.loads(request.body)
        code_text = data.get('code') # Get the raw code as text
        language = data.get('language')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    # --- NEW LOGIC: Save code to a file first ---
    # Create a Django ContentFile from the code text
    code_file = ContentFile(code_text.encode('utf-8'))

    # Create a new Submission instance but don't save it to DB yet
    submission = Submission(
        user=request.user, 
        problem=problem, 
        language=language, 
        status='Pending'
    )

    # Save the ContentFile to the 'code' FileField
    # This will automatically use our 'get_submission_path' function
    file_name = f"submission.{language}"
    submission.code.save(file_name, code_file, save=True)
    # Now the submission object is fully saved in the database
    # --- END NEW LOGIC ---

    try:
        with problem.test_case_file.open('r') as f:
            test_data = json.load(f)
            all_testcases = test_data.get("test_cases", [])
    except (IOError, json.JSONDecodeError):
        submission.status = 'System Error'
        submission.output = 'Failed to read or parse test case file.'
        submission.save()
        return JsonResponse({'status': submission.status, 'message': submission.output})

    for i, testcase in enumerate(all_testcases, 1):
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, dir='/tmp') as temp_input_file:
            temp_input_file.write(testcase.get("input", ""))
            temp_input_file_path = temp_input_file.name

        result_data = {}
        try:
            # We now pass the raw code text to the execution engine
            result_data = _execute_code_in_docker(code_text, language, temp_input_file_path)
        finally:
            os.remove(temp_input_file_path)

        if result_data.get('stderr') or result_data.get('error'):
            submission.status = 'Runtime Error' if 'stderr' in result_data else 'System Error'
            submission.output = f"Failed on Test Case #{i}: {result_data.get('stderr') or result_data.get('error')}"
            submission.save()
            return JsonResponse({'status': submission.status, 'message': submission.output})

        actual_output = result_data.get('stdout', '').strip()
        expected_output = testcase.get("output", "").strip()

        if actual_output != expected_output:
            submission.status = 'Wrong Answer'
            submission.output = f"Wrong Answer on Test Case #{i}"
            submission.save()
            return JsonResponse({'status': submission.status, 'message': submission.output})

    submission.status = 'Accepted'
    submission.output = f"Passed all {len(all_testcases)} test cases."
    submission.save()
    return JsonResponse({'status': 'Accepted', 'message': submission.output})

@login_required
def get_submission_history(request, problem_slug):
    problem = get_object_or_404(Problem, slug=problem_slug)
    submissions = Submission.objects.filter(user=request.user, problem=problem).order_by('-submitted_at')

    # We now include the submission ID in the data
    data = [{
        'id': s.id, # Add the ID
        'status': s.status,
        'language': s.language,
        'submitted_at': s.submitted_at.strftime('%Y-%m-%d %H:%M:%S')
    } for s in submissions]

    return JsonResponse(data, safe=False)

# --- ADD THIS NEW VIEW ---
@login_required
def get_submission_details(request, submission_id):
    # Find the submission, ensuring it belongs to the current user for security
    submission = get_object_or_404(Submission, id=submission_id, user=request.user)

    try:
        with submission.code.open('r') as f:
            code_content = f.read()
    except IOError:
        return JsonResponse({'error': 'Could not read submission file.'}, status=500)

    data = {
        'code': code_content,
        'language': submission.language,
    }

    return JsonResponse(data)