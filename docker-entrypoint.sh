#!/bin/bash
set -e

# Fix permissions on universe domain files
# This runs as root before switching to appuser
if [ -d "/app/universes" ]; then
    echo "[Entrypoint] Fixing permissions on domain files..."

    # Fix all JSON files (except large embeddings)
    find /app/universes -name "*.json" ! -name "embeddings.json" -exec chmod 666 {} \; 2>/dev/null || true

    # Fix directory permissions
    find /app/universes -type d -exec chmod 777 {} \; 2>/dev/null || true

    echo "[Entrypoint] Permissions fixed"
fi

# Run the main command as appuser
exec gosu appuser "$@"
