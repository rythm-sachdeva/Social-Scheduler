from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .serialiser import UserDetails
from rest_framework.permissions import IsAuthenticated


# Create your views here.


class UserDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request,*args, **kwargs):
        print(request)
        user = request.user
        user_data =UserDetails(user)
        return Response(data=user_data.data,status=status.HTTP_200_OK)
        


