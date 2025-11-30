from django.urls import path
from .views import linkedinCallbackView


urlpatterns = [
    path('callback/', linkedinCallbackView.as_view(), name='linkedin_connect'),
]