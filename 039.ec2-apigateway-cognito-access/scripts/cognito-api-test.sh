#!/bin/bash

# Cognito API Gateway Testing Script
# This script authenticates with AWS Cognito and tests API Gateway endpoints

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/config.env"
TOKEN_FILE="${SCRIPT_DIR}/.tokens"
LOG_FILE="${SCRIPT_DIR}/api-test.log"

# Default values
DEFAULT_REGION="us-east-1"
DEFAULT_TIMEOUT=30

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

# Print colored output
print_status() {
    local color="$1"
    shift
    echo -e "${color}$*${NC}"
}

# Show usage information
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS] [COMMAND]

Cognito API Gateway Testing Script

COMMANDS:
    auth                    Authenticate with Cognito and save tokens
    test                    Run API tests (authenticates first if needed)
    refresh                 Refresh access token using refresh token
    clean                   Clean stored tokens and logs
    help                    Show this help message

OPTIONS:
    -c, --config FILE       Configuration file (default: config.env)
    -u, --username USER     Cognito username (overrides config)
    -p, --password PASS     Cognito password (overrides config)
    -a, --api-url URL       API Gateway URL (overrides config)
    -r, --region REGION     AWS region (default: us-east-1)
    -v, --verbose           Enable verbose output
    -h, --help              Show this help message

EXAMPLES:
    $0 auth                                 # Authenticate with config file
    $0 test                                 # Run full test suite
    $0 -u user@example.com -p pass auth     # Auth with specific credentials
    $0 -a https://api.example.com test      # Test specific API URL

CONFIGURATION:
    Create a config.env file with the following variables:
    COGNITO_USER_POOL_ID="your-user-pool-id"
    COGNITO_CLIENT_ID="your-client-id"
    COGNITO_REGION="us-east-1"
    API_GATEWAY_URL="https://your-api.execute-api.region.amazonaws.com/stage"
    COGNITO_USERNAME="your-email@example.com"
    COGNITO_PASSWORD="your-password"

EOF
}

# Load configuration
load_config() {
    if [[ -f "$CONFIG_FILE" ]]; then
        log "INFO" "Loading configuration from $CONFIG_FILE"
        # shellcheck source=/dev/null
        source "$CONFIG_FILE"
    else
        log "WARN" "Configuration file $CONFIG_FILE not found"
    fi

    # Validate required variables
    local missing_vars=()
    [[ -z "${COGNITO_USER_POOL_ID:-}" ]] && missing_vars+=("COGNITO_USER_POOL_ID")
    [[ -z "${COGNITO_CLIENT_ID:-}" ]] && missing_vars+=("COGNITO_CLIENT_ID")
    [[ -z "${API_GATEWAY_URL:-}" ]] && missing_vars+=("API_GATEWAY_URL")
    [[ -z "${COGNITO_USERNAME:-}" ]] && missing_vars+=("COGNITO_USERNAME")
    [[ -z "${COGNITO_PASSWORD:-}" ]] && missing_vars+=("COGNITO_PASSWORD")

    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        print_status "$RED" "Error: Missing required configuration variables:"
        printf '%s\n' "${missing_vars[@]}"
        echo
        show_usage
        exit 1
    fi

    # Set defaults
    COGNITO_REGION="${COGNITO_REGION:-$DEFAULT_REGION}"
    TIMEOUT="${TIMEOUT:-$DEFAULT_TIMEOUT}"
}

# Save tokens to file
save_tokens() {
    local access_token="$1"
    local id_token="$2"
    local refresh_token="$3"
    local expires_in="$4"
    
    local expires_at=$(($(date +%s) + expires_in - 300)) # 5 min buffer
    
    cat > "$TOKEN_FILE" << EOF
ACCESS_TOKEN="$access_token"
ID_TOKEN="$id_token"
REFRESH_TOKEN="$refresh_token"
EXPIRES_AT="$expires_at"
EOF
    
    chmod 600 "$TOKEN_FILE"
    log "INFO" "Tokens saved to $TOKEN_FILE"
}

