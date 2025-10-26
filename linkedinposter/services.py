from social_scheduler.adapters import AccountAdapter
from allauth.socialaccount.models import SocialToken, SocialAccount
from datetime import timedelta
from django.utils import timezone


class LinkedInAccountNotConnected(Exception):
    """Raised when a user has no LinkedIn social account connected."""
    pass

class LinkedInAPIError(Exception):
    """Raised for any failures when communicating with the LinkedIn API."""
    pass


class LinkedINPoster(AccountAdapter):


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