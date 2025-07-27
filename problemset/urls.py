# problemset/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # This will be our main page showing the problem list
    path('', views.problem_list, name='problem-list'),
]