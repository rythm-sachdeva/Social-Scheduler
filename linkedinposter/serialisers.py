from rest_framework import serializers
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from poster.models import SchedulePost,LinkedAccounts


class SchedulePostSerializer(serializers.ModelSerializer):

    author = serializers.HiddenField(user=serializers.CurrentUserDefault())

    social_account_provider = serializers.CharField(source='social_account.provider', read_only=True)
    author_username = serializers.CharField(source='author.username')
    social_account = serializers.PrimaryKeyRelatedField(queryset=SocialAccount.objects.none())
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
        read_only_fields = ['id', 'author_username', 'status', 'created_at']

    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        request = self.context.get('request')

        if request and  hasattr(request,'user'):
            social_account = LinkedAccounts.objects.filter(user=request.user).values_list('social_account_id',flat=True)
            qs = SocialAccount.objects.filter(id__in=social_account.social_account)
            initial_data = getattr(self,'initial_data',{})
            sent_provider = initial_data.get('provider')
            if sent_provider:
                qs = qs.filter(provider=sent_provider)
            
            self.fields['social_account'].queryset = qs



    
    def get_media_url(self,obj):
        if obj.media_file:
            return obj.media_file.url
        else:
            return None