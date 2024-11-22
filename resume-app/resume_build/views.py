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

from django.shortcuts import render, redirect
from django.http import JsonResponse
import openai



from django.contrib.auth.decorators import login_required
from .models import Resume, Education, Experience

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Resume, Education, Experience
from .forms import ResumeForm, EducationForm, ExperienceForm
import openai

@login_required
def create_resume(request):
    # 获取用户的 Resume 对象（如果不存在，则创建一个新的）
    resume, created = Resume.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # 基本信息保存
        if 'save_resume' in request.POST:
            resume_form = ResumeForm(request.POST, instance=resume)
            if resume_form.is_valid():
                resume = resume_form.save()

                # 生成 AI 提示词
                prompt = f"""
                Name: {resume.name}
                Country: {resume.country}
                City: {resume.city}
                Phone: {resume.phone}
                Email: {resume.email}
                Skills: {resume.skills}
                """

                # 教育经历
                prompt += "\nEducation:\n"
                educations = Education.objects.filter(resume=resume)
                for edu in educations:
                    prompt += f"- {edu.start_year}/{edu.start_month} to {edu.end_year}/{edu.end_month}: {edu.school_name} ({edu.major}, GPA: {edu.gpa or 'N/A'})\n"

                # 工作经历
                prompt += "\nExperience:\n"
                experiences = Experience.objects.filter(resume=resume)
                for exp in experiences:
                    prompt += f"- {exp.start_year}/{exp.start_month} to {exp.end_year}/{exp.end_month}: {exp.institution_name} ({exp.position})\n"
                    if exp.department_and_role:
                        prompt += f"  Department: {exp.department_and_role}\n"
                    if exp.bullet_points:
                        for point in exp.bullet_points:
                            prompt += f"  * {point}\n"

                # 调用 OpenAI API
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
                        'resume_form': resume_form,
                        'education_form': EducationForm(),
                        'experience_form': ExperienceForm(),
                        'educations': educations,
                        'experiences': experiences,
                        'error': f"AI Error: {str(e)}"
                    })

        # 教育经历保存
        elif 'add_education' in request.POST:
            education_form = EducationForm(request.POST)
            if education_form.is_valid():
                education = education_form.save(commit=False)
                education.resume = resume  # 将教育经历与当前简历绑定
                # 从 POST 数据中获取 bullet_points 列表
                experience.bullet_points = request.POST.getlist('bullet_points[]')
                education.save()
                return redirect('create_resume')

        # 工作经历保存
        elif 'add_experience' in request.POST:
            experience_form = ExperienceForm(request.POST)
            if experience_form.is_valid():
                experience = experience_form.save(commit=False)
                experience.resume = resume  # 将工作经历与当前简历绑定
                experience.save()
                return redirect('create_resume')

    # 查询当前 Resume 的教育经历和工作经历
    educations = Education.objects.filter(resume=resume)
    experiences = Experience.objects.filter(resume=resume)

    return render(request, 'resume_build/create_resume.html', {
        'resume_form': ResumeForm(instance=resume),
        'education_form': EducationForm(),
        'experience_form': ExperienceForm(),
        'educations': educations,
        'experiences': experiences,
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


from .models import Resume

@login_required
def summary(request):
    try:
        resume = Resume.objects.get(user=request.user)
        educations = resume.education_set.all()
        experiences = resume.experience_set.all()
    except Resume.DoesNotExist:
        resume = None
        educations = []
        experiences = []

    return render(request, 'resume_build/summary.html', {
        'resume': resume,
        'educations': educations,
        'experiences': experiences,
    })




