import requests
import mimetypes
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from allauth.socialaccount.models import SocialToken, SocialAccount

# --- Constants ---
LINKEDIN_API_BASE_URL = "https://api.linkedin.com/v2"

# --- Custom Exceptions for Clear Error Handling ---

class LinkedInAccountNotConnected(Exception):
    """Raised when a user has no LinkedIn social account connected."""
    pass

class LinkedInAPIError(Exception):
    """Raised for any failures when communicating with the LinkedIn API."""
    pass


# --- Internal Helper Functions (prefixed with _) ---

def _refresh_linkedin_token(social_account: SocialAccount) -> SocialToken:
    """
    Checks if a token is expired and refreshes it using the refresh_token if necessary.
    This is a critical function for long-term, automated posting.

    Returns:
        A SocialToken object with a guaranteed-valid access token.

    Raises:
        LinkedInAPIError: If the token cannot be refreshed.
    """
    try:
        social_token = SocialToken.objects.get(account=social_account)
    except SocialToken.DoesNotExist:
        raise LinkedInAPIError(f"No SocialToken found for account {social_account.uid}.")

    if social_token.expires_at < (timezone.now() + timedelta(seconds=60)):
        refresh_token = social_token.token_secret
        if not refresh_token:
            raise LinkedInAPIError("No refresh token found. User must re-authenticate.")
        social_app = social_account.get_provider().get_app(request=None)
        
        response = requests.post(
            "https://www.linkedin.com/oauth/v2/accessToken",
            data={
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'client_id': social_app.client_id,
                'client_secret': social_app.secret,
            }
        )

        if response.status_code != 200:
            raise LinkedInAPIError(f"Failed to refresh token: {response.status_code} - {response.text}")

        data = response.json()
        
        # Update the token in the database with the new values from LinkedIn
        social_token.token = data['access_token']
        social_token.expires_at = timezone.now() + timedelta(seconds=data['expires_in'])
        
        if 'refresh_token' in data:
            social_token.token_secret = data['refresh_token']
        social_token.save()

    return social_token


def _get_linkedin_api_headers(social_account: SocialAccount) -> dict:
    """
    Refreshes the token if needed and returns valid API headers.
    """
    valid_token = _refresh_linkedin_token(social_account)
    return {
        "Authorization": f"Bearer {valid_token.token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "LinkedIn-Version": "202305" # It's good practice to pin to a recent API version
    }


def _upload_media_to_linkedin(social_account: SocialAccount, media_path: str, author_urn: str) -> str:
    """
    Handles the two-step process of uploading media to LinkedIn.

    1. Registers the upload intent to get a temporary upload URL.
    2. Uploads the actual media file to that URL.

    Returns:
        The URN of the uploaded digital media asset (e.g., "urn:li:digitalmediaAsset:C5612AQG...").
    """
    headers = _get_linkedin_api_headers(social_account)
    
    # 1. Register the upload
    register_payload = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"], # Use "feedshare-video" for videos
            "owner": author_urn,
            "serviceRelationships": [{"relationshipType": "OWNER", "identifier": "urn:li:userGeneratedContent"}]
        }
    }
    reg_response = requests.post(f"{LINKEDIN_API_BASE_URL}/assets?action=registerUpload", json=register_payload, headers=headers)
    if reg_response.status_code != 200:
        raise LinkedInAPIError(f"Failed to register media upload: {reg_response.text}")
    
    upload_data = reg_response.json()['value']
    upload_url = upload_data['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
    asset_urn = upload_data['asset']

    # 2. Upload the media file
    with open(media_path, 'rb') as f:
        content_type, _ = mimetypes.guess_type(media_path)
        upload_headers = {'Content-Type': content_type or 'application/octet-stream'}
        upload_response = requests.put(upload_url, data=f, headers=upload_headers)

    if upload_response.status_code not in [200, 201]:
         raise LinkedInAPIError(f"Failed to upload media file: {upload_response.text}")

    return asset_urn


# --- Public-Facing Service Function ---

def post_to_linkedin(social_account: SocialAccount, text: str, media_path: str = None):
    """
    The main service function to create a post on LinkedIn.
    It orchestrates the entire process, including token refresh and media uploads.

    Args:
        social_account: The SocialAccount instance for the target LinkedIn profile.
        text: The text content of the post.
        media_path (optional): The full local path to an image or video file to be attached.

    Returns:
        The JSON response from the LinkedIn API upon successful post creation.

    Raises:
        ValueError: If the provided social_account is not for LinkedIn.
        LinkedInAPIError: For any API-related failures.
    """
    if social_account.provider != 'linkedin_oauth2':
        raise ValueError("This function only supports 'linkedin_oauth2' social accounts.")

    author_urn = f"urn:li:person:{social_account.uid}"
    asset_urn = None

    # Step 1: Upload media if it exists
    if media_path:
        asset_urn = _upload_media_to_linkedin(social_account, media_path, author_urn)
    
    # Step 2: Construct the final post payload
    headers = _get_linkedin_api_headers(social_account)
    post_payload = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }
    
    share_content = post_payload["specificContent"]["com.linkedin.ugc.ShareContent"]
    
    if asset_urn:
        share_content["shareMediaCategory"] = "IMAGE" 
        share_content["media"] = [{"status": "READY", "media": asset_urn}]
    else:
        share_content["shareMediaCategory"] = "NONE"

    # Step 3: Create the post
    response = requests.post(f"{LINKEDIN_API_BASE_URL}/ugcPosts", json=post_payload, headers=headers)

    if response.status_code != 201: # 201 Created is the success code
        raise LinkedInAPIError(f"Failed to create LinkedIn post: {response.status_code} - {response.text}")

    return response.json()
