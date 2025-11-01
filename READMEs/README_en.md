# Telegram Downloader Bot

This is a Telegram bot that allows you to download music and videos from various platforms like YouTube, TikTok, Instagram Reels, and SoundCloud.

## Features

- Search and download music from YouTube.
- Download videos from TikTok, Instagram Reels, and YouTube.
- Download playlists from YouTube and SoundCloud.
- Inline mode for quick search and download.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/furik30/dwnld_bot
    cd dwnld_bot
    ```

2.  **Run the installer:**
    This will create a virtual environment, install dependencies, and create a `.env` file for you.
    ```bash
    bash install.sh
    ```

3.  **Configuration:**
    -   Open the newly created `.env` file.
    -   Fill in your `TELEGRAM_TOKEN` from BotFather.
    -   Optionally, set `OWNER_USERNAME` and `INSTAGRAM_USERNAME`.

4.  **Running the bot:**
    ```bash
    source venv/bin/activate
    python dwnld_bot.py
    ```

## Cookie Files

-   `youtube_cookies.txt`: Used by `yt-dlp` to bypass age restrictions and other limitations on YouTube.
-   `instagram_cookies.txt`: Required for downloading Instagram Reels. See [README_INSTAGRAM.md](README_INSTAGRAM.md) for details.
## License

This project is licensed under the MIT [LICENSE](LICENSE).