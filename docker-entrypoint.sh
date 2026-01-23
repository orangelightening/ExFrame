#!/bin/bash
set -e

# Fix permissions on writable directories
# This runs as root before switching to appuser
echo "[Entrypoint] Fixing permissions..."

# Fix universe domain JSON files
if [ -d "/app/universes" ]; then
    find /app/universes -name "*.json" ! -name "embeddings.json" -exec chmod 666 {} \; 2>/dev/null || true
    find /app/universes -type d -exec chmod 777 {} \; 2>/dev/null || true
fi

# Fix logs directory
if [ -d "/app/logs" ]; then
    chmod -R 777 /app/logs 2>/dev/null || true
else
    mkdir -p /app/logs && chmod 777 /app/logs
fi

# Fix data directory
if [ -d "/app/data" ]; then
    chmod -R 777 /app/data 2>/dev/null || true
fi

echo "[Entrypoint] Permissions fixed"

# Run the main command as appuser
exec gosu appuser "$@"
