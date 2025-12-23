# Telegram Downloader Bot

A powerful Telegram bot to download music and videos from YouTube, Instagram (Reels), TikTok, and SoundCloud.
Refactored for speed (Pyrogram), modularity, and ease of deployment (Docker).

## Features

- 🎵 **Music**: Search and download from YouTube (MP3).
- 📹 **Video**: Download from YouTube, TikTok, Instagram Reels.
- 📦 **Playlists**: Support for YouTube and SoundCloud playlists.
- 🚀 **Fast**: Built on Pyrogram (MTProto).
- 🐳 **Dockerized**: Easy to deploy with Docker Compose.
- 🛠 **CLI**: `downloader.sh` for easy management.
- 🍪 **Cookies**: Support for Instagram and YouTube cookies to bypass restrictions.
- 🔐 **Admin Panel**: View logs and status directly in Telegram.
- 🔗 **Deep Links**: Shareable links for videos.

## Prerequisites

- Docker & Docker Compose
- Telegram Bot Token (@BotFather)
- Telegram API ID & Hash (https://my.telegram.org)

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/dwnld_bot.git
    cd dwnld_bot
    ```

2.  **Configuration:**
    -   Copy `.env.example` to `.env` (or let the script do it).
    -   Edit `.env` and fill in your credentials.
    ```bash
    ./downloader.sh edit-env
    ```

3.  **Cookies (Optional but Recommended):**
    -   **Instagram**: Export cookies in Netscape format (using extensions like "Get cookies.txt LOCALLY") and save as `instagram_cookies.txt` in the root folder.
    -   **YouTube**: Similarly, save `youtube_cookies.txt` in the root folder to bypass age restrictions.

4.  **Run the bot:**
    ```bash
    ./downloader.sh up
    ```

## Usage

- **/start**: Start the bot.
- **Search**: Send any text to search for a song.
- **Links**: Send a link from supported platforms (YouTube, Instagram, TikTok, SoundCloud) to download.
- **Inline**: Type `@YourBotUsername query` in any chat.

### Admin Commands

- **/admin** or **/logs**: Open the admin panel (only for `OWNER_ID`).
    -   **Logs**: View last 20 log lines.
    -   **Status**: View system memory usage and active threads.
    -   **Errors**: View only error logs.

## CLI Commands (`./downloader.sh`)

- `up`: Start bot in background.
- `down`: Stop bot.
- `logs [n]`: View logs (tail).
- `restart`: Restart bot.
- `update`: Pull git changes and rebuild.
- `status`: Check container status.

## Project Structure

- `main.py`: Entry point.
- `modules/`: Bot handlers (youtube, instagram, admin).
- `utils/`: Helper functions (logger, storage, messages).
- `config/`: Configuration files (messages.yml).
- `data/`: Persistent data (deep links, session files).
- `downloads/`: Temporary download folder.

## License

MIT
