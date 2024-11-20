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
from .models import Experience, Education

def create_resume(request):
    resume_form = ResumeForm()
    experience_form = ExperienceForm()
    education_form = EducationForm()
    experiences = Experience.objects.all()
    educations = Education.objects.all()

    if request.method == 'POST':
        resume_form = ResumeForm(request.POST)
        experience_form = ExperienceForm(request.POST)
        education_form = EducationForm(request.POST)

        if resume_form.is_valid():
            resume = resume_form.save()

            if 'add_experience' in request.POST:
                if experience_form.is_valid():
                    experience = experience_form.save(commit=False)
                    experience.resume = resume

                    # Handle multiple bullet points
                    bullet_points = request.POST.getlist('bullet_points[]')
                    if bullet_points:
                        experience.bullet_points = bullet_points

                    experience.save()

            if 'add_education' in request.POST:
                if education_form.is_valid():
                    education = education_form.save(commit=False)
                    education.resume = resume
                    education.save()

            # Redirect after successful submission
            return redirect('create_resume')
        else:
            # Display errors for invalid forms
            return render(request, 'resume_build/create_resume.html', {
                'resume_form': resume_form,
                'experience_form': experience_form,
                'education_form': education_form,
                'experiences': experiences,
                'educations': educations,
            })

    return render(request, 'resume_build/create_resume.html', {
        'resume_form': resume_form,
        'experience_form': experience_form,
        'education_form': education_form,
        'experiences': experiences,
        'educations': educations,
    })



def index(request):
    return render(request, 'resume_build/index.html')
