FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install nodejs for Pi Coding Agent CLI
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install python packages
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Install Pi Coding Agent in container root
COPY package.json package-lock.json /app/
RUN npm ci --omit=dev

# Copy application source
COPY backend /app/backend
COPY .pi /app/.pi

WORKDIR /app/backend

EXPOSE 8000

CMD ["python", "run.py"]
