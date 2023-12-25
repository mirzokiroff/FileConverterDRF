from django.urls import path
from .views import UserProfileRetrieveView, RegisterView, EmailSignUpView, LoginView

urlpatterns = [
    path('profile/', UserProfileRetrieveView.as_view(), name='profile'),
    path('register/', RegisterView.as_view(), name='register'),
    path('email-confirm/', EmailSignUpView.as_view(), name='email_confirm'),
    path('login/', LoginView.as_view(), name='login'),
]