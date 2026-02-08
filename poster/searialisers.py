from rest_framework import serializers
from .models import SchedulePost
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model



class SocialAccountSerializer(serializers.ModelSerializer):
    firstname = serializers.CharField(source='user.first_name', read_only=True)
    lastname = serializers.CharField(source='user.last_name', read_only=True)
    class Meta:
        model = SocialAccount
        fields = ['id', 'provider', 'uid', 'firstname', 'lastname']
        read_only_fields = ['id', 'provider', 'uid', 'username'] 







