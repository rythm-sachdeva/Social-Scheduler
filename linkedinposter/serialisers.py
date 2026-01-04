from rest_framework import serializers
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from poster.models import SchedulePost,LinkedAccounts,Status


class SchedulePostSerializer(serializers.ModelSerializer):

    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    social_account_provider = serializers.CharField(source='social_account.provider', read_only=True)
    author_username = serializers.CharField(source='author.username')
    media_file = serializers.FileField(required=False)
    media_url = serializers.SerializerMethodField()
    
    class Meta:
        model = SchedulePost
        fields =[
            'id', 
            'author_username', 
            'author',
            'social_account',
            'social_account_provider',
            'content', 
            'media_file', 
            'status', 
            'publish_at', 
            'created_at',
        ]
        read_only_fields = ['id', 'author_username', 'status', 'created_at','social_accunt']

    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        request = self.context.get('request')

        if request and  hasattr(request,'user'):
            LinkedAccounts = LinkedAccounts.objects.select_related('social_account').filter(user=request.user,social_account__provider='linkedin')
            self.fields['social_account'] = LinkedAccounts.social_account
        self.fields['status']= Status.SCHEDULED
                   



    
    def get_media_url(self,obj):
        if obj.media_file:
            return obj.media_file.url
        else:
            return None