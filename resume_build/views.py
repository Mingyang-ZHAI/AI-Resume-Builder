import json

import openai
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.shortcuts import render, redirect

from resume_build.forms import LoginForm, JobForm
from resume_build.models import User, Education, Experience

# 配置 OpenAI API Key
openai.api_key = "your_openai_api_key_here"


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try:
                user = User.objects.get(username=username)
                if check_password(password, user.password):
                    # The site generates random strings; Write to the cookie of the user's browser; Write to session
                    request.session["info"] = {'id': user.id, 'name': user.username}
                    # session can be saved for 7 days
                    request.session.set_expiry(60 * 60 * 24 * 7)
                    return redirect('index')
                else:
                    messages.error(request, "Invalid credentials. Please try again.")
            except User.DoesNotExist:
                messages.error(request, "Invalid credentials. Please try again.")
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return render(request, 'account/register.html')
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return render(request, 'account/register.html')
        user = User(username=username, password=make_password(password))
        user.save()
        messages.success(request, "Registration successful! You can now log in.")
        return redirect('login')
    return render(request, 'account/register.html')


def logout_view(request):
    request.session.clear()
    return redirect('/login/')


def index(request):
    return render(request, 'resume_build/index.html')


def create_resume(request):
    user = User.objects.get(id=request.session['info']['id'])
    educations = Education.objects.filter(user_id=request.session['info']['id']).values()
    educations = json.dumps(list(educations))
    experiences = Experience.objects.filter(user_id=request.session['info']['id']).values()
    experiences = json.dumps(list(experiences))

    return render(request, 'resume_build/create_resume.html', {
        'resume_data': user,
        'educations': educations,
        'experiences': experiences
    })


def save_resume(request):
    try:
        # Retrieve the user object based on session ID
        user = User.objects.get(id=request.session['info']['id'])
        res_data = json.loads(request.body)

        # Update basic user info
        user_data = res_data['basicInfo']
        User.objects.filter(id=request.session['info']['id']).update(
            name=user_data['name'],
            country=user_data['country'],
            city=user_data['city'],
            phone=user_data['phone'],
            email=user_data['email'],
            skills=res_data['skills']
        )

        # Process and update education data
        education_data = res_data.get('education', [])
        # Delete all existing education records for the user
        Education.objects.filter(user_id=user.id).delete()

        # Insert new education records
        education_objs = []
        for edu in education_data:
            education_objs.append(Education(
                user_id=user,
                start_year=int(edu.get('education_start_year', 0)) or None,
                start_month=int(edu.get('education_start_month', 0)) or None,
                end_year=int(edu.get('education_end_year', 0)) or None,
                end_month=int(edu.get('education_end_month', 0)) or None,
                school_name=edu.get('education_school_name', 'Unknown School'),
                major=edu.get('education_major', 'Undeclared Major'),
                gpa=float(edu.get('education_gpa', 0)) or None,
                scholarships=edu.get('education_scholarships', '')
            ))

        if education_objs:
            Education.objects.bulk_create(education_objs)

        # Process and update experience data
        experience_data = res_data.get('experience', [])
        # Delete all existing experience records for the user
        Experience.objects.filter(user_id=user.id).delete()

        # Insert new experience records
        experience_objs = []
        for exp in experience_data:
            experience_objs.append(Experience(
                user_id=user,
                start_year=int(exp.get('experience_start_year', 0)) or None,
                start_month=int(exp.get('experience_start_month', 0)) or None,
                end_year=int(exp.get('experience_end_year', 0)) or None,
                end_month=int(exp.get('experience_end_month', 0)) or None,
                institution_name=exp.get('experience_institution_name', ''),
                position=exp.get('experience_position', ''),
                department_and_role=exp.get('experience_department_and_role', ''),
                content=exp.get('content', ''),
                bullet_points=exp.get('bullet_points', [])
            ))

        if experience_objs:
            Experience.objects.bulk_create(experience_objs)

        return JsonResponse({'status': 'success', 'message': 'Your resume has been successfully updated.'}, status=200)
    except Exception as e:
        # Return error response
        return JsonResponse({'status': 'error', 'message': f'An error occurred: {e}'}, status=400)


def job_description(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            # Handle the valid form data here (save to database, send email, etc.)
            job_title = form.cleaned_data['job_title']
            description = form.cleaned_data['description']
            # For now, let's just display a success message
            messages.success(request, 'Job posted successfully!')
            return redirect('job_description')  # redirect back to the form (or somewhere else)
    else:
        form = JobForm()
    return render(request, 'resume_build/job_description.html', {'form': form})
