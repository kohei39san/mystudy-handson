#!/bin/sh
# Start HTTPS proxy for kubectl-proxy
# This script wraps the HTTP kubectl-proxy with an HTTPS layer using socat

set -e

# .envファイルがマウントされている場合は読み込み（オプション）
if [ -f "/.env" ]; then
    echo "Loading .env file..."
    set -a
    . /.env
    set +a
fi

# 環境変数のデフォルト値設定
PROXY_PORT=${PROXY_PORT:-"8001"}
HTTPS_PORT=${HTTPS_PORT:-"8443"}
ENABLE_HTTPS=${ENABLE_HTTPS:-"false"}
CERT_DIR=${CERT_DIR:-"/tmp/certs"}
CERT_FILE="${CERT_DIR}/server.crt"
KEY_FILE="${CERT_DIR}/server.key"

echo "=== HTTPS Proxy Configuration ==="
echo "  ENABLE_HTTPS: ${ENABLE_HTTPS}"
echo "  HTTP Port: ${PROXY_PORT}"
echo "  HTTPS Port: ${HTTPS_PORT}"

if [ "${ENABLE_HTTPS}" = "true" ]; then
    echo "Starting HTTPS proxy..."
    
    # Check if certificates exist
    if [ ! -f "${CERT_FILE}" ] || [ ! -f "${KEY_FILE}" ]; then
        echo "Certificates not found. Generating self-signed certificates..."
        /scripts/generate-certs.sh
    fi
    
    # Install socat if not present (for Alpine-based images)
    if ! command -v socat > /dev/null 2>&1; then
        echo "Installing socat..."
        apk add --no-cache socat
    fi
    
    echo "Starting socat HTTPS wrapper on port ${HTTPS_PORT}..."
    echo "Forwarding HTTPS:${HTTPS_PORT} -> HTTP:kubectl-proxy:${PROXY_PORT}"
    
    # Start socat in background to wrap HTTP with HTTPS
    # Connect to kubectl-proxy service via Docker networking
    socat OPENSSL-LISTEN:${HTTPS_PORT},cert=${CERT_FILE},key=${KEY_FILE},verify=0,fork,reuseaddr TCP:kubectl-proxy:${PROXY_PORT} &
    SOCAT_PID=$!
    
    echo "✓ HTTPS proxy started (PID: ${SOCAT_PID})"
    echo "  Access via: https://localhost:${HTTPS_PORT}"
    echo "  (Self-signed certificate - you may need to accept security warnings)"
    
    # Keep script running
    wait ${SOCAT_PID}
else
    echo "HTTPS is disabled. Use ENABLE_HTTPS=true to enable."
    echo "HTTP proxy is available on port ${PROXY_PORT}"
    # Keep container running
    tail -f /dev/null
fi
