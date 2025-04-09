FROM python:3.10-slim

# 1. Install system deps
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# 2. Install Python deps
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 3. Copy app
COPY . .

# 4. Set FFmpeg path
ENV FFMPEG_BINARY=/usr/bin/ffmpeg

CMD ["python", "app.py"]