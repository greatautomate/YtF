# 🎬 YouTube Uploader Bot

A powerful Telegram bot that allows users to upload videos directly to YouTube using Google OAuth authentication. Built with Pyrogram, Google APIs, and MongoDB for a seamless video uploading experience.

## ✨ Features

- **🔐 Google OAuth Integration**: Secure authentication with YouTube
- **📤 Direct Video Upload**: Upload videos from Telegram to YouTube
- **💾 MongoDB Storage**: User data and upload history tracking
- **🎨 HTML Formatted Messages**: Beautiful, responsive message formatting
- **📊 Upload History**: Track all your uploads with detailed statistics
- **🔒 User Access Control**: Configurable user restrictions
- **🐳 Docker Ready**: Easy deployment with Docker and Render.com
- **⚡ Async Operations**: High-performance asynchronous processing
- **📱 Progress Tracking**: Real-time upload progress updates

## 🚀 Quick Start

### Prerequisites

1. **Telegram Bot Token**: Create a bot via [@BotFather](https://t.me/botfather)
2. **Telegram API Credentials**: Get from [my.telegram.org](https://my.telegram.org)
3. **Google OAuth Credentials**: Set up at [Google Cloud Console](https://console.cloud.google.com)
4. **MongoDB Database**: Create at [MongoDB Atlas](https://www.mongodb.com/atlas)

### 🔧 Local Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd youtube-uploader-bot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. **Run the bot**:
   ```bash
   python bot.py
   ```

## 🌐 Deployment on Render.com

### Method 1: Using render.yaml (Recommended)

1. **Fork this repository** to your GitHub account

2. **Connect to Render.com**:
   - Go to [Render.com](https://render.com)
   - Connect your GitHub account
   - Create a new service from your forked repository

3. **Configure Environment Variables** in Render dashboard:
   ```
   BOT_TOKEN=your_telegram_bot_token
   API_ID=your_telegram_api_id
   API_HASH=your_telegram_api_hash
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   MONGODB_URL=your_mongodb_connection_string
   ALLOWED_USERS=user_id1,user_id2,user_id3
   ```

4. **Deploy**: Render will automatically deploy using the `render.yaml` configuration

### Method 2: Manual Setup

1. **Create a new Web Service** on Render
2. **Select "Docker"** as the environment
3. **Configure**:
   - **Build Command**: `docker build -t youtube-bot .`
   - **Start Command**: `python bot.py`
   - **Plan**: Starter (or higher)
4. **Add environment variables** as listed above
5. **Deploy**

## 🔑 Environment Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `BOT_TOKEN` | Telegram bot token from BotFather | ✅ | `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz` |
| `API_ID` | Telegram API ID from my.telegram.org | ✅ | `12345678` |
| `API_HASH` | Telegram API hash from my.telegram.org | ✅ | `abcdef1234567890abcdef1234567890` |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | ✅ | `123456789.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | ✅ | `GOCSPX-abcdefghijklmnopqrstuvwxyz` |
| `MONGODB_URL` | MongoDB connection string | ✅ | `mongodb+srv://user:pass@cluster.mongodb.net/db` |
| `BOT_NAME` | Display name for the bot | ❌ | `YouTube Uploader Bot` |
| `MAX_FILE_SIZE` | Maximum file size in bytes | ❌ | `2147483648` (2GB) |
| `ALLOWED_USERS` | Comma-separated user IDs | ❌ | `123456789,987654321` |
| `LOG_LEVEL` | Logging level | ❌ | `INFO` |

## 🔐 Google OAuth Setup

1. **Go to [Google Cloud Console](https://console.cloud.google.com)**

2. **Create a new project** or select existing one

3. **Enable YouTube Data API v3**:
   - Go to "APIs & Services" > "Library"
   - Search for "YouTube Data API v3"
   - Click "Enable"

4. **Create OAuth 2.0 Credentials**:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client ID"
   - Choose "Desktop application"
   - Note down Client ID and Client Secret

5. **Configure OAuth Consent Screen**:
   - Add your email as a test user
   - Add required scopes: `https://www.googleapis.com/auth/youtube.upload`

## 💾 MongoDB Setup

1. **Create MongoDB Atlas Account**: [mongodb.com/atlas](https://www.mongodb.com/atlas)

2. **Create a Cluster**:
   - Choose free tier (M0)
   - Select your preferred region

3. **Create Database User**:
   - Go to "Database Access"
   - Add new user with read/write permissions

4. **Configure Network Access**:
   - Go to "Network Access"
   - Add IP address `0.0.0.0/0` (allow from anywhere)

5. **Get Connection String**:
   - Go to "Clusters" > "Connect"
   - Choose "Connect your application"
   - Copy the connection string

## 🤖 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and bot overview |
| `/auth` | Authenticate with Google/YouTube |
| `/upload` | Start video upload process |
| `/history` | View upload history |
| `/stats` | View bot statistics |
| `/help` | Detailed help and instructions |
| `/cancel` | Cancel current operation |

## 📱 Usage Flow

1. **Start the bot**: Send `/start` to get welcome message
2. **Authenticate**: Use `/auth` to connect YouTube account
3. **Upload video**: Send a video file or use `/upload`
4. **Add details**: Provide title and description
5. **Wait for upload**: Monitor progress in real-time
6. **Get YouTube link**: Receive direct link to uploaded video

## 🛠️ Technical Details

### Architecture
- **Framework**: Pyrogram (Telegram MTProto API)
- **Database**: MongoDB with Motor (async driver)
- **YouTube API**: Google API Python Client
- **Authentication**: Google OAuth 2.0
- **Deployment**: Docker + Render.com

### File Structure
```
├── bot.py              # Main bot application
├── database.py         # MongoDB operations
├── youtube_client.py   # YouTube API integration
├── video_handler.py    # Video processing logic
├── html_formatter.py   # Message formatting utilities
├── requirements.txt    # Python dependencies
├── Dockerfile         # Docker configuration
├── render.yaml        # Render.com deployment config
├── .env.example       # Environment variables template
└── README.md          # This file
```

### Security Features
- OAuth 2.0 secure authentication
- User access control
- Secure token storage
- Input validation and sanitization
- Error handling and logging

## 🔧 Troubleshooting

### Common Issues

**Authentication Failed**:
- Verify Google OAuth credentials
- Check if YouTube Data API is enabled
- Ensure OAuth consent screen is configured

**Upload Failed**:
- Check file size (max 2GB)
- Verify supported format (MP4, AVI, MOV, etc.)
- Ensure stable internet connection

**Database Connection Error**:
- Verify MongoDB connection string
- Check network access settings
- Ensure database user has proper permissions

**Bot Not Responding**:
- Check bot token validity
- Verify Telegram API credentials
- Review logs for error messages

### Logs and Monitoring

The bot provides comprehensive logging. Check logs for:
- Authentication events
- Upload progress
- Error messages
- Database operations

## 🎯 Features in Detail

### HTML Message Formatting
The bot uses rich HTML formatting for all messages, providing:
- **Bold** and *italic* text styling
- `Code blocks` for technical information
- [Clickable links](https://example.com) for easy navigation
- Structured layouts with emojis and sections
- Progress bars and status indicators

### Video Upload Process
1. **File Validation**: Checks format, size, and type
2. **Metadata Collection**: Gathers title, description, and tags
3. **Progress Tracking**: Real-time upload status updates
4. **YouTube Integration**: Direct upload to user's channel
5. **History Logging**: Permanent record in MongoDB

### Security & Privacy
- **OAuth 2.0**: Industry-standard authentication
- **Token Encryption**: Secure storage of access tokens
- **User Restrictions**: Configurable access control
- **Data Protection**: Minimal data retention policy
- **Audit Logging**: Complete operation tracking

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the logs for error details

## 🙏 Acknowledgments

- [Pyrogram](https://pyrogram.org) - Modern Telegram Bot Framework
- [Google APIs](https://developers.google.com/youtube) - YouTube Data API
- [MongoDB](https://www.mongodb.com) - Database Solution
- [Render.com](https://render.com) - Deployment Platform

---

**Made with ❤️ for the YouTube creator community**
