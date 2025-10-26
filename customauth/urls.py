from django.urls import path
from .views import UserDetailsView


urlpatterns = [
    path('api/me',UserDetailsView.as_view(),name='user-details'),
]
