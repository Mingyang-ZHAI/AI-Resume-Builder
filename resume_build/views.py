import json
import time
import re

import openai
import pdfkit
import markdown
from sklearn.metrics.pairwise import cosine_similarity
from bs4 import BeautifulSoup
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from openai import OpenAI

from resume_build.forms import LoginForm, JobForm
from resume_build.models import User, Education, Experience, Job
from .utils.match_score import calculate_overall_score, calculate_skill_scores, calculate_title_degree_scores, generate_title_degree_report


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
        if request.method != 'POST':
            return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

        # Parse JSON data from request body
        res_data = json.loads(request.body)

        # Retrieve the user object
        user = User.objects.get(id=request.session['info']['id'])

        # Update basic user info
        user_data = res_data['basicInfo']
        User.objects.filter(id=request.session['info']['id']).update(
            name=user_data['name'],
            country=user_data['country'],
            city=user_data['city'],
            phone=user_data['phone'],
            email=user_data['email'],
            skills=res_data['skills']  # Assuming "skills" is stored as JSON or a list
        )

        # Process and update education data
        education_data = res_data.get('education', [])
        Education.objects.filter(user_id=user.id).delete()  # Clear old records

        education_objs = []
        for edu in education_data:
            # Parse year range for education (e.g., "2018-2022" or "2022-Present")
            year_range = edu.get('education_year', '')
            start_year, end_year = (
                year_range.split('-') if '-' in year_range else (None, None)
            )
            end_year = end_year if end_year != "Present" else None

            education_objs.append(
                Education(
                    user_id=user,
                    school_name=edu.get('education_school', 'Unknown School'),
                    degree=edu.get('education_degree', 'Unknown Degree'),
                    major=edu.get('education_major', 'Undeclared Major'),
                    start_year=int(start_year) if start_year and start_year.isdigit() else None,
                    end_year=int(end_year) if end_year and end_year.isdigit() else None,
                    gpa=float(edu.get('education_gpa', 0)) if edu.get('education_gpa') else None,
                    ongoing=end_year is None
                )
            )
        if education_objs:
            Education.objects.bulk_create(education_objs)

        # Process and update experience data
        experience_data = res_data.get('experience', [])
        Experience.objects.filter(user_id=user.id).delete()  # Clear old records

        experience_objs = []
        for exp in experience_data:
            # Parse year range for experience (e.g., "2020-2022" or "2021-Present")
            year_range = exp.get('experience_year', '')
            start_year, end_year = (
                year_range.split('-') if '-' in year_range else (None, None)
            )
            end_year = end_year if end_year != "Present" else None

            experience_objs.append(
                Experience(
                    user_id=user,
                    institution_name=exp.get('experience_company', 'Unknown Company'),
                    position=exp.get('experience_position', 'Unknown Position'),
                    start_year=int(start_year) if start_year and start_year.isdigit() else None,
                    end_year=int(end_year) if end_year and end_year.isdigit() else None,
                    description=exp.get('experience_description', ''),
                    ongoing=end_year is None
                )
            )
        if experience_objs:
            Experience.objects.bulk_create(experience_objs)

        return JsonResponse({'status': 'success', 'message': 'Your resume has been successfully updated.'}, status=200)

    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({'status': 'error', 'message': f'An error occurred: {e}'}, status=400)




def job_description(request):
    user = User.objects.get(id=request.session['info']['id'])
    if request.method == 'POST':
        job_title = request.POST.get('job_title', '').strip()
        description = request.POST.get('description', '').strip()

        if not job_title or not description:
            return render(request, 'resume_build/job_description.html', {
                'error': 'Both job title and description are required.'
            })

        # Save job data (if needed)
        job_data, created = Job.objects.update_or_create(
            user_id=user,
            defaults={'job_title': job_title, 'description': description}
        )

        # Generate the rewritten resume using AI
        rewritten_resume = rewrite_resume(user.id, job_title)

        # Redirect to show_resume with the rewritten resume
        return redirect(f'/show_resume/?rewritten_resume={json.dumps(rewritten_resume)}')

    return render(request, 'resume_build/job_description.html')


def show_resume(request):
    if request.method == 'POST':
        user_id = request.session['info']['id']
        job_title = request.POST.get('job_title', '')
        description = request.POST.get('description', '')

        # Fetch the User instance using user_id
        user = User.objects.get(id=user_id)

        # Store job description details if needed
        Job.objects.update_or_create(
            user_id=user,  # Use the User instance here
            defaults={'job_title': job_title, 'description': description},
        )

        # Rewrite the resume
        rewritten_resume = rewrite_resume(user_id, job_title, description)

        # Save the rewritten resume to the session
        request.session['rewritten_resume'] = rewritten_resume

    # Fetch the rewritten resume to display
    rewritten_resume = request.session.get('rewritten_resume', None)
    user = User.objects.get(id=request.session['info']['id'])

    context = {
        'name': user.name,
        'username': user.username,
        'country': user.country,
        'city': user.city,
        'phone': user.phone,
        'email': user.email,
        'rewritten_resume': rewritten_resume,
    }
    return render(request, 'resume.html', context)




