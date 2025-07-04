import html
from datetime import datetime
from typing import Dict, Any, List, Optional

class HTMLFormatter:
    """Utility class for formatting Telegram messages with HTML"""
    
    @staticmethod
    def escape(text: str) -> str:
        """Escape HTML special characters"""
        return html.escape(str(text))
    
    @staticmethod
    def bold(text: str) -> str:
        """Make text bold"""
        return f"<b>{HTMLFormatter.escape(text)}</b>"
    
    @staticmethod
    def italic(text: str) -> str:
        """Make text italic"""
        return f"<i>{HTMLFormatter.escape(text)}</i>"
    
    @staticmethod
    def code(text: str) -> str:
        """Format text as code"""
        return f"<code>{HTMLFormatter.escape(text)}</code>"
    
    @staticmethod
    def pre(text: str) -> str:
        """Format text as preformatted"""
        return f"<pre>{HTMLFormatter.escape(text)}</pre>"
    
    @staticmethod
    def link(text: str, url: str) -> str:
        """Create a hyperlink"""
        return f'<a href="{HTMLFormatter.escape(url)}">{HTMLFormatter.escape(text)}</a>'
    
    @staticmethod
    def underline(text: str) -> str:
        """Make text underlined"""
        return f"<u>{HTMLFormatter.escape(text)}</u>"
    
    @staticmethod
    def strikethrough(text: str) -> str:
        """Make text strikethrough"""
        return f"<s>{HTMLFormatter.escape(text)}</s>"
    
    @staticmethod
    def format_welcome_message(user_name: str) -> str:
        """Format welcome message"""
        return f"""
🎬 {HTMLFormatter.bold('Welcome to YouTube Uploader Bot!')} 🎬

Hello {HTMLFormatter.bold(user_name)}! 👋

This bot helps you upload videos directly to YouTube. Here's what you can do:

📋 {HTMLFormatter.bold('Available Commands:')}
• /start - Show this welcome message
• /auth - Authenticate with Google/YouTube
• /upload - Upload a video to YouTube
• /history - View your upload history
• /stats - View bot statistics
• /help - Get detailed help

🔐 {HTMLFormatter.bold('Getting Started:')}
1. First, use /auth to connect your YouTube account
2. Send a video file to upload it
3. Follow the prompts to add title and description

{HTMLFormatter.italic('Note: You need to authenticate with Google first before uploading videos.')}

Need help? Use /help for detailed instructions! 🚀
        """.strip()
    
    @staticmethod
    def format_auth_message(auth_url: str) -> str:
        """Format authentication message"""
        return f"""
🔐 {HTMLFormatter.bold('YouTube Authentication Required')}

To upload videos to YouTube, you need to authenticate with Google.

{HTMLFormatter.bold('Steps to authenticate:')}
1. Click the link below to open Google OAuth page
2. Sign in with your Google account
3. Grant permissions to the bot
4. Copy the authorization code
5. Send the code back to this bot

{HTMLFormatter.link('🔗 Click here to authenticate', auth_url)}

{HTMLFormatter.italic('Note: The authorization code will be a long string of characters. Just copy and paste it here.')}

⚠️ {HTMLFormatter.bold('Important:')} Make sure you're signed in to the correct Google account that has access to the YouTube channel you want to upload to.
        """.strip()
    
    @staticmethod
    def format_auth_success_message(user_name: str) -> str:
        """Format authentication success message"""
        return f"""
✅ {HTMLFormatter.bold('Authentication Successful!')}

Great job, {HTMLFormatter.bold(user_name)}! Your YouTube account is now connected.

🎬 {HTMLFormatter.bold('You can now:')}
• Send video files to upload them to YouTube
• Use /upload command to start the upload process
• View your upload history with /history

{HTMLFormatter.italic('Ready to upload your first video? Just send me a video file!')} 🚀
        """.strip()
    
    @staticmethod
    def format_upload_prompt() -> str:
        """Format upload prompt message"""
        return f"""
📤 {HTMLFormatter.bold('Video Upload')}

Please send me the video file you want to upload to YouTube.

📋 {HTMLFormatter.bold('Supported formats:')}
• MP4, AVI, MOV, WMV, FLV, MKV
• Maximum file size: 2GB
• Recommended: MP4 format for best compatibility

⏳ {HTMLFormatter.italic('Note: Large files may take some time to upload. Please be patient!')}

Cancel anytime by sending /cancel
        """.strip()
    
    @staticmethod
    def format_video_details_prompt(filename: str, file_size: str) -> str:
        """Format video details prompt"""
        return f"""
🎬 {HTMLFormatter.bold('Video Details')}

📁 File: {HTMLFormatter.code(filename)}
📊 Size: {HTMLFormatter.code(file_size)}

Please provide the following details for your video:

{HTMLFormatter.bold('1. Video Title:')}
Send the title for your video (required)

{HTMLFormatter.italic('After you send the title, I\'ll ask for the description and other details.')}

Cancel anytime by sending /cancel
        """.strip()
    
    @staticmethod
    def format_upload_progress(progress: int, filename: str) -> str:
        """Format upload progress message"""
        progress_bar = "█" * (progress // 5) + "░" * (20 - progress // 5)
        return f"""
⏳ {HTMLFormatter.bold('Uploading to YouTube...')}

📁 {HTMLFormatter.code(filename)}
📊 Progress: {HTMLFormatter.code(f'{progress}%')}
{HTMLFormatter.code(f'[{progress_bar}]')}

{HTMLFormatter.italic('Please wait while your video is being uploaded...')}
        """.strip()
    
    @staticmethod
    def format_upload_success(video_data: Dict[str, Any]) -> str:
        """Format upload success message"""
        youtube_url = f"https://www.youtube.com/watch?v={video_data['video_id']}"
        return f"""
🎉 {HTMLFormatter.bold('Upload Successful!')}

Your video has been uploaded to YouTube successfully!

🎬 {HTMLFormatter.bold('Video Details:')}
📝 Title: {HTMLFormatter.bold(video_data.get('title', 'N/A'))}
🆔 Video ID: {HTMLFormatter.code(video_data['video_id'])}
🔗 URL: {HTMLFormatter.link('Watch on YouTube', youtube_url)}
📅 Uploaded: {HTMLFormatter.code(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}

{HTMLFormatter.italic('Your video is now live on YouTube! 🚀')}

Want to upload another video? Just send me another video file!
        """.strip()
    
    @staticmethod
    def format_upload_error(error_message: str) -> str:
        """Format upload error message"""
        return f"""
❌ {HTMLFormatter.bold('Upload Failed')}

Sorry, there was an error uploading your video:

{HTMLFormatter.code(error_message)}

{HTMLFormatter.bold('What you can do:')}
• Try uploading again
• Check if your file format is supported
• Make sure your file size is under 2GB
• Verify your YouTube authentication is still valid

Need help? Use /help for more information.
        """.strip()
    
    @staticmethod
    def format_history(uploads: List[Dict[str, Any]]) -> str:
        """Format upload history"""
        if not uploads:
            return f"""
📋 {HTMLFormatter.bold('Upload History')}

{HTMLFormatter.italic('No uploads found. Upload your first video to see it here!')}

Use /upload to start uploading videos.
            """.strip()
        
        history_text = f"📋 {HTMLFormatter.bold('Your Upload History')}\n\n"
        
        for i, upload in enumerate(uploads[:10], 1):
            upload_date = upload.get('upload_date', datetime.now())
            if isinstance(upload_date, str):
                date_str = upload_date
            else:
                date_str = upload_date.strftime('%Y-%m-%d %H:%M')
            
            youtube_url = upload.get('youtube_url', f"https://www.youtube.com/watch?v={upload.get('video_id', '')}")
            
            history_text += f"""
{HTMLFormatter.bold(f'{i}. {upload.get("title", "Untitled")}')}
🆔 ID: {HTMLFormatter.code(upload.get('video_id', 'N/A'))}
📅 Date: {HTMLFormatter.code(date_str)}
🔗 {HTMLFormatter.link('Watch', youtube_url)}
            """.strip() + "\n\n"
        
        if len(uploads) > 10:
            history_text += f"{HTMLFormatter.italic('Showing latest 10 uploads...')}\n"
        
        return history_text.strip()
    
    @staticmethod
    def format_stats(total_users: int, total_uploads: int, user_uploads: int) -> str:
        """Format bot statistics"""
        return f"""
📊 {HTMLFormatter.bold('Bot Statistics')}

👥 Total Users: {HTMLFormatter.code(str(total_users))}
📤 Total Uploads: {HTMLFormatter.code(str(total_uploads))}
🎬 Your Uploads: {HTMLFormatter.code(str(user_uploads))}

{HTMLFormatter.italic('Thank you for using YouTube Uploader Bot!')} 🚀
        """.strip()
    
    @staticmethod
    def format_help_message() -> str:
        """Format detailed help message"""
        return f"""
❓ {HTMLFormatter.bold('YouTube Uploader Bot Help')}

{HTMLFormatter.bold('🔐 Authentication:')}
• Use /auth to connect your YouTube account
• Follow the OAuth flow to grant permissions
• You only need to do this once

{HTMLFormatter.bold('📤 Uploading Videos:')}
• Send a video file directly to the bot
• Supported formats: MP4, AVI, MOV, WMV, FLV, MKV
• Maximum file size: 2GB
• Add title, description, and tags when prompted

{HTMLFormatter.bold('📋 Commands:')}
• /start - Welcome message and overview
• /auth - Authenticate with YouTube
• /upload - Start upload process
• /history - View your upload history
• /stats - View bot statistics
• /help - Show this help message
• /cancel - Cancel current operation

{HTMLFormatter.bold('🔧 Troubleshooting:')}
• If upload fails, try re-authenticating with /auth
• Check file format and size requirements
• Ensure stable internet connection
• Contact support if issues persist

{HTMLFormatter.bold('🔒 Privacy & Security:')}
• Your OAuth tokens are securely stored
• Videos are uploaded to your YouTube channel
• Bot doesn't store video files permanently
• You can revoke access anytime from Google settings

{HTMLFormatter.italic('Need more help? Contact the bot administrator.')}
        """.strip()
    
    @staticmethod
    def format_error_message(error: str) -> str:
        """Format generic error message"""
        return f"""
❌ {HTMLFormatter.bold('Error')}

{HTMLFormatter.code(error)}

{HTMLFormatter.italic('Please try again or contact support if the issue persists.')}
        """.strip()
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
