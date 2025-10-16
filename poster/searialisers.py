from rest_framework import serializers
from .models import SchedulePost
from allauth.socialaccount.models import SocialAccount

class SchedulePostSerializer(serializers.ModelSerializer):

    author_username = serializers.CharField(source='author.username', read_only=True)
    social_account_name = serializers.CharField(source='social_account.provider', read_only=True)
    social_account = serializers.PrimaryKeyRelatedField(queryset=SocialAccount.objects.all())
    
    class Meta:
        model = SchedulePost
        fields =[
            'id', 
            'author_username', 
            'social_account',
            'social_account_provider',
            'content', 
            'media_file', 
            'status', 
            'publish_at', 
            'created_at',
        ]
        read_only_fields = ['id', 'author_username', 'status', 'created_at'] 


class SocialAccountSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username",read_only=True)
    class Meta:
        model = SocialAccount
        fields = ['id', 'provider', 'uid', 'username']
        read_only_fields = ['id', 'provider', 'uid', 'username']


