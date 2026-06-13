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

# Create persist data directories
RUN mkdir -p /workspace/data/chromadb /workspace/data/sandbox

# Set env vars for local setup defaults
ENV APP_ENV=local
ENV PORT=8000
ENV HOST=0.0.0.0

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
