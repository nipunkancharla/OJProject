# users/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views # Import our own views

urlpatterns = [
    # Add the new signup URL
    path('signup/', views.signup, name='signup'),

    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'), # No template needed for POST logout
    path('', views.home, name='home'),
]