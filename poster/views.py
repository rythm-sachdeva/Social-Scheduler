from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from allauth.socialaccount.models import SocialAccount
from .models import SchedulePost
from .searialisers import SchedulePostSerializer, SocialAccountSerializer
from rest_framework.permissions import IsAuthenticated
# Create your views here.


class SchedulePostView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        post = SchedulePost.objects.filter(author=request.user).filter()
