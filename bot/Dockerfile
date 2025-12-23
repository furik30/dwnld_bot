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

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p downloads logs data

# Command to run the bot
CMD ["python", "main.py"]
