from django import forms

from .models import User


class LoginForm(forms.Form):
    username = forms.CharField(max_length=32, label="Username")
    password = forms.CharField(widget=forms.PasswordInput, max_length=64, label="Password")


class RegisterForm(forms.ModelForm):
    username = forms.CharField(max_length=32, label="Username")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data


class JobForm(forms.Form):
    job_title = forms.CharField(label='Job Title', max_length=100,
                                widget=forms.TextInput(attrs={'placeholder': 'Enter Job Title'}))
    description = forms.CharField(label='Description',
                                  widget=forms.Textarea(attrs={'placeholder': 'Enter Job Description'}))
