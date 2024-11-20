from django.shortcuts import render, redirect
from .forms import ResumeForm
from django.http import JsonResponse
import openai
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

# 配置 OpenAI API Key
openai.api_key = "your_openai_api_key_here"

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # 检查用户名是否已存在
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'signup.html')

        # 创建用户
        user = User.objects.create_user(username=username, password=password)
        user.save()

        messages.success(request, 'Signup successful! You can now login.')
        return render(request, 'login.html')  # 跳转到登录页面
    return render(request, 'signup.html')


def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # 验证用户名和密码
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return render(request, 'home.html')  # 登录成功后跳转到主页
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password.'})
    return render(request, 'login.html')



from django.shortcuts import render
from django.http import JsonResponse
from .forms import ResumeForm
import openai
import requests

# 国家联想接口
# 示例国家数据
COUNTRIES = ['Canada', 'China', 'United States', 'India', 'Mexico']

def get_countries(request):
    query = request.GET.get('query', '')
    if not query:
        return JsonResponse({'error': 'No query provided'}, status=400)

    # 筛选匹配的国家
    suggestions = [country for country in COUNTRIES if query.lower() in country.lower()]
    return JsonResponse({'suggestions': suggestions})


# 城市联想接口
# 示例城市数据
CITIES = {
    'Canada': ['Toronto, ON', 'Vancouver, BC', 'Montreal, QC', 'Ottawa, ON'],
    'China': ['Beijing', 'Shanghai', 'Tianjin', 'Shenzhen'],
    'United States': ['New York, NY', 'Los Angeles, CA', 'Chicago, IL', 'Houston, TX'],
    'India': ['Delhi', 'Mumbai', 'Bangalore', 'Hyderabad'],
    'Mexico': ['Mexico City', 'Guadalajara', 'Monterrey']
}

def get_cities(request):
    query = request.GET.get('query', '')
    country = request.GET.get('country', '')
    suggestions = []

    if not query or not country:
        return JsonResponse({'error': 'Both query and country are required'}, status=400)

    # 检查国家是否在 CITIES 数据中
    if country in CITIES:
        suggestions = [city for city in CITIES[country] if query.lower() in city.lower()]

    return JsonResponse({'suggestions': suggestions})

from django.shortcuts import render, redirect
from .forms import ResumeForm, ExperienceForm, EducationForm
from .models import Experience, Education, Resume
import openai

def create_resume(request):
    # Retrieve session data or initialize default empty values
    resume_form = ResumeForm(request.POST or {
        'name': request.session.get('name', ''),
        'country': request.session.get('country', ''),
        'city': request.session.get('city', ''),
        'phone': request.session.get('phone', ''),
        'email': request.session.get('email', ''),
        'skills': request.session.get('skills', ''),
    })

    experience_form = ExperienceForm(request.POST or None)
    education_form = EducationForm(request.POST or None)

    # Load session data for experiences and educations
    experiences = request.session.get('experiences', [])
    educations = request.session.get('educations', [])

    if request.method == 'POST':
        # Check which button was clicked
        if 'save_resume' in request.POST:
            # Handle "Save Resume" action
            if resume_form.is_valid():
                # Save resume data to session
                resume = resume_form.cleaned_data
                request.session['name'] = resume['name']
                request.session['country'] = resume['country']
                request.session['city'] = resume['city']
                request.session['phone'] = resume['phone']
                request.session['email'] = resume['email']
                request.session['skills'] = resume['skills']

                # Redirect to the summary page
                return redirect('summary')

        elif 'add_experience' in request.POST:
            # Handle "Add Experience" action
            if experience_form.is_valid():
                experience = experience_form.cleaned_data
                experiences.append(experience)
                request.session['experiences'] = experiences
                return redirect('create_resume')

        elif 'add_education' in request.POST:
            # Handle "Add Education" action
            if education_form.is_valid():
                education = education_form.cleaned_data
                educations.append(education)
                request.session['educations'] = educations
                return redirect('create_resume')

    # Render the form with the existing data
    return render(request, 'resume_build/create_resume.html', {
        'resume_form': resume_form,
        'experience_form': experience_form,
        'education_form': education_form,
        'experiences': experiences,
        'educations': educations,
    })


def summary(request):
    # Retrieve data from the session
    resume = {
        'name': request.session.get('name', ''),
        'country': request.session.get('country', ''),
        'city': request.session.get('city', ''),
        'phone': request.session.get('phone', ''),
        'email': request.session.get('email', ''),
        'skills': request.session.get('skills', ''),
    }
    experiences = request.session.get('experiences', [])
    educations = request.session.get('educations', [])

    # Render the summary page
    return render(request, 'resume_build/summary.html', {
        'resume': resume,
        'experiences': experiences,
        'educations': educations,
    })



def generate_ai_summary(resume, experiences, educations):
    """
    Generate AI summary for the resume based on user-provided data.
    """
    try:
        content = f"Resume for {resume.name}:\n\n"
        content += f"Country: {resume.country}, City: {resume.city}\n"
        content += f"Phone: {resume.phone}, Email: {resume.email}\n"
        content += f"Skills: {resume.skills}\n\n"

        content += "Experience:\n"
        for exp in experiences:
            content += f"- {exp.start_year}/{exp.start_month} to {exp.end_year}/{exp.end_month}: "
            content += f"{exp.institution_name} - {exp.position}\n"
            if exp.bullet_points:
                for point in exp.bullet_points:
                    content += f"  - {point}\n"

        content += "\nEducation:\n"
        for edu in educations:
            content += f"- {edu.start_year}/{edu.start_month} to {edu.end_year}/{edu.end_month}: "
            content += f"{edu.school_name} ({edu.major}), GPA: {edu.gpa}\n"
            if edu.scholarships:
                content += f"  Scholarships: {edu.scholarships}\n"

        # Use OpenAI API to summarize or improve the content
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Please summarize and polish this resume content:\n{content}",
            max_tokens=300
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"AI Summary Error: {str(e)}"


def index(request):
    return render(request, 'resume_build/index.html')

from django.shortcuts import render

def summary(request):
    # Example: Retrieve data you want to display in the summary page
    resume_data = {
        'name': request.session.get('name', ''),
        'country': request.session.get('country', ''),
        'city': request.session.get('city', ''),
        'phone': request.session.get('phone', ''),
        'email': request.session.get('email', ''),
        'skills': request.session.get('skills', ''),
        'educations': request.session.get('educations', []),
        'experiences': request.session.get('experiences', [])
    }

    return render(request, 'resume_build/summary.html', {'resume_data': resume_data})

