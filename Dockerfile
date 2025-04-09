FROM python:3.10-slim

# 1. Install system deps (added build essentials)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Install Python deps (added wheel and prefer-binary)
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip wheel && \
    pip install --no-cache-dir --prefer-binary -r requirements.txt

# 3. Copy app
COPY . .

# 4. Set FFmpeg path
ENV FFMPEG_BINARY=/usr/bin/ffmpeg

CMD ["python", "app.py"]