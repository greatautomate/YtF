import os
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
import aiofiles
from dotenv import load_dotenv

from database import db
from youtube_client import youtube_client
from html_formatter import HTMLFormatter
from video_handler import VideoHandler

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class YouTubeBot:
    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN')
        self.api_id = int(os.getenv('API_ID'))
        self.api_hash = os.getenv('API_HASH')
        self.allowed_users = self._parse_allowed_users()
        self.max_file_size = int(os.getenv('MAX_FILE_SIZE', 2147483648))  # 2GB default
        
        if not all([self.bot_token, self.api_id, self.api_hash]):
            raise ValueError("Bot credentials are required")
        
        # Initialize Pyrogram client
        self.app = Client(
            "youtube_bot",
            api_id=self.api_id,
            api_hash=self.api_hash,
            bot_token=self.bot_token
        )
        
        # User states for conversation flow
        self.user_states: Dict[int, Dict[str, Any]] = {}
        
        # Video handler
        self.video_handler = VideoHandler()
        
        # Register handlers
        self._register_handlers()
    
    def _parse_allowed_users(self) -> list:
        """Parse allowed users from environment variable"""
        allowed_users_str = os.getenv('ALLOWED_USERS', '')
        if not allowed_users_str:
            return []
        
        try:
            return [int(user_id.strip()) for user_id in allowed_users_str.split(',') if user_id.strip()]
        except ValueError:
            logger.warning("Invalid ALLOWED_USERS format. Allowing all users.")
            return []
    
    def _register_handlers(self):
        """Register all bot handlers"""
        
        @self.app.on_message(filters.command("start"))
        async def start_command(client, message: Message):
            await self.handle_start(message)
        
        @self.app.on_message(filters.command("auth"))
        async def auth_command(client, message: Message):
            await self.handle_auth(message)
        
        @self.app.on_message(filters.command("upload"))
        async def upload_command(client, message: Message):
            await self.handle_upload_command(message)
        
        @self.app.on_message(filters.command("history"))
        async def history_command(client, message: Message):
            await self.handle_history(message)
        
        @self.app.on_message(filters.command("stats"))
        async def stats_command(client, message: Message):
            await self.handle_stats(message)
        
        @self.app.on_message(filters.command("help"))
        async def help_command(client, message: Message):
            await self.handle_help(message)
        
        @self.app.on_message(filters.command("cancel"))
        async def cancel_command(client, message: Message):
            await self.handle_cancel(message)
        
        @self.app.on_message(filters.video | filters.document)
        async def video_handler(client, message: Message):
            await self.handle_video(message)
        
        @self.app.on_message(filters.text & ~filters.command(["start", "auth", "upload", "history", "stats", "help", "cancel"]))
        async def text_handler(client, message: Message):
            await self.handle_text(message)
    
    async def is_user_allowed(self, user_id: int) -> bool:
        """Check if user is allowed to use the bot"""
        if not self.allowed_users:  # If no restrictions, allow all users
            return True
        return user_id in self.allowed_users
    
    async def ensure_user_in_db(self, message: Message):
        """Ensure user exists in database"""
        user = message.from_user
        await db.add_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name
        )
        await db.update_user_activity(user.id)
    
    async def handle_start(self, message: Message):
        """Handle /start command"""
        try:
            if not await self.is_user_allowed(message.from_user.id):
                await message.reply_text("❌ You are not authorized to use this bot.")
                return
            
            await self.ensure_user_in_db(message)
            
            welcome_msg = HTMLFormatter.format_welcome_message(message.from_user.first_name or "User")
            await message.reply_text(welcome_msg, parse_mode="HTML", disable_web_page_preview=True)
            
        except Exception as e:
            logger.error(f"Error in start command: {e}")
            await message.reply_text("❌ An error occurred. Please try again.")
    
    async def handle_auth(self, message: Message):
        """Handle /auth command"""
        try:
            if not await self.is_user_allowed(message.from_user.id):
                await message.reply_text("❌ You are not authorized to use this bot.")
                return
            
            await self.ensure_user_in_db(message)
            
            # Check if user is already authenticated
            token_data = await db.get_oauth_token(message.from_user.id)
            if token_data:
                await message.reply_text(
                    "✅ You are already authenticated! You can start uploading videos.",
                    parse_mode="HTML"
                )
                return
            
            # Generate OAuth URL
            auth_url = youtube_client.get_oauth_url()
            auth_msg = HTMLFormatter.format_auth_message(auth_url)
            
            # Set user state to waiting for auth code
            self.user_states[message.from_user.id] = {
                'state': 'waiting_auth_code',
                'timestamp': datetime.now()
            }
            
            await message.reply_text(auth_msg, parse_mode="HTML", disable_web_page_preview=True)
            
        except Exception as e:
            logger.error(f"Error in auth command: {e}")
            await message.reply_text("❌ Failed to generate authentication URL. Please try again.")
    
    async def handle_upload_command(self, message: Message):
        """Handle /upload command"""
        try:
            if not await self.is_user_allowed(message.from_user.id):
                await message.reply_text("❌ You are not authorized to use this bot.")
                return
            
            await self.ensure_user_in_db(message)
            
            # Check if user is authenticated
            token_data = await db.get_oauth_token(message.from_user.id)
            if not token_data:
                await message.reply_text(
                    "🔐 Please authenticate first using /auth command.",
                    parse_mode="HTML"
                )
                return
            
            upload_msg = HTMLFormatter.format_upload_prompt()
            self.user_states[message.from_user.id] = {
                'state': 'waiting_video',
                'timestamp': datetime.now()
            }
            
            await message.reply_text(upload_msg, parse_mode="HTML")
            
        except Exception as e:
            logger.error(f"Error in upload command: {e}")
            await message.reply_text("❌ An error occurred. Please try again.")
    
    async def handle_history(self, message: Message):
        """Handle /history command"""
        try:
            if not await self.is_user_allowed(message.from_user.id):
                await message.reply_text("❌ You are not authorized to use this bot.")
                return
            
            await self.ensure_user_in_db(message)
            
            uploads = await db.get_user_uploads(message.from_user.id, limit=10)
            history_msg = HTMLFormatter.format_history(uploads)
            
            await message.reply_text(history_msg, parse_mode="HTML", disable_web_page_preview=True)
            
        except Exception as e:
            logger.error(f"Error in history command: {e}")
            await message.reply_text("❌ Failed to retrieve upload history.")
    
    async def handle_stats(self, message: Message):
        """Handle /stats command"""
        try:
            if not await self.is_user_allowed(message.from_user.id):
                await message.reply_text("❌ You are not authorized to use this bot.")
                return
            
            await self.ensure_user_in_db(message)
            
            total_users = await db.get_total_users()
            total_uploads = await db.get_total_uploads()
            user_uploads = len(await db.get_user_uploads(message.from_user.id))
            
            stats_msg = HTMLFormatter.format_stats(total_users, total_uploads, user_uploads)
            await message.reply_text(stats_msg, parse_mode="HTML")
            
        except Exception as e:
            logger.error(f"Error in stats command: {e}")
            await message.reply_text("❌ Failed to retrieve statistics.")
    
    async def handle_help(self, message: Message):
        """Handle /help command"""
        try:
            if not await self.is_user_allowed(message.from_user.id):
                await message.reply_text("❌ You are not authorized to use this bot.")
                return
            
            help_msg = HTMLFormatter.format_help_message()
            await message.reply_text(help_msg, parse_mode="HTML", disable_web_page_preview=True)
            
        except Exception as e:
            logger.error(f"Error in help command: {e}")
            await message.reply_text("❌ An error occurred. Please try again.")
    
    async def handle_cancel(self, message: Message):
        """Handle /cancel command"""
        try:
            user_id = message.from_user.id
            if user_id in self.user_states:
                del self.user_states[user_id]
                await message.reply_text("✅ Operation cancelled.")
            else:
                await message.reply_text("ℹ️ No operation to cancel.")
                
        except Exception as e:
            logger.error(f"Error in cancel command: {e}")
            await message.reply_text("❌ An error occurred.")
    
    async def handle_video(self, message: Message):
        """Handle video files"""
        try:
            if not await self.is_user_allowed(message.from_user.id):
                await message.reply_text("❌ You are not authorized to use this bot.")
                return
            
            await self.ensure_user_in_db(message)
            
            # Check if user is authenticated
            token_data = await db.get_oauth_token(message.from_user.id)
            if not token_data:
                await message.reply_text(
                    "🔐 Please authenticate first using /auth command.",
                    parse_mode="HTML"
                )
                return
            
            # Process video
            await self.video_handler.process_video(message, self.user_states)
            
        except Exception as e:
            logger.error(f"Error handling video: {e}")
            await message.reply_text("❌ Failed to process video. Please try again.")
    
    async def handle_text(self, message: Message):
        """Handle text messages based on user state"""
        try:
            user_id = message.from_user.id
            user_state = self.user_states.get(user_id)
            
            if not user_state:
                await message.reply_text(
                    "ℹ️ Send /start to begin or /help for available commands.",
                    parse_mode="HTML"
                )
                return
            
            state = user_state.get('state')
            
            if state == 'waiting_auth_code':
                await self._handle_auth_code(message)
            elif state == 'waiting_title':
                await self._handle_video_title(message)
            elif state == 'waiting_description':
                await self._handle_video_description(message)
            else:
                await message.reply_text("ℹ️ I don't understand. Use /help for available commands.")
                
        except Exception as e:
            logger.error(f"Error handling text: {e}")
            await message.reply_text("❌ An error occurred. Please try again.")
    
    async def _handle_auth_code(self, message: Message):
        """Handle OAuth authorization code"""
        try:
            auth_code = message.text.strip()
            
            # Exchange code for token
            token_data = await youtube_client.exchange_code_for_token(auth_code)
            
            if token_data:
                # Save token to database
                await db.save_oauth_token(message.from_user.id, token_data)
                await db.set_user_authenticated(message.from_user.id, True)
                
                # Clear user state
                if message.from_user.id in self.user_states:
                    del self.user_states[message.from_user.id]
                
                success_msg = HTMLFormatter.format_auth_success_message(
                    message.from_user.first_name or "User"
                )
                await message.reply_text(success_msg, parse_mode="HTML")
            else:
                await message.reply_text(
                    "❌ Invalid authorization code. Please try /auth again.",
                    parse_mode="HTML"
                )
                
        except Exception as e:
            logger.error(f"Error handling auth code: {e}")
            await message.reply_text("❌ Authentication failed. Please try /auth again.")
    
    async def _handle_video_title(self, message: Message):
        """Handle video title input"""
        title = message.text.strip()
        if len(title) > 100:
            await message.reply_text("❌ Title is too long. Please keep it under 100 characters.")
            return
        
        # Update user state
        self.user_states[message.from_user.id]['title'] = title
        self.user_states[message.from_user.id]['state'] = 'waiting_description'
        
        await message.reply_text(
            f"✅ Title set: <b>{HTMLFormatter.escape(title)}</b>\n\n"
            "📝 Now send the video description (optional - send 'skip' to skip):",
            parse_mode="HTML"
        )
    
    async def _handle_video_description(self, message: Message):
        """Handle video description input"""
        description = message.text.strip()
        if description.lower() == 'skip':
            description = ""
        
        # Update user state and start upload
        user_state = self.user_states[message.from_user.id]
        user_state['description'] = description
        
        await self.video_handler.upload_video_to_youtube(message, user_state)
        
        # Clear user state
        if message.from_user.id in self.user_states:
            del self.user_states[message.from_user.id]
    
    async def start(self):
        """Start the bot"""
        try:
            # Connect to database
            await db.connect()
            logger.info("Connected to database")
            
            # Start the bot
            await self.app.start()
            logger.info("Bot started successfully")
            
            # Keep the bot running
            await asyncio.Event().wait()
            
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            raise
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop the bot"""
        try:
            await self.app.stop()
            await db.close()
            logger.info("Bot stopped")
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")

# Create bot instance
bot = YouTubeBot()

if __name__ == "__main__":
    try:
        asyncio.run(bot.start())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        raise
