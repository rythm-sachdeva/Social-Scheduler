from django.shortcuts import render
from allauth.socialaccount.providers.openid_connect.views import OpenIDConnectOAuth2Adapter
from allauth.socialaccount.providers.oauth2.views import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework.views import APIView
from django.http import HttpResponse
from allauth.socialaccount.helpers import complete_social_login
from django.shortcuts import redirect
# Create your views here.

class LinkedINOidcAdapter(OpenIDConnectOAuth2Adapter):
    provider_id = "linkedin"


class linkedinCallbackView(APIView):
    provider_id = "linkedin"
    mobile_app_scheme = "exp://he5wsyg-anonymous-8081.exp.direct/--/home"

    def get_callback_url(self):
        return "https://x17hwf7f-8000.inc1.devtunnels.ms/linkedin/callback"
    
    def get_adapter(self):
        adapter = OpenIDConnectOAuth2Adapter()
        adapter.provider_id = self.provider_id
        return adapter

        

    def get(self,request,*args, **kwargs):
        
            code = request.GET.get('code')
            state = request.GET.get('state')
            error = request.GET.get('error')

            if error:
                return HttpResponse(f"Error during LinkedIn authentication. Message : {error}")
            
            if not code or not state:
                return HttpResponse("Missing code or state parameter.")
            try:
                adapter = self.get_adapter()
                provider = adapter.get_provider()
                app = provider.get_app(request)
                client = OAuth2Client(self.request, app.client_id, app.secret, adapter.access_token_method, adapter.access_token_url,callback_url=self.get_callback_url())
                token = client.get_access_token(code)
                social_login = adapter.complete_login(request, app, token, response=token.token)
                complete_social_login(request, social_login)
                data = social_login.account.extra_data
                query_params = {
                    'fname': data.get('given_name', ''),
                    'lname': data.get('family_name', ''),
                    'pic': data.get('picture', ''),
                    'email': data.get('email', '')
                }
                params_str = "&".join(f"{key}={value}" for key, value in query_params.items())
                redirect_url = f"{self.mobile_app_scheme}?{params_str}"
                return redirect(redirect_url)
        
            except Exception as e:
                return HttpResponse(f"An error occurred: {str(e)}")
        
    

