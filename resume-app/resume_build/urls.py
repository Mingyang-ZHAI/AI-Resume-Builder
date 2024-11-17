from django.urls import path
from . import views
from django.shortcuts import render


urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create_resume, name='create_resume'),
    path('signup/', views.signup, name='signup'),  # Fixed signup function reference
]