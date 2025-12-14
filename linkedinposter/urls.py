from django.urls import path
from .views import linkedinCallbackView,LinkedInLogin


urlpatterns = [
    path('callback/', linkedinCallbackView.as_view(), name='linkedin_connect'),
    path('login/', LinkedInLogin.as_view(), name='linkedin_login'),
]