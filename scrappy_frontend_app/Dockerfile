# Use Python 3.11 slim image
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

# Copy the entire parent directory to access main project modules
COPY ../ /app/

# Set environment variables
ENV PYTHONPATH=/app
ENV FLASK_APP=scrappy_frontend_app/app.py
ENV FLASK_ENV=production

# Expose port
EXPOSE 5001

# Change to the scrappy frontend app directory
WORKDIR /app/scrappy_frontend_app

# Run the application
CMD ["python", "run.py"]
