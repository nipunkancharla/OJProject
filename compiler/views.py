# compiler/views.py
import subprocess
import tempfile
import shutil
from pathlib import Path
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def _execute_code_in_docker(code, language, input_data_path, expected_output_path=None):
    """
    A helper function that runs code in a Docker container and returns the result.
    It now accepts file paths instead of raw data.
    """
    temp_dir = tempfile.mkdtemp(dir="/tmp")
    temp_dir_path = Path(temp_dir)
    output = {}
    
    try:
        # --- NEW: Read input data from the file ---
        with open(input_data_path, 'r') as f:
            input_data = f.read()   

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

# --- UPDATE THE execute_code_api VIEW ---
@csrf_exempt
def execute_code_api(request):
    # This view is now only for the "Run" button with custom input
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code = data.get('code')
            language = data.get('language')
            input_data = data.get('input') # This is raw text from the user

            # Create a temporary file for the custom input
            with tempfile.NamedTemporaryFile(mode='w+', delete=False, dir='/tmp') as temp_input_file:
                temp_input_file.write(input_data)
                temp_input_file_path = temp_input_file.name
            
            result = _execute_code_in_docker(code, language, temp_input_file_path)
            
            # Clean up the temporary file
            os.remove(temp_input_file_path)

            return JsonResponse(result)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

