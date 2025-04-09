FROM python:3.9-slim

# 1. Install system dependencies + build essentials
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Install wheel package FIRST (critical)
RUN pip install --upgrade pip wheel setuptools

WORKDIR /app

# 3. Copy requirements and install with NO-BINARY flag
COPY requirements.txt .
RUN pip install --no-cache-dir \
    --only-binary=:all: \  # Force wheel-only installation
    -r requirements.txt

# 4. Copy application code
COPY . .

# 5. Set FFmpeg path (for moviepy)
ENV FFMPEG_BINARY=/usr/bin/ffmpeg

CMD ["python", "app.py"]