def download_pdf(request):
    user = User.objects.get(id=request.session['info']['id'])

    job_response = Job.objects.filter(user_id=user.id).first()

    experiences = Experience.objects.filter(user_id=user)
    i = 0
    for exp in experiences:
        exp.content = job_response.response[i]
        i += 1
    context = {
        'name': user.name,
        'username': user.username,
        'country': user.country,
        'city': user.city,
        'phone': user.phone,
        'email': user.email,
        'skills': user.skills,
        'experiences': experiences,
        'education_list': Education.objects.filter(user_id=user),
    }
    html_content = render_to_string('resume_pdf.html', context)
    path_wkhtmltopdf = r"D:\wkhtmltopdf\bin\wkhtmltopdf.exe"  # 替换为实际路径
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    pdf = pdfkit.from_string(html_content, False, configuration=config)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{user.id}.pdf"'
    return response

    
def rewrite_resume(user_id, job_title, job_description):
    """
    Takes a user's resume data and rewrites it in a professional, HTML-formatted style for a specific job title and job description.
    """
    try:
        # Fetch user data
        user = User.objects.get(id=user_id)
        education = Education.objects.filter(user_id=user_id)
        experience = Experience.objects.filter(user_id=user_id)

        # Prepare details for the AI prompt
        education_details = "\n".join([
            f"{edu.school_name}, {edu.degree} in {edu.major} ({edu.start_year or 'N/A'}-{edu.end_year or 'Present'})"
            f"{' - GPA: ' + str(edu.gpa) if edu.gpa else ''}"
            for edu in education
        ])

        experience_details = "\n".join([
            f"{exp.position} at {exp.institution_name} ({exp.start_year or 'N/A'}-{exp.end_year or 'Present'}): {exp.description}"
            for exp in experience
        ])

        skills = ", ".join(user.skills) if user.skills else "Not specified"

        # AI prompt
        prompt = f"""
        Rewrite the following resume for a {job_title} position with the provided description ({job_description}). Structure the output in valid HTML format with the following sections:
        1. Summary
        2. Education
        3. Professional Experience
        4. Skills

        Improve the language, add professional wording, and tailor it to the job title while maintaining the facts.
        Highlight relevant skills and achievements, and add industry-appropriate points if necessary. 

        Output only the formatted resume. Do not include any additional notes, explanations, or comments. Use appropriate headings (e.g., <h2>, <h3>), paragraphs (<p>), and bullet points (<ul>, <li>). 

        Resume Details:
        Name: {user.name}
        Contact Information: Email - {user.email}, Phone - {user.phone}, Location - {user.city}, {user.country}
        Education:
        {education_details}
        Experience:
        {experience_details}
        Skills: {skills}
        """

        # Use the existing AI client to fetch the response
        client = OpenAI(
            base_url="https://api.studio.nebius.ai/v1/",
            api_key="eyJhbGciOiJIUzI1NiIsImtpZCI6IlV6SXJWd1h0dnprLVRvdzlLZWstc0M1akptWXBvX1VaVkxUZlpnMDRlOFUiLCJ0eXAiOiJKV1QifQ.eyJzdWIiOiJnb29nbGUtb2F1dGgyfDEwNjE1OTMwMzEwNTQyOTIxNzM4OCIsInNjb3BlIjoib3BlbmlkIG9mZmxpbmVfYWNjZXNzIiwiaXNzIjoiYXBpX2tleV9pc3N1ZXIiLCJhdWQiOlsiaHR0cHM6Ly9uZWJpdXMtaW5mZXJlbmNlLmV1LmF1dGgwLmNvbS9hcGkvdjIvIl0sImV4cCI6MTg5MDMzMTk3OCwidXVpZCI6IjEyZWExYTE0LWY4MDEtNGFjMy1hNDJkLWQ5NmVjNTQ4M2M5ZSIsIm5hbWUiOiJVbm5hbWVkIGtleSIsImV4cGlyZXNfYXQiOiIyMDI5LTExLTI1VDIwOjEyOjU4KzAwMDAifQ.HQ1oPQQGkwiIi8BJGh3459jj4pEbhOrp387-kpQ3xkY",
        )
        completion = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-70B-Instruct",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
        )
        response = json.loads(completion.to_json())['choices'][0]['message']['content']
        return response.strip()

    except Exception as e:
        print(f"Error rewriting resume: {e}")
        return "<p>An error occurred while rewriting the resume.</p>"


