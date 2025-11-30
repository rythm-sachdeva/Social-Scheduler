from django.urls import path
from .views import LinkedAccountConnectView


urlpatterns = [
    path('connect/', LinkedAccountConnectView.as_view(), name='linkedin_connect'),
]