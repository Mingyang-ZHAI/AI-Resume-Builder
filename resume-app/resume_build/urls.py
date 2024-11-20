from django.urls import path
from . import views
from django.shortcuts import render


urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create_resume, name='create_resume'),
    path('signup/', views.signup, name='signup'),  # Fixed signup function reference
    path('signin/', views.signin, name='signin'),
    path('api/countries/', views.get_countries, name='get_countries'),
    path('api/cities/', views.get_cities, name='get_cities'),

]