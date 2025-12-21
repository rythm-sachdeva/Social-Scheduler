from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import status
from allauth.socialaccount.models import SocialAccount
from .models import SchedulePost,LinkedAccounts
from .searialisers import SchedulePostSerializer, SocialAccountSerializer
from rest_framework.permissions import IsAuthenticated
# Create your views here.


class SchedulePostView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        post = SchedulePost.objects.filter(author=request.user).filter()
        

class ConnectedAccountList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request,*args,**kwargs):
        
        linkedAccounts = LinkedAccounts.objects.filter(user=request.user).select_related('social_account')
        app_user = [account.social_account for account in linkedAccounts]
        social_accounts = SocialAccountSerializer(app_user,many=True)
        return Response(data=social_accounts.data,status=status.HTTP_200_OK)


        
        

        

    
        
        
        