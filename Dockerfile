# Dockerfile

# 1. Start with an official Python base image
FROM python:3.11-slim

# 2. Set environment variables to prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Set the working directory inside the container
WORKDIR /app

# 4. Copy the requirements file into the container
COPY requirements.txt /app/

# 5. Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of your project's code into the container
COPY . /app/

# 7. Expose the port the app runs on
EXPOSE 8000

# 8. Define the command to run your app
# We use 0.0.0.0 to make it accessible from outside the container
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]