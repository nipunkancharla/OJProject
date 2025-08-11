# compiler/views.py
import subprocess
import tempfile
import shutil
from pathlib import Path
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def _execute_code_in_docker(code, language, input_data):
    """
    A helper function that runs code in a Docker container and returns the result.
    This is the core execution logic.
    """
    temp_dir = tempfile.mkdtemp(dir="/tmp")
    temp_dir_path = Path(temp_dir)
    output = {}

    try:
        if language == 'python':
            file_name = "main.py"
            (temp_dir_path / file_name).write_text(code)
            # --- THE FIX IS HERE: Add the '-i' flag ---
            command = ['docker', 'run', '-i', '--rm', '--volume', f'{temp_dir_path}:/app', '--memory=256m', '--cpus=0.5', 'python:3.11-slim', 'python', f'/app/{file_name}']
        elif language == 'cpp':
            file_name = "main.cpp"
            (temp_dir_path / file_name).write_text(code)
            # --- THE FIX IS HERE: Add the '-i' flag ---
            command = ['docker', 'run', '-i', '--rm', '--volume', f'{temp_dir_path}:/app', '--memory=512m', '--cpus=0.5', 'gcc:latest', 'sh', '-c', f'g++ /app/{file_name} -o /app/program && /app/program']
        else:
            return {'error': 'Unsupported language'}

        # We use text=True to let subprocess handle encoding/decoding
        result = subprocess.run(
            command,
            input=input_data,
            capture_output=True,
            text=True, # This handles encoding automatically
            timeout=10
        )

        if result.returncode == 0:
            output['stdout'] = result.stdout
        else:
            output['stderr'] = result.stderr

    except subprocess.TimeoutExpired:
        output['error'] = 'Execution timed out (10 seconds).'
    except Exception as e:
        output['error'] = f'An unexpected error occurred: {e}'
    finally:
        shutil.rmtree(temp_dir_path)

    return output

# The test page view now uses the helper function
def compiler_test_page(request):
    context = {'output': '', 'code': '', 'language': 'python', 'input_data': ''}
    if request.method == 'POST':
        code = request.POST.get('code', '')
        language = request.POST.get('language', 'python')
        input_data = request.POST.get('input_data', '')

        context.update({'code': code, 'language': language, 'input_data': input_data})

        result = _execute_code_in_docker(code, language, input_data)
        context['output'] = result.get('stdout') or result.get('stderr') or result.get('error')

    return render(request, 'compiler/test_page.html', context)

# API view for our workspace to call
@csrf_exempt
def execute_code_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code = data.get('code')
            language = data.get('language')
            input_data = data.get('input')

            result = _execute_code_in_docker(code, language, input_data)
            return JsonResponse(result)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)
