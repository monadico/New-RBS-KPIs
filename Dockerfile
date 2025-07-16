# Multi-stage Dockerfile for Betting Analytics API + Frontend
FROM node:18-alpine AS frontend-builder

# Set working directory
WORKDIR /app

# Copy package files
COPY new/package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy frontend source
COPY new/ ./

# Build the Next.js app
RUN npm run build

# Python API stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python application files
COPY betting_database.py .
COPY json_query.py .
COPY api_server.py .

# Copy the built frontend from the previous stage
COPY --from=frontend-builder /app/.next ./new/.next
COPY --from=frontend-builder /app/public ./new/public

# Create data directory for SQLite database
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Run the API server
CMD ["python", "api_server.py"] 