# compiler/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('test/', views.compiler_test_page, name='compiler-test-page'),
    # New API endpoint for internal use
    path('api/execute/', views.execute_code_api, name='execute-code-api'),
]