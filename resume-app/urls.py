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
    show_resume, rewrite_resume_view, match_score_page, generate_cover_letter, \
    download_template_resume, download_template_pdf, template_preview, regenerate_cover_letter, \
    regenerate_resume, refresh_match_score, download_cover_letter, resume_options, upload_resume

urlpatterns = [
    path('', index, name='index'),
    path('admin/', admin.site.urls),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('index/', index, name='index'),
    path('create/', create_resume, name='create_resume'),
    path('save/', save_resume, name='save_resume'),
    path('show_resume/', show_resume, name='show_resume'),
    path('match_score_page/', match_score_page, name='match_score_page'),
    path("generate_cover_letter/", generate_cover_letter, name="generate_cover_letter"),
    path('download_template_resume/', download_template_resume, name='download_template_resume'),
    path('download_template/<str:template_id>/', download_template_pdf, name='download_template'),
    path('template_preview/', template_preview, name='template_preview'),
    path('regenerate_cover_letter/', regenerate_cover_letter, name='regenerate_cover_letter'),
    path('regenerate_resume/', regenerate_resume, name='regenerate_resume'),
    path('refresh_match_score/', refresh_match_score, name='refresh_match_score'),
    path('download_cover_letter/', download_cover_letter, name='download_cover_letter'),
    path('resume-options/', resume_options, name='resume_options'),
    path('upload-resume/', upload_resume, name='upload_resume'),

]
