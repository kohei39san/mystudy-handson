#!/bin/bash

# API Integration Test Script
# Tests: Login, /public, /user, and /admin endpoints with different user roles

# Configuration
API_ENDPOINT="${API_ENDPOINT:-}"
TEST_USERNAME="${TEST_USERNAME:-testuser}"
TEST_PASSWORD="${TEST_PASSWORD:-}"
ADMIN_USERNAME="${ADMIN_USERNAME:-adminuser}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-}"

# Options
URLENCODE=true

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Helper function to print section headers
print_header() {
  echo ""
  echo -e "${BLUE}=== $1 ===${NC}"
}

# Helper function to print success
print_success() {
  echo -e "${GREEN}✓ $1${NC}"
}

# Helper function to print warning
print_warning() {
  echo -e "${YELLOW}⚠ $1${NC}"
}

# Helper function to print error
print_error() {
  echo -e "${RED}✗ $1${NC}"
}

# URL encode function
urlencode() {
  local string="$1"
  local strlen=${#string}
  local encoded=""
  local pos c o

  for (( pos=0 ; pos<strlen ; pos++ )); do
    c=${string:$pos:1}
    case "$c" in
      [-_.~a-zA-Z0-9] ) o="${c}" ;;
      * ) printf -v o '%%%02x' "'$c"
    esac
    encoded+="${o}"
  done
  echo "${encoded}"
}

# Helper function to test an endpoint
test_endpoint() {
  local method=$1
  local endpoint=$2
  local token=$3
  local description=$4
  
  echo ""
  echo -e "${BLUE}Testing ${method} ${endpoint}${NC}"
  echo -e "Description: ${description}"
  echo ""
  
  local curl_cmd="curl -s -v -w '\n%{http_code}' -X $method '$API_ENDPOINT$endpoint'"
  
  if [ -n "$token" ]; then
    curl_cmd="$curl_cmd -H 'Authorization: Bearer $token'"
  fi
  
  echo "Command:"
  echo "$curl_cmd"
  echo ""
  echo "Response:"
  echo "---"
  
  # Execute curl once and capture output
  local response
  if [ -z "$token" ]; then
    response=$(curl -s -i -w '\n%{http_code}' -X "$method" "$API_ENDPOINT$endpoint" 2>&1)
  else
    response=$(curl -s -i -w '\n%{http_code}' -X "$method" "$API_ENDPOINT$endpoint" \
      -H "Authorization: Bearer $token" 2>&1)
  fi
  
  echo "$response"
  echo "---"
}

# Authenticate a user and return the bearer token
authenticate() {
  local username=$1
  local password=$2
  local label=${3:-$username}
  print_header "Authenticating as $label" >&2
  local login_body="{\"username\":\"$username\",\"password\":\"$password\"}"
  echo "Request:" >&2
  echo "POST $API_ENDPOINT/auth/login" >&2
  echo "Content-Type: application/json" >&2
  echo "Body: $login_body" >&2
  echo "" >&2
  echo "Response:" >&2
  echo "---" >&2
  local login_response
  login_response=$(curl -s -i -X POST "$API_ENDPOINT/auth/login" \
    -H "Content-Type: application/json" \
    -d "$login_body" 2>&1)
  echo "$login_response" >&2
  echo "---" >&2
  local token
  token=$(echo "$login_response" | grep -iE "^(Authorization|x-amzn-remapped-authorization):" | head -1 | sed 's/^[^:]*: //i' | tr -d '\r')
  if [ -z "$token" ]; then
    print_error "Failed to get token for $label" >&2
    return 1
  fi
  print_success "Login successful for $label" >&2
  echo "$token"
}

# Set admin password to test password if not specified
if [ -z "$ADMIN_PASSWORD" ]; then
  ADMIN_PASSWORD="$TEST_PASSWORD"
fi

# Validate required parameters (via environment variables)
if [ -z "$API_ENDPOINT" ]; then
  print_error "Error: API_ENDPOINT is required"
  exit 1
fi

if [ -z "$TEST_PASSWORD" ]; then
  print_error "Error: TEST_PASSWORD is required"
  exit 1
fi

print_header "API Integration Test"
echo "API Endpoint: $API_ENDPOINT"
echo "Test User: $TEST_USERNAME"
echo "Admin User: $ADMIN_USERNAME"
echo "URL Encode: $URLENCODE"

# Test endpoints with test user
test_user_token=$(authenticate "$TEST_USERNAME" "$TEST_PASSWORD" "$TEST_USERNAME")
test_endpoint "GET" "/public" "" "Public endpoint (no authentication required)"
test_endpoint "GET" "/user?filter=test&limit=5" "$test_user_token" "User endpoint with test user token"

# Authenticate admin user
admin_token=$(authenticate "$ADMIN_USERNAME" "$ADMIN_PASSWORD" "$ADMIN_USERNAME")
test_endpoint "POST" "/admin" "$admin_token" "Admin endpoint with admin user token (should succeed)"

print_success "API Integration Tests Completed"