# users/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm

def home(request):
    return render(request, 'users/home.html')

def signup(request):
    if request.method == 'POST':
        # If the form is submitted, create a form instance with the POST data
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save() # This saves the new user to the database
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now login.')
            return redirect('login') # Redirect to the login page after successful registration
    else:
        # If it's a GET request, just create an empty form
        form = UserRegisterForm()
    return render(request, 'users/signup.html', {'form': form})