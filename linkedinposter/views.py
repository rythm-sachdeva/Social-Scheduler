from django.shortcuts import render
from allauth.socialaccount.providers.openid_connect.views import OpenIDConnectOAuth2Adapter
from allauth.socialaccount.providers.oauth2.views import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
# Create your views here.

class LinkedINOidcAdapter(OpenIDConnectOAuth2Adapter):
    provider_id = "linkedin"

class LinkedAccountConnectView(SocialLoginView):
    adapter_class = LinkedINOidcAdapter
    client_class = OAuth2Client

    callback_uri = "exp://he5wsyg-anonymous-8081.exp.direct"



