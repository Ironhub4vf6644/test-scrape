FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    libnss3 \
    libxss1 \
    libasound2 \
    libgbm1 \
    libdbus-glib-1-2 \
    chromium \
    fonts-noto-color-emoji && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt && \
    playwright install chromium

COPY . .

CMD['python3': 'test_scraper.py']