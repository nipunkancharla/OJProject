# core/views.py
from django.shortcuts import render

def home(request):
    return render(request, 'core/home.html')

def contests(request):
    return render(request, 'core/contests.html')

def dashboard(request):
    return render(request, 'core/dashboard.html')

def resources(request):
    return render(request, 'core/resources.html')
