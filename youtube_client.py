import os
import logging
import json
import asyncio
from typing import Optional, Dict, Any, Tuple
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
import aiofiles
import aiohttp

logger = logging.getLogger(__name__)

class YouTubeClient:
    def __init__(self):
        self.client_id = os.getenv('GOOGLE_CLIENT_ID')
        self.client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        self.scopes = ['https://www.googleapis.com/auth/youtube.upload']
        self.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
        
        if not self.client_id or not self.client_secret:
            raise ValueError("Google OAuth credentials are required")
    
    def get_oauth_url(self) -> str:
        """Generate OAuth authorization URL"""
        try:
            client_config = {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            }
            
            flow = Flow.from_client_config(
                client_config,
                scopes=self.scopes,
                redirect_uri=self.redirect_uri
            )
            
            auth_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'
            )
            
            return auth_url
            
        except Exception as e:
            logger.error(f"Failed to generate OAuth URL: {e}")
            raise
    
    async def exchange_code_for_token(self, auth_code: str) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for access token"""
        try:
            client_config = {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            }
            
            flow = Flow.from_client_config(
                client_config,
                scopes=self.scopes,
                redirect_uri=self.redirect_uri
            )
            
            # Exchange code for token
            flow.fetch_token(code=auth_code)
            credentials = flow.credentials
            
            token_data = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            }
            
            return token_data
            
        except Exception as e:
            logger.error(f"Failed to exchange code for token: {e}")
            return None
    
    def create_credentials_from_token(self, token_data: Dict[str, Any]) -> Credentials:
        """Create Google credentials from token data"""
        return Credentials(
            token=token_data['token'],
            refresh_token=token_data.get('refresh_token'),
            token_uri=token_data['token_uri'],
            client_id=token_data['client_id'],
            client_secret=token_data['client_secret'],
            scopes=token_data['scopes']
        )
    
    async def refresh_token_if_needed(self, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """Refresh token if needed and return updated token data"""
        try:
            credentials = self.create_credentials_from_token(token_data)
            
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                
                # Update token data
                token_data.update({
                    'token': credentials.token,
                    'refresh_token': credentials.refresh_token
                })
            
            return token_data
            
        except Exception as e:
            logger.error(f"Failed to refresh token: {e}")
            raise
    
    async def upload_video(self, file_path: str, token_data: Dict[str, Any], 
                          title: str, description: str = "", 
                          tags: list = None, privacy_status: str = "private") -> Optional[str]:
        """Upload video to YouTube"""
        try:
            # Refresh token if needed
            token_data = await self.refresh_token_if_needed(token_data)
            credentials = self.create_credentials_from_token(token_data)
            
            # Build YouTube service
            youtube = build('youtube', 'v3', credentials=credentials)
            
            # Prepare video metadata
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags or [],
                    'categoryId': '22'  # People & Blogs category
                },
                'status': {
                    'privacyStatus': privacy_status,
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # Create media upload object
            media = MediaFileUpload(
                file_path,
                chunksize=-1,
                resumable=True,
                mimetype='video/*'
            )
            
            # Execute upload
            insert_request = youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None
            error = None
            retry = 0
            
            while response is None:
                try:
                    status, response = insert_request.next_chunk()
                    if status:
                        logger.info(f"Upload progress: {int(status.progress() * 100)}%")
                except HttpError as e:
                    if e.resp.status in [500, 502, 503, 504]:
                        error = f"A retriable HTTP error {e.resp.status} occurred:\n{e.content}"
                        retry += 1
                        if retry > 5:
                            logger.error("Maximum retries exceeded")
                            return None
                        await asyncio.sleep(2 ** retry)
                    else:
                        logger.error(f"A non-retriable HTTP error occurred: {e}")
                        return None
                except Exception as e:
                    logger.error(f"An error occurred during upload: {e}")
                    return None
            
            if response:
                video_id = response.get('id')
                logger.info(f"Video uploaded successfully. Video ID: {video_id}")
                return video_id
            else:
                logger.error("Upload failed - no response received")
                return None
                
        except Exception as e:
            logger.error(f"Failed to upload video: {e}")
            return None
    
    async def get_video_info(self, video_id: str, token_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get video information from YouTube"""
        try:
            credentials = self.create_credentials_from_token(token_data)
            youtube = build('youtube', 'v3', credentials=credentials)
            
            request = youtube.videos().list(
                part="snippet,status,statistics",
                id=video_id
            )
            
            response = request.execute()
            
            if response['items']:
                return response['items'][0]
            else:
                return None
                
        except Exception as e:
            logger.error(f"Failed to get video info: {e}")
            return None
    
    async def delete_video(self, video_id: str, token_data: Dict[str, Any]) -> bool:
        """Delete video from YouTube"""
        try:
            credentials = self.create_credentials_from_token(token_data)
            youtube = build('youtube', 'v3', credentials=credentials)
            
            request = youtube.videos().delete(id=video_id)
            request.execute()
            
            logger.info(f"Video {video_id} deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete video {video_id}: {e}")
            return False

# Global YouTube client instance
youtube_client = YouTubeClient()
