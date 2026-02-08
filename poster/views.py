from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import status
from allauth.socialaccount.models import SocialAccount
from .models import SchedulePost,LinkedAccounts
from .searialisers import  SocialAccountSerializer
from rest_framework.permissions import IsAuthenticated
from linkedinposter.serialisers import SchedulePostSerializer
# Create your views here.


        

class ConnectedAccountList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request,*args,**kwargs):
        
        linkedAccounts = LinkedAccounts.objects.filter(user=request.user).select_related('social_account')
        app_user = [account.social_account for account in linkedAccounts]
        social_accounts = SocialAccountSerializer(app_user,many=True)
        return Response(data=social_accounts.data,status=status.HTTP_200_OK)

class ScheduledPostsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request,*args,**kwargs):
        scheduled_posts = SchedulePost.objects.filter(author=request.user)
        serializer = SchedulePostSerializer(scheduled_posts,many=True)
        return Response(data=serializer.data,status=status.HTTP_200_OK)


        
        

        

    
        
        
        