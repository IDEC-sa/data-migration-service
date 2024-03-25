from django.urls import path 
from .views import SalesManSignUpFormView, UserLoginView, UserLogoutView, SuccessView, DirectorSignUpView, SalesDirectorSignUpView
from django.contrib.auth import views
urlpatterns = [    
    path('sales-man/register', SalesManSignUpFormView.as_view(), name = 'sale-man-register'),
    path('director/register', DirectorSignUpView.as_view(), name='director-register'), 
    path('sales-director/register', SalesDirectorSignUpView.as_view(), name='sales-director-register'), 
    path('success/', SuccessView.as_view(), name = "success"),
    path("login/", UserLoginView.as_view(), name = "login"),
    path("logout/", UserLogoutView.as_view(), name="logout")
]