# Load tokens from file
load_tokens() {
    if [[ -f "$TOKEN_FILE" ]]; then
        # shellcheck source=/dev/null
        source "$TOKEN_FILE"
        
        local current_time=$(date +%s)
        if [[ -n "${EXPIRES_AT:-}" ]] && [[ $current_time -lt $EXPIRES_AT ]]; then
            log "INFO" "Loaded valid tokens from $TOKEN_FILE"
            return 0
        else
            log "WARN" "Tokens have expired"
            return 1
        fi
    else
        log "WARN" "No token file found"
        return 1
    fi
}

# Authenticate with Cognito
authenticate() {
    print_status "$BLUE" "Authenticating with Cognito..."
    log "INFO" "Starting authentication for user: $COGNITO_USERNAME"
    
    local auth_response
    auth_response=$(aws cognito-idp admin-initiate-auth \
        --user-pool-id "$COGNITO_USER_POOL_ID" \
        --client-id "$COGNITO_CLIENT_ID" \
        --auth-flow ADMIN_USER_PASSWORD_AUTH \
        --auth-parameters "USERNAME=$COGNITO_USERNAME,PASSWORD=$COGNITO_PASSWORD" \
        --region "$COGNITO_REGION" \
        --output json 2>/dev/null) || {
        
        print_status "$RED" "Authentication failed with ADMIN_USER_PASSWORD_AUTH, trying ADMIN_NO_SRP_AUTH..."
        auth_response=$(aws cognito-idp admin-initiate-auth \
            --user-pool-id "$COGNITO_USER_POOL_ID" \
            --client-id "$COGNITO_CLIENT_ID" \
            --auth-flow ADMIN_NO_SRP_AUTH \
            --auth-parameters "USERNAME=$COGNITO_USERNAME,PASSWORD=$COGNITO_PASSWORD" \
            --region "$COGNITO_REGION" \
            --output json) || {
            print_status "$RED" "Authentication failed!"
            log "ERROR" "Both authentication flows failed"
            return 1
        }
    }
    
    # Check for challenges
    local challenge_name
    challenge_name=$(echo "$auth_response" | jq -r '.ChallengeName // empty')
    
    if [[ -n "$challenge_name" ]]; then
        print_status "$YELLOW" "Challenge required: $challenge_name"
        if [[ "$challenge_name" == "NEW_PASSWORD_REQUIRED" ]]; then
            print_status "$RED" "New password required. Please set a permanent password first."
            log "ERROR" "NEW_PASSWORD_REQUIRED challenge encountered"
            return 1
        fi
    fi
    
    # Extract tokens
    local access_token id_token refresh_token expires_in
    access_token=$(echo "$auth_response" | jq -r '.AuthenticationResult.AccessToken')
    id_token=$(echo "$auth_response" | jq -r '.AuthenticationResult.IdToken')
    refresh_token=$(echo "$auth_response" | jq -r '.AuthenticationResult.RefreshToken')
    expires_in=$(echo "$auth_response" | jq -r '.AuthenticationResult.ExpiresIn')
    
    if [[ "$access_token" == "null" ]] || [[ -z "$access_token" ]]; then
        print_status "$RED" "Failed to extract access token from response"
        log "ERROR" "Invalid authentication response"
        return 1
    fi
    
    # Save tokens
    save_tokens "$access_token" "$id_token" "$refresh_token" "$expires_in"
    
    # Set global variables
    ACCESS_TOKEN="$access_token"
    ID_TOKEN="$id_token"
    REFRESH_TOKEN="$refresh_token"
    
    print_status "$GREEN" "Authentication successful!"
    log "INFO" "Authentication completed successfully"
    return 0
}

