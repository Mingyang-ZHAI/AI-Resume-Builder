from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create_resume, name='create_resume'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('api/countries/', views.get_countries, name='get_countries'),
    path('api/cities/', views.get_cities, name='get_cities'),
    # path('generate_ai_response/', views.generate_ai_response, name='generate_ai_response'),
    path('summary/', views.summary, name='summary'),  # Add this line
    
]
