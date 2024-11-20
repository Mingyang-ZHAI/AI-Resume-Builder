
from django import forms
from .models import Resume, Experience, Education

class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['name', 'country', 'city', 'phone', 'email', 'skills']

    # 为 country 和 city 添加属性支持动态联想
    country = forms.CharField(
        widget=forms.TextInput(attrs={'id': 'country-input', 'placeholder': 'Start typing a country...'}),
        required=True
    )
    city = forms.CharField(
        widget=forms.TextInput(attrs={'id': 'city-input', 'placeholder': 'Start typing a city...'}),
        required=True
    )


class ExperienceForm(forms.ModelForm):
    bullet_point = forms.CharField(
        label="Bullet Point", required=False, widget=forms.TextInput(attrs={'placeholder': 'Add a bullet point'})
    )  # Temporary field for a single bullet point

    class Meta:
        model = Experience
        fields = [
            'start_year',
            'start_month',
            'end_year',
            'end_month',
            'institution_name',
            'position',
            'department_and_role',
            'content',
        ]



class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = [
            'start_year', 'start_month', 'end_year', 'end_month',
            'school_name', 'major', 'gpa', 'content',
        ]


