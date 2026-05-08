ARG BUILD_FROM=ghcr.io/home-assistant/aarch64-base:latest

# --- Stage 1: Frontend bauen (Next.js -> statische Dateien) ---
# --platform=$BUILDPLATFORM: immer auf der nativen Runner-CPU bauen,
# nicht unter QEMU-Emulation. Output ist platform-unabhaengiges HTML/JS.
FROM --platform=$BUILDPLATFORM node:20-alpine AS frontend-build
WORKDIR /build
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --no-audit --no-fund --prefer-offline 2>/dev/null || npm install --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

# --- Stage 2: HA-Add-on Container ---
FROM ${BUILD_FROM}

ENV LANG=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STATIC_DIR=/app/static

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-venv python3-pip ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir --upgrade pip

ENV PATH="/opt/venv/bin:${PATH}"

WORKDIR /app

COPY backend/requirements.txt /app/requirements.txt
RUN /opt/venv/bin/pip install --no-cache-dir -r /app/requirements.txt

COPY backend/ /app/
COPY --from=frontend-build /build/out /app/static

COPY run.sh /run.sh
RUN chmod +x /run.sh

EXPOSE 8000
CMD ["/run.sh"]
