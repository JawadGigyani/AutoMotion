# Python 3.10 + Node.js 18 base image
FROM nikolaik/python-nodejs:python3.10-nodejs18-bullseye

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install FFmpeg, Chromium, and required system libraries for Remotion/Puppeteer
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    chromium \
    libnss3 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libxss1 \
    libasound2 \
    libgbm-dev \
    libgtk-3-0 \
    fonts-liberation \
    libappindicator3-1 \
    xdg-utils \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Tell Remotion/Puppeteer to use the OS-installed Chromium
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

WORKDIR /app

# ── Install Remotion Server dependencies ──
COPY remotion/package*.json ./remotion/
RUN cd remotion && npm ci

# ── Install Backend dependencies ──
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# ── Copy application code ──
COPY . .

# Ensure startup script is executable and outputs dir exists
RUN chmod +x /app/startup.sh && mkdir -p /app/backend/outputs

# DigitalOcean App Platform routes to $PORT
ENV PORT=8080
EXPOSE 8080

CMD ["/app/startup.sh"]
