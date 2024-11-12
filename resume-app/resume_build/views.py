from django.shortcuts import render, redirect
from .forms import ResumeForm

def create_resume(request):
    if request.method == 'POST':
        form = ResumeForm(request.POST)
        if form.is_valid():
            form.save()  # Save the data to the database
            return redirect('resume_success')  # Redirect after saving
    else:
        form = ResumeForm()

    return render(request, 'resume_build/create_resume.html', {'form': form})