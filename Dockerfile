FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main script
COPY webpage_tracker.py .

# Create directories for persistent data
RUN mkdir -p webpage_versions diffs

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["python", "webpage_tracker.py"] 