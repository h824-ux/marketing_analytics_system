from typing import Any
from django import forms 
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Feedback, RequestSupport

class SignupForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['first_name'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': 'Enter your first name:',
        })

        self.fields['last_name'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': 'Enter your last name:',
        })

        self.fields['company_name'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': 'Enter your company name:',
        })
        
        self.fields['email'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': 'Enter your email address:',
        })

        self.fields['password1'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': 'Enter a password:',
        })

        self.fields['password2'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': 'Confirm your password:',
        })

        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your username:',
        })

    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    username = forms.CharField(max_length=150)
    company_name = forms.CharField(max_length=250)
    email = forms.EmailField(max_length=150)
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            self.add_error('password2', "The passwords don't match")

        return cleaned_data
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'company_name', 'email', 'password1', 'password2']


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['feedback']
        widgets = {
            'feedback': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Feedback:',
                'rows': 10,
            }),
        }

class SupportForm(forms.Form):
    class Meta:
        model = RequestSupport
        fields = ['support']
