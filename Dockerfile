# Demo-only Dockerfile for CFO ChatbotUI
# - No internal hostnames or secrets
# - Builds static UI and runs a minimal FastAPI gateway
# - For local testing; do NOT expose these ports on the public internet

FROM node:20-bullseye AS ui-build
WORKDIR /app/ui
# Copy only UI first for better layer caching
COPY ui/package*.json ./
RUN npm ci
COPY ui/ ./
# Build static assets (dist/)
RUN npm run build

# ------------------------------

FROM node:20-bullseye
# Install Python runtime for the demo FastAPI gateway (no system secrets)
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 python3-pip ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy backend/gateway files
# Expecting: requirements.txt and gateway.py at repo root (adjust paths if needed)
COPY requirements.txt ./requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY gateway.py ./gateway.py

# Copy built UI from the first stage
COPY --from=ui-build /app/ui/dist ./ui/dist

# Install a tiny static file server to serve the built UI
RUN npm i -g serve

# Demo-safe, local-only defaults (override via -e at runtime if needed)
ENV CFO_GATEWAY_BIND=0.0.0.0
ENV CFO_GATEWAY_PORT=9000
# Note: Router/backing services are NOT included in this public demo image.

# Non-root user for safety
RUN useradd -m appuser
USER appuser

EXPOSE 5173 9000

# Start both processes:
# - serve UI static build at :5173
# - run FastAPI demo gateway at :9000
CMD bash -lc "serve -s ui/dist -l 5173 & python3 gateway.py"

