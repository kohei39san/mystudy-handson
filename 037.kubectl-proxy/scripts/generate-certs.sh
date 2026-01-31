#!/bin/sh
# Generate self-signed certificates for HTTPS support in kubectl-proxy

set -e

CERT_DIR="${CERT_DIR:-/tmp/certs}"
CERT_FILE="${CERT_DIR}/server.crt"
KEY_FILE="${CERT_DIR}/server.key"

echo "=== Generating self-signed certificates for HTTPS ==="

# Create certificate directory
mkdir -p ${CERT_DIR}

# Generate private key and self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ${KEY_FILE} \
    -out ${CERT_FILE} \
    -subj "/C=JP/ST=Tokyo/L=Tokyo/O=kubectl-proxy/CN=kubectl-proxy" \
    -addext "subjectAltName=DNS:kubectl-proxy,DNS:localhost,IP:127.0.0.1"

# Set appropriate permissions
chmod 600 ${KEY_FILE}
chmod 644 ${CERT_FILE}

echo "✓ Certificates generated successfully:"
echo "  Certificate: ${CERT_FILE}"
echo "  Private Key: ${KEY_FILE}"
echo ""
echo "Certificate details:"
openssl x509 -in ${CERT_FILE} -text -noout | grep -E "Subject:|Issuer:|Not Before|Not After|DNS:"
