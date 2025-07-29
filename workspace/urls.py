# workspace/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('solve/<slug:problem_slug>/', views.solve_workspace, name='solve-workspace'),
    path('api/run-code/', views.run_code, name='run-code'),
    # Add the new URLs
    path('api/submit/<slug:problem_slug>/', views.submit_code, name='submit-code'),
    path('api/history/<slug:problem_slug>/', views.get_submission_history, name='get-submission-history'),
]