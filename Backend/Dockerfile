FROM python:3.11-slim

# Install system dependencies
# ffmpeg is needed for audio extraction fallback
# build-essential is needed for some python packages
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Render uses $PORT environment variable, default 8080)
EXPOSE 8080

# Run uvicorn on 0.0.0.0 and port 8080 (or $PORT)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
