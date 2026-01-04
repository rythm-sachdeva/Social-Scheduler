from social_scheduler.adapters import AccountAdapter
from allauth.socialaccount.models import SocialToken, SocialAccount
from datetime import timedelta
from django.utils import timezone
from poster.services import PosterABS
from poster.models import SchedulePost
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
        

    
    def _refresh_linkedin_token(self)->SocialAccount:
        """
        Refreshes the token
        """
        try:
            social_token = SocialToken.objects.get(account=self.social_account)
        except SocialToken.DoesNotExist:
            raise LinkedInAPIError("Token does not exist")
        
        if social_token.expires_at < (timezone.now() + timedelta(seconds=60)):
                refresh_token = social_token.token_secret
                if not refresh_token:
                     raise LinkedInAccountNotConnected("LinkedIn Token Not Found")
                social_app = self.social_account.get_provider().get_app(request=None)

    def get_headers(self)->dict:
        """
        Refreshes the token if needed and returns valid API headers.
        """

        valid_token = self._refresh_linkedin_token(social_account=self.social_account)
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
     

class LinkedInUploader:
     def __init__(self,config:LinkedInConfig):
          self.config = config
     
     def upload_media(self,person_urn,media_file)->str:
          """
          Uploads media to LinkedIn and returns the asset URN.
          """
          headers = self.config.get_headers()
          register_url = "https://api.linkedin.com/v2/assets?action=registerUpload"
          register_data = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": f"urn:li:person:{person_urn}",
                "serviceRelationships": [{
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent"
                }]
            }
        }
          response = requests.post(register_url,json=register_data,headers=headers)
          if response.status_code != 200:
               raise LinkedInAPIError(f"Failed to register Upload: {response.text}")
          reg_json = response.json()
          upload_url = reg_json['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
          asset_urn = reg_json['value']['asset']
          cloudinary_url = media_file.url
          try:
               file_response = requests.get(cloudinary_url)
               file_response.raise_for_status()
               fileBinary = file_response.content
          except requests.RequestException as e:
               raise LinkedInAPIError(f"Error Fetching Media from cloudinary: {str(e)}")


          upload_headers = {"Authorization": headers["Authorization"],
                            "Content-Type": "application/octet-stream"}
          upload_response = requests.put(upload_url, data=fileBinary, headers=upload_headers)
          if upload_response.status_code not in [200, 201]:
               raise LinkedInAPIError(f"Error Uploading Binary: {upload_response.text}")
          return asset_urn




  
class LinkedInAdapter(PosterABS):
     def __init__(self):
          pass

     def post(self,post:SchedulePost):
          linked_account = post.social_account
          if linked_account.provider != 'linkedin':
               raise LinkedInAccountNotConnected("The provided social account is not a LinkedIn account.")
          social_account = SocialAccount.objects.get(id=linked_account.id)
          linked_in_config = LinkedInConfig(social_account)
          asset_urn = None
          person_urn = social_account.uid

          if post.media_file:
               uploader = LinkedInUploader(linked_in_config)
               asset_urn = uploader.upload_media(person_urn=person_urn,media_file=post.media_file)
          
          post_body = {
            "author": f"urn:li:person:{person_urn}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": post.text
                    },
                    "shareMediaCategory": "NONE" if not asset_urn else "IMAGE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
          if asset_urn:
               post_body["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                    {
                         "status": "READY",
                         "description": {"text": "Image Description"},
                         "media": asset_urn,
                         "title": {"text": "Image Title"} 
                    }
               ]
               
          url = "https://api.linkedin.com/v2/ugcPosts"
          headers = linked_in_config.get_headers()
          
          response = requests.post(url, headers=headers, json=post_body)
          
          if response.status_code not in [200, 201]:
               raise LinkedInAPIError(f"Failed to create post: {response.text}")
          
          return response.json()
               

          

          