# from django.shortcuts import render, redirect
# from .forms import ResumeForm

# def index(request):
#     return render(request, 'resume_build/index.html')


# def create_resume(request):
#     if request.method == 'POST':
#         form = ResumeForm(request.POST)
#         if form.is_valid():
#             form.save()  # Save the data to the database
#             return redirect('index')  # Redirect after saving
#     else:
#         form = ResumeForm()

#     return render(request, 'resume_build/create_resume.html', {'form': form})

from django.shortcuts import render, redirect
from .forms import ResumeForm
from django.http import JsonResponse
import openai
from django.contrib import messages

# 配置 OpenAI API Key
openai.api_key = "your_openai_api_key_here"


def signup(request):
    if request.method == 'POST':
        # Example: Fetch form data
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Implement signup logic here (e.g., save user data to the database)
        if username and password:
            # You can add user creation logic here
            messages.success(request, f'Account created for {username}!')

            # Redirect to a specific page after successful signup
            return redirect('index')  # Change 'index' to your desired page name
        else:
            messages.error(request, 'Please fill in all required fields.')

    # Render the signup page if GET request or validation fails
    return render(request, 'signup.html')

def create_resume(request):
    if request.method == 'POST':
        form = ResumeForm(request.POST)
        if form.is_valid():
            # 保存用户提交的数据
            resume = form.save()

            # 构建 GPT prompt
            prompt = f"""
            Optimize the following resume information:

            Name: {resume.name}
            Email: {resume.email}
            Phone: {resume.phone}

            Education:
            {resume.education}

            Skills:
            {resume.skills}

            Work Experience:
            {resume.work_experience}

            Additional Information:
            {resume.additional_info}
            """

            # 调用 GPT API
            try:
                response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=prompt,
                    max_tokens=500,
                    temperature=0.7,
                )
                optimized_resume = response.choices[0].text.strip()

                return render(request, 'optimized_resume.html', {
                    'optimized_resume': optimized_resume,
                    'form': form
                })

            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
    else:
        form = ResumeForm()

    return render(request, 'create_resume.html', {'form': form})

def index(request):
    return render(request, 'resume_build/index.html')