# Refresh access token
refresh_token() {
    if [[ -z "${REFRESH_TOKEN:-}" ]]; then
        log "ERROR" "No refresh token available"
        return 1
    fi
    
    print_status "$BLUE" "Refreshing access token..."
    log "INFO" "Refreshing access token"
    
    local refresh_response
    refresh_response=$(aws cognito-idp admin-initiate-auth \
        --user-pool-id "$COGNITO_USER_POOL_ID" \
        --client-id "$COGNITO_CLIENT_ID" \
        --auth-flow REFRESH_TOKEN_AUTH \
        --auth-parameters "REFRESH_TOKEN=$REFRESH_TOKEN" \
        --region "$COGNITO_REGION" \
        --output json) || {
        print_status "$RED" "Token refresh failed!"
        log "ERROR" "Token refresh failed"
        return 1
    }
    
    # Extract new tokens
    local new_access_token new_id_token expires_in
    new_access_token=$(echo "$refresh_response" | jq -r '.AuthenticationResult.AccessToken')
    new_id_token=$(echo "$refresh_response" | jq -r '.AuthenticationResult.IdToken')
    expires_in=$(echo "$refresh_response" | jq -r '.AuthenticationResult.ExpiresIn')
    
    # Save updated tokens (keep existing refresh token)
    save_tokens "$new_access_token" "$new_id_token" "$REFRESH_TOKEN" "$expires_in"
    
    # Update global variables
    ACCESS_TOKEN="$new_access_token"
    ID_TOKEN="$new_id_token"
    
    print_status "$GREEN" "Token refresh successful!"
    log "INFO" "Token refresh completed successfully"
    return 0
}

# Make API call
make_api_call() {
    local method="$1"
    local path="$2"
    local data="${3:-}"
    local extra_headers="${4:-}"
    
    local url="${API_GATEWAY_URL%/}${path}"
    local headers=()
    
    # Add authorization header (use ID token for API Gateway)
    headers+=("-H" "Authorization: Bearer $ID_TOKEN")
    headers+=("-H" "Content-Type: application/json")
    
    # Add custom headers if provided
    if [[ -n "$extra_headers" ]]; then
        while IFS= read -r header; do
            [[ -n "$header" ]] && headers+=("-H" "$header")
        done <<< "$extra_headers"
    fi
    
    print_status "$BLUE" "Making $method request to: $url"
    log "INFO" "API call: $method $url"
    
    local curl_args=()
    curl_args+=("-X" "$method")
    curl_args+=("${headers[@]}")
    curl_args+=("-w" "\nHTTP Status: %{http_code}\nTime: %{time_total}s\n")
    curl_args+=("--connect-timeout" "$TIMEOUT")
    curl_args+=("--max-time" "$((TIMEOUT * 2))")
    curl_args+=("-s")
    
    if [[ -n "$data" ]]; then
        curl_args+=("-d" "$data")
        log "INFO" "Request body: $data"
    fi
    
    curl_args+=("$url")
    
    local response
    response=$(curl "${curl_args[@]}") || {
        print_status "$RED" "API call failed!"
        log "ERROR" "curl command failed"
        return 1
    }
    
    echo "$response"
    log "INFO" "API response: $response"
    return 0
}

