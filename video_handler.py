import os
import logging
import asyncio
import aiofiles
import tempfile
from datetime import datetime
from typing import Dict, Any, Optional
from pyrogram.types import Message
from pyrogram.errors import FloodWait

from database import db
from youtube_client import youtube_client
from html_formatter import HTMLFormatter

logger = logging.getLogger(__name__)

class VideoHandler:
    def __init__(self):
        self.max_file_size = int(os.getenv('MAX_FILE_SIZE', 2147483648))  # 2GB default
        self.supported_formats = {
            'video/mp4', 'video/avi', 'video/quicktime', 'video/x-msvideo',
            'video/x-flv', 'video/x-matroska', 'video/webm', 'application/octet-stream'
        }
        self.temp_dir = tempfile.gettempdir()
    
    async def process_video(self, message: Message, user_states: Dict[int, Dict[str, Any]]):
        """Process incoming video file"""
        try:
            user_id = message.from_user.id
            
            # Get file info
            if message.video:
                file_obj = message.video
                file_name = file_obj.file_name or f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
                file_size = file_obj.file_size
                duration = file_obj.duration
                mime_type = file_obj.mime_type
            elif message.document:
                file_obj = message.document
                file_name = file_obj.file_name or f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                file_size = file_obj.file_size
                duration = None
                mime_type = file_obj.mime_type
            else:
                await message.reply_text("❌ Please send a valid video file.")
                return
            
            # Validate file size
            if file_size > self.max_file_size:
                size_mb = file_size / (1024 * 1024)
                max_size_mb = self.max_file_size / (1024 * 1024)
                await message.reply_text(
                    f"❌ File too large ({size_mb:.1f}MB). Maximum allowed size is {max_size_mb:.1f}MB.",
                    parse_mode="HTML"
                )
                return
            
            # Validate file format
            if mime_type and mime_type not in self.supported_formats:
                await message.reply_text(
                    "❌ Unsupported file format. Please send MP4, AVI, MOV, WMV, FLV, or MKV files.",
                    parse_mode="HTML"
                )
                return
            
            # Show file details and ask for title
            file_size_str = HTMLFormatter.format_file_size(file_size)
            details_msg = HTMLFormatter.format_video_details_prompt(file_name, file_size_str)
            
            # Store video info in user state
            user_states[user_id] = {
                'state': 'waiting_title',
                'file_id': file_obj.file_id,
                'file_name': file_name,
                'file_size': file_size,
                'duration': duration,
                'mime_type': mime_type,
                'timestamp': datetime.now()
            }
            
            await message.reply_text(details_msg, parse_mode="HTML")
            
        except Exception as e:
            logger.error(f"Error processing video: {e}")
            await message.reply_text("❌ Failed to process video. Please try again.")
    
    async def upload_video_to_youtube(self, message: Message, user_state: Dict[str, Any]):
        """Upload video to YouTube"""
        try:
            user_id = message.from_user.id
            
            # Get OAuth token
            token_data = await db.get_oauth_token(user_id)
            if not token_data:
                await message.reply_text("❌ Authentication required. Please use /auth command.")
                return
            
            # Send initial upload message
            progress_msg = await message.reply_text(
                "⏳ <b>Preparing upload...</b>\n\nDownloading video file...",
                parse_mode="HTML"
            )
            
            # Download video file
            file_path = await self._download_video(message, user_state, progress_msg)
            if not file_path:
                await progress_msg.edit_text("❌ Failed to download video file.")
                return
            
            try:
                # Update progress
                await progress_msg.edit_text(
                    HTMLFormatter.format_upload_progress(10, user_state['file_name']),
                    parse_mode="HTML"
                )
                
                # Prepare video metadata
                title = user_state.get('title', 'Untitled Video')
                description = user_state.get('description', '')
                
                # Add bot signature to description
                if description:
                    description += "\n\n"
                description += "📤 Uploaded via YouTube Uploader Bot"
                
                # Update progress
                await progress_msg.edit_text(
                    HTMLFormatter.format_upload_progress(20, user_state['file_name']),
                    parse_mode="HTML"
                )
                
                # Upload to YouTube
                video_id = await self._upload_with_progress(
                    file_path, token_data, title, description, progress_msg, user_state['file_name']
                )
                
                if video_id:
                    # Save upload record
                    video_data = {
                        'video_id': video_id,
                        'title': title,
                        'description': description,
                        'file_name': user_state['file_name'],
                        'file_size': user_state['file_size'],
                        'duration': user_state.get('duration')
                    }
                    
                    await db.add_upload_record(user_id, video_data)
                    
                    # Send success message
                    success_msg = HTMLFormatter.format_upload_success(video_data)
                    await progress_msg.edit_text(success_msg, parse_mode="HTML", disable_web_page_preview=True)
                    
                else:
                    await progress_msg.edit_text(
                        HTMLFormatter.format_upload_error("Upload failed. Please try again."),
                        parse_mode="HTML"
                    )
                
            finally:
                # Clean up temporary file
                await self._cleanup_file(file_path)
                
        except Exception as e:
            logger.error(f"Error uploading video: {e}")
            await message.reply_text(
                HTMLFormatter.format_upload_error(str(e)),
                parse_mode="HTML"
            )
    
    async def _download_video(self, message: Message, user_state: Dict[str, Any], 
                             progress_msg: Message) -> Optional[str]:
        """Download video file from Telegram"""
        try:
            file_id = user_state['file_id']
            file_name = user_state['file_name']
            
            # Create temporary file path
            temp_file_path = os.path.join(self.temp_dir, f"temp_{file_id}_{file_name}")
            
            # Download file
            await message._client.download_media(file_id, file_name=temp_file_path)
            
            # Verify file exists and has content
            if os.path.exists(temp_file_path) and os.path.getsize(temp_file_path) > 0:
                logger.info(f"Video downloaded successfully: {temp_file_path}")
                return temp_file_path
            else:
                logger.error("Downloaded file is empty or doesn't exist")
                return None
                
        except Exception as e:
            logger.error(f"Error downloading video: {e}")
            return None
    
    async def _upload_with_progress(self, file_path: str, token_data: Dict[str, Any], 
                                   title: str, description: str, progress_msg: Message, 
                                   file_name: str) -> Optional[str]:
        """Upload video with progress updates"""
        try:
            # Update progress to 30%
            await progress_msg.edit_text(
                HTMLFormatter.format_upload_progress(30, file_name),
                parse_mode="HTML"
            )
            
            # Start upload in background and update progress
            upload_task = asyncio.create_task(
                youtube_client.upload_video(
                    file_path=file_path,
                    token_data=token_data,
                    title=title,
                    description=description,
                    privacy_status="private"  # Default to private for safety
                )
            )
            
            # Simulate progress updates while upload is happening
            progress_values = [40, 50, 60, 70, 80, 90]
            for progress in progress_values:
                if upload_task.done():
                    break
                
                try:
                    await progress_msg.edit_text(
                        HTMLFormatter.format_upload_progress(progress, file_name),
                        parse_mode="HTML"
                    )
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                except Exception:
                    pass  # Ignore edit errors
                
                await asyncio.sleep(2)  # Wait 2 seconds between updates
            
            # Wait for upload to complete
            video_id = await upload_task
            
            if video_id:
                # Final progress update
                await progress_msg.edit_text(
                    HTMLFormatter.format_upload_progress(100, file_name),
                    parse_mode="HTML"
                )
                await asyncio.sleep(1)  # Brief pause before success message
            
            return video_id
            
        except Exception as e:
            logger.error(f"Error during upload with progress: {e}")
            return None
    
    async def _cleanup_file(self, file_path: str):
        """Clean up temporary file"""
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up temporary file: {file_path}")
        except Exception as e:
            logger.error(f"Error cleaning up file {file_path}: {e}")
    
    def _get_video_format_from_filename(self, filename: str) -> str:
        """Get video format from filename"""
        ext = os.path.splitext(filename)[1].lower()
        format_map = {
            '.mp4': 'MP4',
            '.avi': 'AVI',
            '.mov': 'MOV',
            '.wmv': 'WMV',
            '.flv': 'FLV',
            '.mkv': 'MKV',
            '.webm': 'WebM'
        }
        return format_map.get(ext, 'Unknown')
    
    def _is_video_file(self, filename: str) -> bool:
        """Check if file is a video based on extension"""
        video_extensions = {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm', '.m4v', '.3gp'}
        ext = os.path.splitext(filename)[1].lower()
        return ext in video_extensions
    
    async def get_video_thumbnail(self, file_path: str) -> Optional[str]:
        """Extract thumbnail from video (placeholder for future implementation)"""
        # This could be implemented using ffmpeg or similar
        # For now, return None
        return None
    
    async def get_video_metadata(self, file_path: str) -> Dict[str, Any]:
        """Get video metadata (placeholder for future implementation)"""
        # This could be implemented using ffprobe or similar
        # For now, return basic info
        try:
            file_size = os.path.getsize(file_path)
            return {
                'file_size': file_size,
                'format': self._get_video_format_from_filename(file_path)
            }
        except Exception as e:
            logger.error(f"Error getting video metadata: {e}")
            return {}
    
    def _validate_video_title(self, title: str) -> bool:
        """Validate video title"""
        if not title or not title.strip():
            return False
        if len(title) > 100:
            return False
        return True
    
    def _validate_video_description(self, description: str) -> bool:
        """Validate video description"""
        if len(description) > 5000:  # YouTube limit
            return False
        return True
