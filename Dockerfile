FROM python:3.11-slim

WORKDIR /workspace

# Install build dependencies for psutil/chromadb wheels if compiled from source
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

# Copy frontend static files to be served by FastAPI
COPY index.html app.js style.css admin_avatar.png ./

# Create persist data directories
RUN mkdir -p /workspace/data/chromadb /workspace/data/sandbox

# Set env vars for setup defaults (PORT will be overridden by Railway)
ENV APP_ENV=production
ENV PORT=8000
ENV HOST=0.0.0.0

CMD ["sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]