def rewrite_resume_view(request):
    if request.method == 'POST':
        user_id = request.session['info']['id']
        job_title = request.POST.get('job_title')
        description = request.POST.get('description', '')

        # Call the AI to rewrite the resume
        rewritten_resume = rewrite_resume(user_id, job_title, description)

        # Save the rewritten resume to the session
        request.session['rewritten_resume'] = rewritten_resume

        # Redirect to the show_resume page
        return JsonResponse({"redirect_url": "/show_resume/"})
    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)


def fetch_resume_content(request, user):
    """
    Fetch raw and processed resume content.
    """
    raw_resume_content = Experience.objects.filter(user_id=user.id).values_list('description', flat=True)
    raw_resume_content_combined = ' '.join(raw_resume_content)

    # Use rewritten resume from the session or fallback to raw content
    processed_resume_content = request.session.get('rewritten_resume', raw_resume_content_combined)

    return raw_resume_content_combined, processed_resume_content


def match_score_page(request):
    """
    Main view to calculate match score breakdown for both raw and AI-processed resume content.
    """
    user = User.objects.get(id=request.session['info']['id'])

    # Fetch job description
    job = Job.objects.filter(user_id=user.id).first()
    if not job:
        return render(request, 'match_score.html', {
            'error': 'No job description found for this user.',
        })

    # Fetch raw and processed resume content
    raw_resume_content, processed_resume_content = fetch_resume_content(request, user)

    # Calculate skill-based scores
    scores_and_reports = calculate_skill_scores(job, raw_resume_content, processed_resume_content)

    # Calculate degree and title scores
    raw_degree_score, raw_title_score = calculate_title_degree_scores(raw_resume_content, job)
    processed_degree_score, processed_title_score = calculate_title_degree_scores(processed_resume_content, job)

    # Ensure processed scores are not lower than raw scores
    processed_degree_score = max(processed_degree_score, raw_degree_score)
    processed_title_score = max(processed_title_score, raw_title_score)

    # Calculate overall scores
    raw_overall_score = calculate_overall_score(
        scores_and_reports["Hard Skills"]["raw_score"],
        scores_and_reports["Soft Skills"]["raw_score"],
        scores_and_reports["Keywords"]["raw_score"],
        raw_degree_score,
        raw_title_score,
    )

    processed_overall_score = calculate_overall_score(
        scores_and_reports["Hard Skills"]["processed_score"],
        scores_and_reports["Soft Skills"]["processed_score"],
        scores_and_reports["Keywords"]["processed_score"],
        processed_degree_score,
        processed_title_score,
    )

    # Generate title and degree reports
    raw_title_report = generate_title_degree_report(raw_title_score, "Job Title")
    processed_title_report = generate_title_degree_report(processed_title_score, "Job Title")
    raw_degree_report = generate_title_degree_report(raw_degree_score, "Degree")
    processed_degree_report = generate_title_degree_report(processed_degree_score, "Degree")

    # Render the response
    return render(request, 'match_score.html', {
        'raw_overall_score': raw_overall_score,
        'processed_overall_score': processed_overall_score,

        'raw_hard_skills_score': scores_and_reports["Hard Skills"]["raw_score"],
        'processed_hard_skills_score': scores_and_reports["Hard Skills"]["processed_score"],
        'raw_soft_skills_score': scores_and_reports["Soft Skills"]["raw_score"],
        'processed_soft_skills_score': scores_and_reports["Soft Skills"]["processed_score"],
        'raw_keywords_score': scores_and_reports["Keywords"]["raw_score"],
        'processed_keywords_score': scores_and_reports["Keywords"]["processed_score"],
        'raw_degree_score': raw_degree_score,
        'processed_degree_score': processed_degree_score,
        'raw_title_score': raw_title_score,
        'processed_title_score': processed_title_score,

        'raw_hard_skills_report': scores_and_reports["Hard Skills"]["raw_report"],
        'processed_hard_skills_report': scores_and_reports["Hard Skills"]["processed_report"],
        'raw_soft_skills_report': scores_and_reports["Soft Skills"]["raw_report"],
        'processed_soft_skills_report': scores_and_reports["Soft Skills"]["processed_report"],
        'raw_keywords_report': scores_and_reports["Keywords"]["raw_report"],
        'processed_keywords_report': scores_and_reports["Keywords"]["processed_report"],
        'raw_title_report': raw_title_report,
        'processed_title_report': processed_title_report,
        'raw_degree_report': raw_degree_report,
        'processed_degree_report': processed_degree_report,
    })
