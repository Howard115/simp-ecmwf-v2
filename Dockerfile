# Force AMD64 platform for compatibility with Google Chrome
FROM --platform=linux/amd64 ubuntu:24.04

# Install basic dependencies first
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    sudo \
    gnupg \
    software-properties-common \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | \
    gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg
RUN echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | \
    tee /etc/apt/sources.list.d/google-chrome.list

# Update package list and install Chrome
RUN apt-get update && apt-get install -y google-chrome-stable && rm -rf /var/lib/apt/lists/*

# Install uv using the official installer and ensure it's properly available
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    cp /root/.local/bin/uv /usr/local/bin/uv && \
    chmod +x /usr/local/bin/uv

# Add Google Chrome repository using modern approach


WORKDIR /app

COPY pyproject.toml /app/pyproject.toml
RUN mkdir -p /app/weather_img
COPY app.py /app/app.py

CMD ["uv", "run", "app.py"]