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
from .models import Resume, Experience, Education
import openai

openai.api_key = "your_openai_api_key_here"
from django.shortcuts import render, redirect
from django.http import JsonResponse
import openai

def create_resume(request):
    if 'resume_data' not in request.session:
        request.session['resume_data'] = {
            'name': '',
            'country': '',
            'city': '',
            'phone': '',
            'email': '',
            'skills': '',
            'educations': [],
            'experiences': []
        }

    resume_data = request.session['resume_data']

    if request.method == 'POST':
        if 'save_resume' in request.POST:
            # Update basic information
            resume_data.update({
                'name': request.POST.get('name', resume_data['name']),
                'country': request.POST.get('country', resume_data['country']),
                'city': request.POST.get('city', resume_data['city']),
                'phone': request.POST.get('phone', resume_data['phone']),
                'email': request.POST.get('email', resume_data['email']),
                'skills': request.POST.get('skills', resume_data['skills']),
            })

            request.session['resume_data'] = resume_data  # Save back to session

            # Generate AI prompt and call API
            prompt = f"""
            Name: {resume_data['name']}
            Country: {resume_data['country']}
            City: {resume_data['city']}
            Phone: {resume_data['phone']}
            Email: {resume_data['email']}
            Skills: {resume_data['skills']}
            """
            prompt += "\nEducation:\n"
            for edu in resume_data['educations']:
                prompt += f"- {edu['start_year']}/{edu['start_month']} to {edu['end_year']}/{edu['end_month']}: {edu['school_name']} ({edu['major']}, GPA: {edu.get('gpa', 'N/A')})\n"

            prompt += "\nExperience:\n"
            for exp in resume_data['experiences']:
                prompt += f"- {exp['start_year']}/{exp['start_month']} to {exp['end_year']}/{exp['end_month']}: {exp['institution_name']} ({exp['position']})\n"
                for point in exp.get('bullet_points', []):
                    prompt += f"  * {point}\n"

            try:
                response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=prompt,
                    max_tokens=300
                )
                request.session['ai_summary'] = response.choices[0].text.strip()
                return redirect('summary')
            except Exception as e:
                return render(request, 'resume_build/create_resume.html', {
                    'resume_data': resume_data,
                    'error': f"AI Error: {str(e)}"
                })

        elif 'add_education' in request.POST:
            # Add education data
            education = {
                'start_year': request.POST.get('start_year'),
                'start_month': request.POST.get('start_month'),
                'end_year': request.POST.get('end_year'),
                'end_month': request.POST.get('end_month'),
                'school_name': request.POST.get('school_name'),
                'major': request.POST.get('major'),
                'gpa': request.POST.get('gpa'),
                'scholarships': request.POST.get('scholarships')
            }
            resume_data['educations'].append(education)
            request.session['resume_data'] = resume_data
            return redirect('create_resume')

        elif 'add_experience' in request.POST:
            # Add experience data
            experience = {
                'start_year': request.POST.get('start_year'),
                'start_month': request.POST.get('start_month'),
                'end_year': request.POST.get('end_year'),
                'end_month': request.POST.get('end_month'),
                'institution_name': request.POST.get('institution_name'),
                'position': request.POST.get('position'),
                'department_and_role': request.POST.get('department_and_role'),
                'bullet_points': request.POST.getlist('bullet_points[]')
            }
            resume_data['experiences'].append(experience)
            request.session['resume_data'] = resume_data
            return redirect('create_resume')

    return render(request, 'resume_build/create_resume.html', {
        'resume_data': resume_data,
        'ai_summary': request.session.get('ai_summary', ''),
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
from django.http import JsonResponse
import openai

def generate_ai_response(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input', '')

        if not user_input:
            return render(request, 'resume_build/create_resume.html', {
                'error': 'Please provide input for AI.',
            })

        # Call OpenAI API (make sure your API key is configured correctly)
        openai.api_key = "your_openai_api_key_here"
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=user_input,
                max_tokens=150
            )
            ai_output = response.choices[0].text.strip()
            return render(request, 'resume_build/summary.html', {'ai_output': ai_output})
        except Exception as e:
            return render(request, 'resume_build/create_resume.html', {
                'error': f"AI interaction failed: {e}",
            })


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

