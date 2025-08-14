# I Love Problem Solving - An Online Judge Platform

Welcome to the repository for **iloveproblemsolving.fun**, a full-featured online judge and competitive programming platform built with Django and Docker. This project allows users to sign up, solve algorithmic challenges in a web-based code editor, and receive instant feedback on their solutions.

The platform features a custom-built, secure code execution engine that uses Docker to run user-submitted code in isolated containers, providing a safe and scalable environment for judging solutions.

**Live Website:** [**http://iloveproblemsolving.fun**](http://iloveproblemsolving.fun)

---

## Features

- **User Authentication:** Secure user registration, login, and logout system.
- **Problem Catalog:** A browsable list of coding problems, categorized by difficulty.
- **Interactive Workspace:** A two-pane view with the problem description on one side and a feature-rich Ace Code Editor on the other.
- **Custom Code Execution:**
  - Supports multiple languages (Python, C++).
  - **Run Code:** Execute code against sample or custom test cases for quick debugging.
  - **Submit Code:** Judge code against a full suite of hidden test cases.
- **Secure Sandbox:** All user code is executed inside temporary, isolated Docker containers to ensure server security.
- **Submission History:** Users can view their past submissions for any problem and load the code back into the editor.
- **Admin Panel:** A custom Django admin interface for easily adding new problems and managing test case files.

---

## Technologies & Frameworks Used

- **Backend:**
  - **Framework:** Django
  - **Production Server:** Gunicorn
- **Frontend:**
  - HTML5
  - CSS3 with **Bootstrap 5**
  - JavaScript (for API calls and DOM manipulation)
  - **Ace Editor** (for the in-browser code editor)
- **Database:**
  - SQLite (for local development)
- **Code Execution Engine:**
  - **Docker:** For creating secure, isolated sandboxes for code execution.
  - **Python `subprocess` Module:** To control the Docker daemon from the Django application.
- **Deployment & Infrastructure:**
  - **Cloud Provider:** Amazon Web Services (AWS)
  - **Virtual Server:** EC2 Instance
  - **Web Server / Reverse Proxy:** Nginx
  - **Containerization:** Docker & Docker Compose

---

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Git
- Docker
- Docker Compose

### Local Development

1.  **Clone the repository:**

    ```bash
    git clone [https://github.com/nipunkancharla/OJProject.git](https://github.com/nipunkancharla/OJProject.git)
    cd OJProject
    ```

2.  **Create an environment file:**
    Create a file named `.env` in the project root. This file is for your local development secrets.

    ```
    # .env
    SECRET_KEY=your_local_django_secret_key
    DEBUG=True
    ALLOWED_HOSTS=localhost,127.0.0.1
    ```

3.  **Build and run the development containers:**
    This command will build the image specified in `Dockerfile` and start the Django development server.

    ```bash
    docker-compose up --build
    ```

4.  **Apply database migrations:**
    In a separate terminal, run the following commands to set up your local database and create an admin user.

    ```bash
    docker-compose exec web python manage.py migrate
    docker-compose exec web python manage.py createsuperuser
    ```

5.  **Access the site:**
    You can now access the local version of the site at **http://localhost:8000**. The Django admin panel is available at `http://localhost:8000/admin/`.
