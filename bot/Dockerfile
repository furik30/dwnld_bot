FROM python:3.11-slim

# Install system dependencies
# ffmpeg: for audio conversion
# gcc: for compiling some python libs if needed
# curl: for healthchecks or downloading files
RUN apt-get update && apt-get install -y \
    ffmpeg \
    gcc \
    curl \
    nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p downloads logs data cookies

# Command to run the bot
CMD ["/bin/bash", "-c", "pip install --upgrade --no-cache-dir yt-dlp && python main.py"]