# Frontend-only Dockerfile for Next.js Dashboard
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY new/package*.json ./

# Install dependencies
RUN npm ci

# Copy frontend source
COPY new/ ./

# Build the Next.js app
RUN npm run build

# Install serve to run the built app
RUN npm install -g serve

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/ || exit 1

# Serve the built Next.js app
CMD ["serve", "-s", ".next", "-l", "3000"] 