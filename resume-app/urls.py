"""
URL configuration for resume-app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from resume_build.views import login_view, register_view, logout_view, index, create_resume, save_resume, \
    job_description, download_pdf, show_resume, match_score_page

urlpatterns = [
    path('', index, name='index'),
    path('admin/', admin.site.urls),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('index/', index, name='index'),
    path('create/', create_resume, name='create_resume'),
    path('save/', save_resume, name='save_resume'),
    path('job_description/', job_description, name='job_description'),
    path('show_resume/', show_resume, name='show_resume'),
    path('download_pdf/', download_pdf, name='download_pdf'),
    path('match_score_page/', match_score_page, name='match_score_page'),
]
