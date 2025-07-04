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
        welcome_text = (
            f"🎬 {HTMLFormatter.bold('Welcome to YouTube Uploader Bot!')} 🎬\n\n"
            f"Hello {HTMLFormatter.bold(user_name)}! 👋\n\n"
            "This bot helps you upload videos directly to YouTube. Here's what you can do:\n\n"
            f"📋 {HTMLFormatter.bold('Available Commands:')}\n"
            "• /start - Show this welcome message\n"
            "• /auth - Authenticate with Google/YouTube\n"
            "• /upload - Upload a video to YouTube\n"
            "• /history - View your upload history\n"
            "• /stats - View bot statistics\n"
            "• /help - Get detailed help\n\n"
            f"🔐 {HTMLFormatter.bold('Getting Started:')}\n"
            "1. First, use /auth to connect your YouTube account\n"
            "2. Send a video file to upload it\n"
            "3. Follow the prompts to add title and description\n\n"
            f"{HTMLFormatter.italic('Note: You need to authenticate with Google first before uploading videos.')}\n\n"
            "Need help? Use /help for detailed instructions! 🚀"
        )
        return welcome_text
    
    @staticmethod
    def format_auth_message(auth_url: str) -> str:
        """Format authentication message"""
        auth_text = (
            f"🔐 {HTMLFormatter.bold('YouTube Authentication Required')}\n\n"
            "To upload videos to YouTube, you need to authenticate with Google.\n\n"
            f"{HTMLFormatter.bold('Steps to authenticate:')}\n"
            "1. Click the link below to open Google OAuth page\n"
            "2. Sign in with your Google account\n"
            "3. Grant permissions to the bot\n"
            "4. Copy the authorization code\n"
            "5. Send the code back to this bot\n\n"
            f"{HTMLFormatter.link('🔗 Click here to authenticate', auth_url)}\n\n"
            f"{HTMLFormatter.italic('Note: The authorization code will be a long string of characters. Just copy and paste it here.')}\n\n"
            f"⚠️ {HTMLFormatter.bold('Important:')} Make sure you're signed in to the correct Google account that has access to the YouTube channel you want to upload to."
        )
        return auth_text
    
    @staticmethod
    def format_auth_success_message(user_name: str) -> str:
        """Format authentication success message"""
        success_text = (
            f"✅ {HTMLFormatter.bold('Authentication Successful!')}\n\n"
            f"Great job, {HTMLFormatter.bold(user_name)}! Your YouTube account is now connected.\n\n"
            f"🎬 {HTMLFormatter.bold('You can now:')}\n"
            "• Send video files to upload them to YouTube\n"
            "• Use /upload command to start the upload process\n"
            "• View your upload history with /history\n\n"
            f"{HTMLFormatter.italic('Ready to upload your first video? Just send me a video file!')} 🚀"
        )
        return success_text
    
    @staticmethod
    def format_upload_prompt() -> str:
        """Format upload prompt message"""
        prompt_text = (
            f"📤 {HTMLFormatter.bold('Video Upload')}\n\n"
            "Please send me the video file you want to upload to YouTube.\n\n"
            f"📋 {HTMLFormatter.bold('Supported formats:')}\n"
            "• MP4, AVI, MOV, WMV, FLV, MKV\n"
            "• Maximum file size: 2GB\n"
            "• Recommended: MP4 format for best compatibility\n\n"
            f"⏳ {HTMLFormatter.italic('Note: Large files may take some time to upload. Please be patient!')}\n\n"
            "Cancel anytime by sending /cancel"
        )
        return prompt_text
    
    @staticmethod
    def format_video_details_prompt(filename: str, file_size: str) -> str:
        """Format video details prompt"""
        details_text = (
            f"🎬 {HTMLFormatter.bold('Video Details')}\n\n"
            f"📁 File: {HTMLFormatter.code(filename)}\n"
            f"📊 Size: {HTMLFormatter.code(file_size)}\n\n"
            "Please provide the following details for your video:\n\n"
            f"{HTMLFormatter.bold('1. Video Title:')}\n"
            "Send the title for your video (required)\n\n"
            f"{HTMLFormatter.italic('After you send the title, I will ask for the description and other details.')}\n\n"
            "Cancel anytime by sending /cancel"
        )
        return details_text
    
    @staticmethod
    def format_upload_progress(progress: int, filename: str) -> str:
        """Format upload progress message"""
        progress_blocks = progress // 5
        progress_bar = "█" * progress_blocks + "░" * (20 - progress_blocks)
        
        progress_text = (
            f"⏳ {HTMLFormatter.bold('Uploading to YouTube...')}\n\n"
            f"📁 {HTMLFormatter.code(filename)}\n"
            f"📊 Progress: {HTMLFormatter.code(f'{progress}%')}\n"
            f"{HTMLFormatter.code(f'[{progress_bar}]')}\n\n"
            f"{HTMLFormatter.italic('Please wait while your video is being uploaded...')}"
        )
        return progress_text
    
    @staticmethod
    def format_upload_success(video_data: Dict[str, Any]) -> str:
        """Format upload success message"""
        video_id = video_data['video_id']
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        success_text = (
            f"🎉 {HTMLFormatter.bold('Upload Successful!')}\n\n"
            "Your video has been uploaded to YouTube successfully!\n\n"
            f"🎬 {HTMLFormatter.bold('Video Details:')}\n"
            f"📝 Title: {HTMLFormatter.bold(video_data.get('title', 'N/A'))}\n"
            f"🆔 Video ID: {HTMLFormatter.code(video_id)}\n"
            f"🔗 URL: {HTMLFormatter.link('Watch on YouTube', youtube_url)}\n"
            f"📅 Uploaded: {HTMLFormatter.code(current_time)}\n\n"
            f"{HTMLFormatter.italic('Your video is now live on YouTube! 🚀')}\n\n"
            "Want to upload another video? Just send me another video file!"
        )
        return success_text
    
    @staticmethod
    def format_upload_error(error_message: str) -> str:
        """Format upload error message"""
        error_text = (
            f"❌ {HTMLFormatter.bold('Upload Failed')}\n\n"
            "Sorry, there was an error uploading your video:\n\n"
            f"{HTMLFormatter.code(error_message)}\n\n"
            f"{HTMLFormatter.bold('What you can do:')}\n"
            "• Try uploading again\n"
            "• Check if your file format is supported\n"
            "• Make sure your file size is under 2GB\n"
            "• Verify your YouTube authentication is still valid\n\n"
            "Need help? Use /help for more information."
        )
        return error_text
    
    @staticmethod
    def format_history(uploads: List[Dict[str, Any]]) -> str:
        """Format upload history"""
        if not uploads:
            history_text = (
                f"📋 {HTMLFormatter.bold('Upload History')}\n\n"
                f"{HTMLFormatter.italic('No uploads found. Upload your first video to see it here!')}\n\n"
                "Use /upload to start uploading videos."
            )
            return history_text
        
        history_text = f"📋 {HTMLFormatter.bold('Your Upload History')}\n\n"
        
        for i, upload in enumerate(uploads[:10], 1):
            upload_date = upload.get('upload_date', datetime.now())
            if isinstance(upload_date, str):
                date_str = upload_date
            else:
                date_str = upload_date.strftime('%Y-%m-%d %H:%M')
            
            video_id = upload.get('video_id', '')
            youtube_url = upload.get('youtube_url', f"https://www.youtube.com/watch?v={video_id}")
            title = upload.get("title", "Untitled")
            
            history_text += (
                f"{HTMLFormatter.bold(f'{i}. {title}')}\n"
                f"🆔 ID: {HTMLFormatter.code(video_id)}\n"
                f"📅 Date: {HTMLFormatter.code(date_str)}\n"
                f"🔗 {HTMLFormatter.link('Watch', youtube_url)}\n\n"
            )
        
        if len(uploads) > 10:
            history_text += f"{HTMLFormatter.italic('Showing latest 10 uploads...')}\n"
        
        return history_text.strip()
    
    @staticmethod
    def format_stats(total_users: int, total_uploads: int, user_uploads: int) -> str:
        """Format bot statistics"""
        stats_text = (
            f"📊 {HTMLFormatter.bold('Bot Statistics')}\n\n"
            f"👥 Total Users: {HTMLFormatter.code(str(total_users))}\n"
            f"📤 Total Uploads: {HTMLFormatter.code(str(total_uploads))}\n"
            f"🎬 Your Uploads: {HTMLFormatter.code(str(user_uploads))}\n\n"
            f"{HTMLFormatter.italic('Thank you for using YouTube Uploader Bot!')} 🚀"
        )
        return stats_text
    
    @staticmethod
    def format_help_message() -> str:
        """Format detailed help message"""
        help_text = (
            f"❓ {HTMLFormatter.bold('YouTube Uploader Bot Help')}\n\n"
            f"{HTMLFormatter.bold('🔐 Authentication:')}\n"
            "• Use /auth to connect your YouTube account\n"
            "• Follow the OAuth flow to grant permissions\n"
            "• You only need to do this once\n\n"
            f"{HTMLFormatter.bold('📤 Uploading Videos:')}\n"
            "• Send a video file directly to the bot\n"
            "• Supported formats: MP4, AVI, MOV, WMV, FLV, MKV\n"
            "• Maximum file size: 2GB\n"
            "• Add title, description, and tags when prompted\n\n"
            f"{HTMLFormatter.bold('📋 Commands:')}\n"
            "• /start - Welcome message and overview\n"
            "• /auth - Authenticate with YouTube\n"
            "• /upload - Start upload process\n"
            "• /history - View your upload history\n"
            "• /stats - View bot statistics\n"
            "• /help - Show this help message\n"
            "• /cancel - Cancel current operation\n\n"
            f"{HTMLFormatter.bold('🔧 Troubleshooting:')}\n"
            "• If upload fails, try re-authenticating with /auth\n"
            "• Check file format and size requirements\n"
            "• Ensure stable internet connection\n"
            "• Contact support if issues persist\n\n"
            f"{HTMLFormatter.bold('🔒 Privacy & Security:')}\n"
            "• Your OAuth tokens are securely stored\n"
            "• Videos are uploaded to your YouTube channel\n"
            "• Bot doesn't store video files permanently\n"
            "• You can revoke access anytime from Google settings\n\n"
            f"{HTMLFormatter.italic('Need more help? Contact the bot administrator.')}"
        )
        return help_text
    
    @staticmethod
    def format_error_message(error: str) -> str:
        """Format generic error message"""
        error_text = (
            f"❌ {HTMLFormatter.bold('Error')}\n\n"
            f"{HTMLFormatter.code(error)}\n\n"
            f"{HTMLFormatter.italic('Please try again or contact support if the issue persists.')}"
        )
        return error_text
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
