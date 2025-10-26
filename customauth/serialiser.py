from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework import serializers



class CustomRegisterSerialiser(RegisterSerializer):

    def get_cleaned_data(self):
        return super().get_cleaned_data()
    
    def save(self, request):
        user = super().save(request)

        refresh = RefreshToken.for_user(user=user)
        user.refresh = str(refresh)
        user.access = str(refresh.access_token)

        return user

class UserDetails(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id','username','email','first_name','last_name']

    


    
    
