"""
Configuration module for YouTube Uploader Bot
Contains default settings and configuration constants
"""

import os
from typing import List, Dict, Any

class Config:
    """Bot configuration class"""
    
    # Bot Information
    BOT_NAME = os.getenv('BOT_NAME', 'YouTube Uploader Bot')
    BOT_VERSION = '1.0.0'
    BOT_DESCRIPTION = 'Upload videos to YouTube directly from Telegram'
    
    # File Upload Limits
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 2147483648))  # 2GB
    MIN_FILE_SIZE = 1024  # 1KB
    
    # Supported Video Formats
    SUPPORTED_VIDEO_FORMATS = {
        'video/mp4': '.mp4',
        'video/avi': '.avi', 
        'video/quicktime': '.mov',
        'video/x-msvideo': '.avi',
        'video/x-flv': '.flv',
        'video/x-matroska': '.mkv',
        'video/webm': '.webm',
        'application/octet-stream': '.mp4'  # Fallback
    }
    
    SUPPORTED_EXTENSIONS = {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm', '.m4v', '.3gp'}
    
    # YouTube API Settings
    YOUTUBE_SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    YOUTUBE_API_SERVICE_NAME = 'youtube'
    YOUTUBE_API_VERSION = 'v3'
    
    # Default Video Settings
    DEFAULT_PRIVACY_STATUS = 'private'  # private, unlisted, public
    DEFAULT_CATEGORY_ID = '22'  # People & Blogs
    DEFAULT_MADE_FOR_KIDS = False
    
    # Database Settings
    DB_NAME = 'youtube_bot'
    COLLECTIONS = {
        'users': 'users',
        'uploads': 'uploads', 
        'oauth_tokens': 'oauth_tokens'
    }
    
    # Logging Configuration
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    # Rate Limiting
    MAX_UPLOADS_PER_DAY = 50
    MAX_UPLOADS_PER_HOUR = 10
    
    # Message Templates
    MESSAGES = {
        'welcome': '🎬 Welcome to YouTube Uploader Bot!',
        'auth_required': '🔐 Please authenticate first using /auth command.',
        'upload_success': '🎉 Upload successful!',
        'upload_failed': '❌ Upload failed.',
        'file_too_large': '❌ File too large. Maximum size is {max_size}MB.',
        'unsupported_format': '❌ Unsupported file format.',
        'processing': '⏳ Processing your request...',
        'uploading': '📤 Uploading to YouTube...',
        'completed': '✅ Completed successfully!'
    }
    
    # Error Messages
    ERROR_MESSAGES = {
        'auth_failed': 'Authentication failed. Please try again.',
        'upload_failed': 'Upload failed. Please check your file and try again.',
        'network_error': 'Network error. Please check your connection.',
        'quota_exceeded': 'Daily upload quota exceeded. Try again tomorrow.',
        'invalid_token': 'Invalid authentication token. Please re-authenticate.',
        'file_not_found': 'File not found or corrupted.',
        'permission_denied': 'Permission denied. Check your YouTube channel access.'
    }
    
    # Progress Messages
    PROGRESS_MESSAGES = {
        0: '🔄 Initializing...',
        10: '📥 Downloading file...',
        20: '🔍 Validating file...',
        30: '🔐 Authenticating...',
        40: '📤 Starting upload...',
        50: '⏳ Uploading... 50%',
        60: '⏳ Uploading... 60%',
        70: '⏳ Uploading... 70%',
        80: '⏳ Uploading... 80%',
        90: '⏳ Uploading... 90%',
        95: '🔄 Finalizing...',
        100: '✅ Upload complete!'
    }
    
    # Command Descriptions
    COMMANDS = {
        'start': 'Start the bot and show welcome message',
        'auth': 'Authenticate with Google/YouTube',
        'upload': 'Upload a video to YouTube',
        'history': 'View your upload history',
        'stats': 'View bot statistics',
        'help': 'Show help and instructions',
        'cancel': 'Cancel current operation'
    }
    
    # HTML Formatting
    HTML_TAGS = {
        'bold': '<b>{}</b>',
        'italic': '<i>{}</i>',
        'code': '<code>{}</code>',
        'pre': '<pre>{}</pre>',
        'link': '<a href="{}">{}</a>',
        'underline': '<u>{}</u>',
        'strikethrough': '<s>{}</s>'
    }
    
    # Emojis
    EMOJIS = {
        'video': '🎬',
        'upload': '📤',
        'download': '📥',
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️',
        'loading': '⏳',
        'auth': '🔐',
        'stats': '📊',
        'history': '📋',
        'help': '❓',
        'cancel': '🚫',
        'file': '📁',
        'link': '🔗',
        'user': '👤',
        'bot': '🤖',
        'youtube': '📺',
        'google': '🔍'
    }
    
    @classmethod
    def get_file_size_mb(cls, size_bytes: int) -> float:
        """Convert bytes to MB"""
        return round(size_bytes / (1024 * 1024), 2)
    
    @classmethod
    def get_max_file_size_mb(cls) -> float:
        """Get maximum file size in MB"""
        return cls.get_file_size_mb(cls.MAX_FILE_SIZE)
    
    @classmethod
    def is_supported_format(cls, mime_type: str) -> bool:
        """Check if file format is supported"""
        return mime_type in cls.SUPPORTED_VIDEO_FORMATS
    
    @classmethod
    def is_supported_extension(cls, filename: str) -> bool:
        """Check if file extension is supported"""
        ext = os.path.splitext(filename)[1].lower()
        return ext in cls.SUPPORTED_EXTENSIONS
    
    @classmethod
    def get_progress_message(cls, progress: int) -> str:
        """Get progress message for given percentage"""
        # Find the closest progress value
        closest = min(cls.PROGRESS_MESSAGES.keys(), key=lambda x: abs(x - progress))
        return cls.PROGRESS_MESSAGES[closest]
    
    @classmethod
    def format_file_size(cls, size_bytes: int) -> str:
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

# Global config instance
config = Config()
