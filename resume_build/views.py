import json
from io import BytesIO
from xhtml2pdf import pisa

from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from openai import OpenAI

from resume_build.forms import LoginForm
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

    # Pass blank fields if the user data is None or invalid
    resume_data = {
        'name': user.name or '',
        'country': user.country or '',
        'city': user.city or '',
        'phone': user.phone or '',
        'email': user.email or '',
        'skills': user.skills or [],
    }

    # Fetch the saved job data
    job = Job.objects.filter(user_id=user.id).first()
    job_data = {
        'job_title': job.job_title if job else '',
        'description': job.description if job else ''
    }

    return render(request, 'resume_build/create_resume.html', {
        'resume_data': resume_data,
        'educations': educations,
        'experiences': experiences,
        'job_data': job_data  # Pass job data to the template
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

        # Update job title and description
        job_title = res_data.get('job_title', '')
        description = res_data.get('description', '')
        Job.objects.update_or_create(
            user_id=user,
            defaults={'job_title': job_title, 'description': description}
        )
        
        return JsonResponse({'status': 'success', 'message': 'Your resume has been successfully updated.'}, status=200)

    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({'status': 'error', 'message': f'An error occurred: {e}'}, status=400)



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

        Make sure not to make up degrees like 'PhD' or 'Master' unless stated in the input.

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


def regenerate_resume(request):
    if request.method == "POST":
        user_id = request.session['info']['id']

        # Fetch job details
        job = Job.objects.filter(user_id=user_id).first()

        if not job:
            messages.error(request, "No job information available to regenerate the resume.")
            return redirect('show_resume')

        # Regenerate the resume
        rewritten_resume = rewrite_resume(user_id, job.job_title, job.description)
        request.session['rewritten_resume'] = rewritten_resume

        messages.success(request, "Resume regenerated successfully!")
        return redirect('show_resume')

    return JsonResponse({"error": "Invalid request method."}, status=400)


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
    raw_title_report = generate_title_degree_report(raw_title_score, "Title", job, raw_resume_content)
    processed_title_report = generate_title_degree_report(processed_title_score, "Title", job, raw_resume_content)
    raw_degree_report = generate_title_degree_report(raw_degree_score, "Degree", job, raw_resume_content)
    processed_degree_report = generate_title_degree_report(processed_degree_score, "Degree", job, raw_resume_content)

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

def refresh_match_score(request):
    if request.method == "POST":
        user_id = request.session['info']['id']

        # Fetch job details
        job = Job.objects.filter(user_id=user_id).first()

        if not job:
            messages.error(request, "No job information available to refresh the match score.")
            return redirect('match_score_page')

        # Recalculate the match score
        try:
            # Fetch raw and processed resume content
            user = User.objects.get(id=user_id)
            raw_resume_content, processed_resume_content = fetch_resume_content(request, user)

            # Calculate match scores and reports
            calculate_skill_scores(job, raw_resume_content, processed_resume_content)

            # Generate match score reports and refresh results
            messages.success(request, "Match scores refreshed successfully!")
        except Exception as e:
            print(f"Error refreshing match score: {e}")
            messages.error(request, "An error occurred while refreshing the match score.")

        return redirect('match_score_page')

    return JsonResponse({"error": "Invalid request method."}, status=400)



def generate_cover_letter(request):
    """
    Generates or retrieves the user's cover letter based on the job description and rewritten resume.
    """
    try:
        # Get the user and job details
        user = User.objects.get(id=request.session['info']['id'])
        job = Job.objects.filter(user_id=user.id).first()

        if not job:
            return render(request, 'cover_letter.html', {
                'error': 'No job description found. Please add a job description first.',
            })

        # Check if a cover letter is already stored in the session
        if 'generated_cover_letter' in request.session:
            cover_letter = request.session['generated_cover_letter']
        else:
            # Generate the cover letter using AI
            rewritten_resume = request.session.get('rewritten_resume', '')
            prompt = f"""
            Write a professional and compelling cover letter for a {job.job_title} position.
            Job Description: {job.description}

            Base the cover letter on the following resume:
            {rewritten_resume}

            Ensure the tone is professional, enthusiastic, and tailored to the job description.
            Highlight relevant skills and achievements, and add industry-appropriate points if necessary.
            Make sure not to make up information. Use the resume as a reference for the cover letter.
            Output only the formatted cover letter. Do not include any additional notes, explanations, or comments.
            Use appropriate headings (e.g., <h2>, <h3>), paragraphs (<p>), and bullet points (<ul>, <li>) where necessary.
            Maintain a professional and engaging tone and formatting throughout the cover letter.
            """

            # Call the AI API (assuming the same setup as your resume rewriting)
            client = OpenAI(
            base_url="https://api.studio.nebius.ai/v1/",
            api_key="eyJhbGciOiJIUzI1NiIsImtpZCI6IlV6SXJWd1h0dnprLVRvdzlLZWstc0M1akptWXBvX1VaVkxUZlpnMDRlOFUiLCJ0eXAiOiJKV1QifQ.eyJzdWIiOiJnb29nbGUtb2F1dGgyfDEwNjE1OTMwMzEwNTQyOTIxNzM4OCIsInNjb3BlIjoib3BlbmlkIG9mZmxpbmVfYWNjZXNzIiwiaXNzIjoiYXBpX2tleV9pc3N1ZXIiLCJhdWQiOlsiaHR0cHM6Ly9uZWJpdXMtaW5mZXJlbmNlLmV1LmF1dGgwLmNvbS9hcGkvdjIvIl0sImV4cCI6MTg5MDMzMTk3OCwidXVpZCI6IjEyZWExYTE0LWY4MDEtNGFjMy1hNDJkLWQ5NmVjNTQ4M2M5ZSIsIm5hbWUiOiJVbm5hbWVkIGtleSIsImV4cGlyZXNfYXQiOiIyMDI5LTExLTI1VDIwOjEyOjU4KzAwMDAifQ.HQ1oPQQGkwiIi8BJGh3459jj4pEbhOrp387-kpQ3xkY",
            )
            completion = client.chat.completions.create(
                model="meta-llama/Meta-Llama-3.1-70B-Instruct",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
            )
            cover_letter = json.loads(completion.to_json())['choices'][0]['message']['content']

            # Save the generated cover letter in the session
            request.session['generated_cover_letter'] = cover_letter

        # Render the cover letter
        return render(request, 'resume_build/cover_letter.html', {'cover_letter': cover_letter})

    except Exception as e:
        print(f"Error generating cover letter: {e}")
        return render(request, 'resume_build/cover_letter.html', {
            'error': 'An error occurred while generating the cover letter.',
        })


def download_cover_letter(request):
    """
    Generate a PDF for the cover letter content and serve it for download.
    """
    try:
        # Fetch the cover letter from the session
        cover_letter = request.session.get('generated_cover_letter', None)

        if not cover_letter:
            return HttpResponse("No cover letter available. Please generate one first.", status=404)

        # Render only the cover letter content into a minimal HTML template
        html_content = f"""
        <html>
        <head>
            <title>Cover Letter</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 20px; }}
                h2 {{ color: #333; }}
                p {{ margin: 10px 0; }}
                ul {{ margin: 10px 0; margin-bottom: 2px; padding-bottom: 2px; }}
                ul li {{ margin-bottom: 2px; padding-bottom: 2px; }}
            </style>
        </head>
        <body>
            {cover_letter}
        </body>
        </html>
        """

        # Create a PDF buffer
        pdf_buffer = BytesIO()
        pisa_status = pisa.CreatePDF(BytesIO(html_content.encode('utf-8')), dest=pdf_buffer)

        if pisa_status.err:
            return HttpResponse('Error generating PDF', status=500)

        # Serve the PDF as a downloadable response
        pdf_buffer.seek(0)
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="cover_letter.pdf"'
        return response

    except Exception as e:
        print(f"Error generating cover letter PDF: {e}")
        return HttpResponse("An error occurred while generating the cover letter PDF.", status=500)


def regenerate_cover_letter(request):
    """
    Clears the stored cover letter and regenerates a new one.
    """
    if request.method == "POST":
        if 'generated_cover_letter' in request.session:
            del request.session['generated_cover_letter']
        return redirect('generate_cover_letter')
    return JsonResponse({"error": "Invalid request method."}, status=400)


def download_template_resume(request):
    """
    Generate a PDF for the selected template using the rewritten resume.
    """
    try:
        # Check if user session is present
        if 'info' not in request.session:
            raise KeyError("User session is missing")

        # Fetch user information
        user = User.objects.get(id=request.session['info']['id'])
        rewritten_resume = request.session.get('rewritten_resume')

        if not rewritten_resume:
            return HttpResponse("No rewritten resume available. Please generate one first.", status=404)

        # Get the selected template from the query parameter
        template_name = request.GET.get('template', 'template1')  # Default to template1

        # Prepare context for rendering the template
        context = {
            'name': user.name,
            'email': user.email,
            'phone': user.phone,
            'city': user.city,
            'country': user.country,
            'rewritten_resume': rewritten_resume,
        }

        # Render the selected template to HTML
        template_path = f'resume_templates/{template_name}.html'
        html = render_to_string(template_path, context)

        # Convert HTML to PDF using xhtml2pdf
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{user.name}_resume.pdf"'
        pisa_status = pisa.CreatePDF(html, dest=response)

        if pisa_status.err:
            return HttpResponse('Error generating PDF', status=500)
        return response

    except Exception as e:
        print(f"Error generating PDF: {e}")
        return HttpResponse(f"An error occurred: {e}", status=500)

def template_preview(request):
    user_id = request.session['info']['id']
    job = Job.objects.filter(user_id=user_id).first()
    rewritten_resume = request.session.get('rewritten_resume', '')

    templates = [
        {'name': 'Template 1', 'id': 'template_1'},
        {'name': 'Template 2', 'id': 'template_2'},
        {'name': 'Template 3', 'id': 'template_3'},
        {'name': 'Template 4', 'id': 'template_4'},
    ]

    return render(request, 'resume_build/template_preview.html', {
        'rewritten_resume': rewritten_resume,
        'job': job,
        'templates': templates,
    })

def download_template_pdf(request, template_id):
    user_id = request.session['info']['id']
    rewritten_resume = request.session.get('rewritten_resume', '')
    template_mapping = {
        'template_1': 'resume_templates/template1.html',
        'template_2': 'resume_templates/template2.html',
        'template_3': 'resume_templates/template3.html',
        'template_4': 'resume_templates/template4.html',
    }

    template_path = template_mapping.get(template_id, 'resume_build/templates/template_1.html')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="resume_{template_id}.pdf"'

    html = render_to_string(template_path, {'rewritten_resume': rewritten_resume})
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse(f'We had some errors <pre>{html}</pre>')
    return response