# Run API test suite
run_tests() {
    print_status "$BLUE" "Running API test suite..."
    log "INFO" "Starting API test suite"
    
    # Ensure we have valid tokens
    if ! load_tokens; then
        if ! authenticate; then
            print_status "$RED" "Cannot proceed without authentication"
            return 1
        fi
    fi
    
    local test_count=0
    local success_count=0
    
    # Test 1: Simple GET request
    print_status "$YELLOW" "\nTest 1: Simple GET request"
    ((test_count++))
    if make_api_call "GET" "/"; then
        ((success_count++))
        print_status "$GREEN" "✓ Test 1 passed"
    else
        print_status "$RED" "✗ Test 1 failed"
    fi
    
    # Test 2: GET with query parameters
    print_status "$YELLOW" "\nTest 2: GET with query parameters"
    ((test_count++))
    if make_api_call "GET" "/?param1=value1&param2=value2"; then
        ((success_count++))
        print_status "$GREEN" "✓ Test 2 passed"
    else
        print_status "$RED" "✗ Test 2 failed"
    fi
    
    # Test 3: POST with JSON data
    print_status "$YELLOW" "\nTest 3: POST with JSON data"
    ((test_count++))
    local test_data='{"message":"Hello from bash script","timestamp":"'$(date -Iseconds)'","test_id":"bash-test-001"}'
    if make_api_call "POST" "/test" "$test_data"; then
        ((success_count++))
        print_status "$GREEN" "✓ Test 3 passed"
    else
        print_status "$RED" "✗ Test 3 failed"
    fi
    
    # Test 4: PUT request
    print_status "$YELLOW" "\nTest 4: PUT request"
    ((test_count++))
    local update_data='{"action":"update","resource_id":"12345","changes":["field1","field2"]}'
    if make_api_call "PUT" "/resource/12345" "$update_data"; then
        ((success_count++))
        print_status "$GREEN" "✓ Test 4 passed"
    else
        print_status "$RED" "✗ Test 4 failed"
    fi
    
    # Test 5: Custom headers
    print_status "$YELLOW" "\nTest 5: Request with custom headers"
    ((test_count++))
    local custom_headers="X-Custom-Header: test-value"$'\n'"X-Request-ID: bash-req-12345"
    if make_api_call "GET" "/custom" "" "$custom_headers"; then
        ((success_count++))
        print_status "$GREEN" "✓ Test 5 passed"
    else
        print_status "$RED" "✗ Test 5 failed"
    fi
    
    # Summary
    print_status "$BLUE" "\n=== Test Summary ==="
    print_status "$BLUE" "Total tests: $test_count"
    print_status "$GREEN" "Passed: $success_count"
    print_status "$RED" "Failed: $((test_count - success_count))"
    
    if [[ $success_count -eq $test_count ]]; then
        print_status "$GREEN" "All tests passed! ✓"
        log "INFO" "All tests completed successfully"
        return 0
    else
        print_status "$YELLOW" "Some tests failed. Check the logs for details."
        log "WARN" "Some tests failed: $((test_count - success_count))/$test_count"
        return 1
    fi
}

# Clean up tokens and logs
clean_up() {
    print_status "$BLUE" "Cleaning up tokens and logs..."
    [[ -f "$TOKEN_FILE" ]] && rm -f "$TOKEN_FILE" && echo "Removed token file"
    [[ -f "$LOG_FILE" ]] && rm -f "$LOG_FILE" && echo "Removed log file"
    print_status "$GREEN" "Cleanup completed"
}

# Main function
main() {
    local command=""
    local verbose=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -c|--config)
                CONFIG_FILE="$2"
                shift 2
                ;;
            -u|--username)
                COGNITO_USERNAME="$2"
                shift 2
                ;;
            -p|--password)
                COGNITO_PASSWORD="$2"
                shift 2
                ;;
            -a|--api-url)
                API_GATEWAY_URL="$2"
                shift 2
                ;;
            -r|--region)
                COGNITO_REGION="$2"
                shift 2
                ;;
            -v|--verbose)
                verbose=true
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            auth|test|refresh|clean|help)
                command="$1"
                shift
                ;;
            *)
                echo "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Set verbose mode
    if [[ "$verbose" == true ]]; then
        set -x
    fi
    
    # Default command
    if [[ -z "$command" ]]; then
        command="help"
    fi
    
    # Load configuration (except for help and clean commands)
    if [[ "$command" != "help" && "$command" != "clean" ]]; then
        load_config
    fi
    
    # Execute command
    case "$command" in
        auth)
            authenticate
            ;;
        test)
            run_tests
            ;;
        refresh)
            load_tokens && refresh_token
            ;;
        clean)
            clean_up
            ;;
        help)
            show_usage
            ;;
        *)
            echo "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
