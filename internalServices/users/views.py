from typing import Any
from django.shortcuts import render
from .forms import SignUpForm, SalesManSignUpForm, UserLoginForm, DirectorSignUpForm, SalesDirectorSignUpForm
from django.http import HttpRequest, HttpResponse
from django.views.generic import TemplateView, CreateView
from django.urls import reverse
from django.contrib.auth.views import LoginView, LogoutView

# Create your views here.


class UserLoginView(LoginView):
    template_name = "login.html"
    authentication_form = UserLoginForm


class UserLogoutView(LogoutView):
    pass

class SignUpForm(CreateView):
    template_name = "signup.html"
    # form_class = SignUpForm
    
    def get_success_url(self) -> str:
        return reverse("success")

    def form_valid(self, form) -> HttpResponse:
        return super().form_valid(form)
    
class SalesManSignUpFormView(SignUpForm):
    form_class = SalesManSignUpForm
    # template_name = "signup.html"
    # form_class = SignUpForm
    
    # def get_success_url(self) -> str:
    #     return reverse("success")

    # def form_valid(self, form) -> HttpResponse:
    #     return super().form_valid(form)

class DirectorSignUpView(SignUpForm):
    form_class = DirectorSignUpForm


class SalesDirectorSignUpView(SignUpForm):
    form_class = SalesDirectorSignUpForm

class SuccessView(TemplateView):
    template_name = "success.html"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().get(request, *args, **kwargs)
