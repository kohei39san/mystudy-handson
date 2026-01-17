#!/bin/bash

# Login and call /user endpoint test script

set -e

# Default values
API_ENDPOINT="${API_ENDPOINT:-}"
USERNAME="${USERNAME:-testuser}"
PASSWORD="${PASSWORD:-}"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --api-endpoint)
      API_ENDPOINT="$2"
      shift 2
      ;;
    --username)
      USERNAME="$2"
      shift 2
      ;;
    --password)
      PASSWORD="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Validate required parameters
if [ -z "$API_ENDPOINT" ]; then
  echo "Error: --api-endpoint is required"
  echo "Usage: $0 --api-endpoint <API_ENDPOINT> --username <USERNAME> --password <PASSWORD>"
  exit 1
fi

if [ -z "$PASSWORD" ]; then
  echo "Error: --password is required"
  exit 1
fi

echo "=== Login Test ==="
echo "API Endpoint: $API_ENDPOINT"
echo "Username: $USERNAME"

# Login and capture response with headers
LOGIN_RESPONSE=$(curl -s -i -X POST "$API_ENDPOINT/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}")

# Extract access token from Authorization header or x-amzn-remapped-authorization header
ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | grep -iE "^(Authorization|x-amzn-remapped-authorization):" | sed 's/^[^:]*: //i' | tr -d '\r')

if [ -z "$ACCESS_TOKEN" ]; then
  echo "Error: Failed to get access token"
  echo "$LOGIN_RESPONSE"
  exit 1
fi

echo "✓ Login successful"
echo "Access Token: ${ACCESS_TOKEN:0:50}..."

# Call /user endpoint with access token
echo ""
echo "=== Calling /user endpoint ==="
USER_RESPONSE=$(curl -s -X GET "$API_ENDPOINT/user?filter=test&limit=5" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "Response:"
echo "$USER_RESPONSE" | jq '.' 2>/dev/null || echo "$USER_RESPONSE"

echo ""
echo "✓ Test completed successfully"
