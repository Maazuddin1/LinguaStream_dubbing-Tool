# Dockerfile
FROM python:3.9-slim

# Install system dependencies (FFmpeg + build tools)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python packages (prefer wheels)
COPY requirements.txt .
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt

COPY . .

CMD ["python", "app.py"]