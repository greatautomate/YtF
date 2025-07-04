import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError
import asyncio

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.client = None
        self.db = None
        self.users = None
        self.uploads = None
        self.oauth_tokens = None
        
    async def connect(self):
        """Connect to MongoDB database"""
        try:
            mongodb_url = os.getenv('MONGODB_URL')
            if not mongodb_url:
                raise ValueError("MONGODB_URL environment variable is required")
            
            self.client = AsyncIOMotorClient(mongodb_url)
            self.db = self.client.youtube_bot
            self.users = self.db.users
            self.uploads = self.db.uploads
            self.oauth_tokens = self.db.oauth_tokens
            
            # Create indexes
            await self.create_indexes()
            logger.info("Connected to MongoDB successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def create_indexes(self):
        """Create database indexes for better performance"""
        try:
            await self.users.create_index("user_id", unique=True)
            await self.uploads.create_index("user_id")
            await self.uploads.create_index("upload_date")
            await self.oauth_tokens.create_index("user_id", unique=True)
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
    
    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("Database connection closed")
    
    # User management
    async def add_user(self, user_id: int, username: str = None, first_name: str = None) -> bool:
        """Add a new user to the database"""
        try:
            user_data = {
                "user_id": user_id,
                "username": username,
                "first_name": first_name,
                "joined_date": datetime.utcnow(),
                "is_authenticated": False,
                "upload_count": 0,
                "last_activity": datetime.utcnow()
            }
            await self.users.insert_one(user_data)
            logger.info(f"User {user_id} added to database")
            return True
        except DuplicateKeyError:
            logger.info(f"User {user_id} already exists in database")
            return False
        except Exception as e:
            logger.error(f"Failed to add user {user_id}: {e}")
            return False
    
    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user data from database"""
        try:
            user = await self.users.find_one({"user_id": user_id})
            return user
        except Exception as e:
            logger.error(f"Failed to get user {user_id}: {e}")
            return None
    
    async def update_user_activity(self, user_id: int):
        """Update user's last activity timestamp"""
        try:
            await self.users.update_one(
                {"user_id": user_id},
                {"$set": {"last_activity": datetime.utcnow()}}
            )
        except Exception as e:
            logger.error(f"Failed to update user activity for {user_id}: {e}")
    
    async def set_user_authenticated(self, user_id: int, authenticated: bool = True):
        """Set user authentication status"""
        try:
            await self.users.update_one(
                {"user_id": user_id},
                {"$set": {"is_authenticated": authenticated}}
            )
            logger.info(f"User {user_id} authentication status set to {authenticated}")
        except Exception as e:
            logger.error(f"Failed to set authentication status for {user_id}: {e}")
    
    # OAuth token management
    async def save_oauth_token(self, user_id: int, token_data: Dict[str, Any]):
        """Save OAuth token for user"""
        try:
            token_doc = {
                "user_id": user_id,
                "token_data": token_data,
                "created_date": datetime.utcnow(),
                "updated_date": datetime.utcnow()
            }
            await self.oauth_tokens.replace_one(
                {"user_id": user_id},
                token_doc,
                upsert=True
            )
            logger.info(f"OAuth token saved for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to save OAuth token for {user_id}: {e}")
    
    async def get_oauth_token(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get OAuth token for user"""
        try:
            token_doc = await self.oauth_tokens.find_one({"user_id": user_id})
            return token_doc["token_data"] if token_doc else None
        except Exception as e:
            logger.error(f"Failed to get OAuth token for {user_id}: {e}")
            return None
    
    async def delete_oauth_token(self, user_id: int):
        """Delete OAuth token for user"""
        try:
            await self.oauth_tokens.delete_one({"user_id": user_id})
            logger.info(f"OAuth token deleted for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to delete OAuth token for {user_id}: {e}")
    
    # Upload history management
    async def add_upload_record(self, user_id: int, video_data: Dict[str, Any]):
        """Add upload record to database"""
        try:
            upload_record = {
                "user_id": user_id,
                "video_id": video_data.get("video_id"),
                "title": video_data.get("title"),
                "description": video_data.get("description"),
                "file_name": video_data.get("file_name"),
                "file_size": video_data.get("file_size"),
                "duration": video_data.get("duration"),
                "upload_date": datetime.utcnow(),
                "youtube_url": f"https://www.youtube.com/watch?v={video_data.get('video_id')}",
                "status": "completed"
            }
            await self.uploads.insert_one(upload_record)
            
            # Increment user upload count
            await self.users.update_one(
                {"user_id": user_id},
                {"$inc": {"upload_count": 1}}
            )
            
            logger.info(f"Upload record added for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to add upload record for {user_id}: {e}")
    
    async def get_user_uploads(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user's upload history"""
        try:
            cursor = self.uploads.find({"user_id": user_id}).sort("upload_date", -1).limit(limit)
            uploads = await cursor.to_list(length=limit)
            return uploads
        except Exception as e:
            logger.error(f"Failed to get uploads for user {user_id}: {e}")
            return []
    
    async def get_total_uploads(self) -> int:
        """Get total number of uploads"""
        try:
            count = await self.uploads.count_documents({})
            return count
        except Exception as e:
            logger.error(f"Failed to get total uploads count: {e}")
            return 0
    
    async def get_total_users(self) -> int:
        """Get total number of users"""
        try:
            count = await self.users.count_documents({})
            return count
        except Exception as e:
            logger.error(f"Failed to get total users count: {e}")
            return 0

# Global database instance
db = Database()
