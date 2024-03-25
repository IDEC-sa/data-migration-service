from typing import Any
from django import forms  
from django.contrib.auth.forms import UserCreationForm  
from django.db import transaction
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth.forms import AuthenticationForm, UsernameField


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 
                                                     'placeholder':'Email address'})
        self.fields['password'].widget.attrs.update({'class':'form-control', 
                                                     'placeholder':'password'})

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=100, help_text="please enter your organization email", required=True)
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

class SalesManSignUpForm(SignUpForm):
    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.sysRole = "sman"
        user = super().save(commit=True)
        return user
   
class DirectorSignUpForm(SignUpForm):
    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.sysRole = "dir"
        user = super().save(commit=True)
        return user
   
class SalesDirectorSignUpForm(SignUpForm):
    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.sysRole = "sdir"
        user = super().save(commit=True)
        return user
