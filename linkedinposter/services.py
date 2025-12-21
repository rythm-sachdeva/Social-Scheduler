from social_scheduler.adapters import AccountAdapter
from allauth.socialaccount.models import SocialToken, SocialAccount
from datetime import timedelta
from django.utils import timezone
import requests



class LinkedInAccountNotConnected(Exception):
    """Raised when a user has no LinkedIn social account connected."""
    pass

class LinkedInAPIError(Exception):
    """Raised for any failures when communicating with the LinkedIn API."""
    pass


class LinkedInConfig(AccountAdapter):

    def __init__(self,SocialAccount:SocialAccount):
        self.social_account = SocialAccount
        

    
    def _refresh_linkedin_token(self,social_account:SocialAccount)->SocialAccount:
        """
        Refreshes the token
        """
        try:
            social_token = SocialToken.objects.get(account=social_account)
        except SocialToken.DoesNotExist:
            raise LinkedInAPIError("Token does not exist")
        
        if social_token.expires_at < (timezone.now() + timedelta(seconds=60)):
                refresh_token = social_token.token_secret
                if not refresh_token:
                     raise LinkedInAccountNotConnected("LinkedIn Token Not Found")
                social_app = social_account.get_provider().get_app(request=None)

                


            


    def get_headers(self,social_account:SocialAccount)->dict:
        """
        Refreshes the token if needed and returns valid API headers.
        """

        valid_token = self._refresh_linkedin_token(social_account=social_account)
        return {
            "Authorization": f"Bearer {valid_token.token}",
            "X-Restli-Protocol-Version": "2.0.0",
            "LinkedIn-Version": "202305" 
        }
    
class PostViewLinkedIn(LinkedInConfig):
     """
     Class For Posting on LInkedIn
     """
     def __init__(self, SocialAccount:SocialAccount,PostOptions:dict):
          super().__init__(SocialAccount)
          self.post_options = PostOptions

        def create_post(self):
          """
          Creates a post on LinkedIn
          """
          headers = self.get_headers(self.social_account)
          post_data = {
               "author": f"urn:li:person:{self.post_options['person_urn']}",
               "lifecycleState": "PUBLISHED",
               "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                         "shareCommentary": {
                              "text": self.post_options['text']
                         },
                         "shareMediaCategory": "NONE"
                    }
               },
               "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
               }
          }
          
          return post_data  

    
     
     

