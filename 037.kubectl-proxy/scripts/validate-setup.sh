#!/bin/bash
# Test script for Ansible and kubectl-proxy setup validation

set -e

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=== kubectl-proxy Ansible Setup Validation ==="
echo "Project directory: $PROJECT_DIR"
echo ""

# Check directory structure
echo "1. Checking directory structure..."
if [ -d "$PROJECT_DIR/ansible" ]; then
    echo "   ✓ ansible directory exists"
else
    echo "   ✗ ansible directory missing"
    exit 1
fi

if [ -d "$PROJECT_DIR/ansible/inventories" ]; then
    echo "   ✓ inventories directory exists"
else
    echo "   ✗ inventories directory missing"
    exit 1
fi

# Check required files
echo ""
echo "2. Checking required files..."
REQUIRED_FILES=(
    "ansible/ansible.cfg"
    "ansible/inventories/hosts"
    "ansible/create-custom-resources.yml"
    "ansible/delete-custom-resources.yml"
    "scripts/generate-certs.sh"
    "scripts/start-https-proxy.sh"
    "docker-compose.yml"
    ".env.example"
)

cd "$PROJECT_DIR"
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✓ $file"
    else
        echo "   ✗ $file missing"
        exit 1
    fi
done

# Check script permissions
echo ""
echo "3. Checking script permissions..."
for script in scripts/*.sh; do
    if [ -x "$script" ]; then
        echo "   ✓ $script is executable"
    else
        echo "   ✗ $script is not executable"
        exit 1
    fi
done

# Validate YAML syntax
echo ""
echo "4. Validating YAML syntax..."
python3 -c "import yaml; yaml.safe_load(open('ansible/create-custom-resources.yml'))" && \
    echo "   ✓ create-custom-resources.yml is valid"
python3 -c "import yaml; yaml.safe_load(open('ansible/delete-custom-resources.yml'))" && \
    echo "   ✓ delete-custom-resources.yml is valid"
python3 -c "import yaml; yaml.safe_load(open('docker-compose.yml'))" && \
    echo "   ✓ docker-compose.yml is valid"

# Check docker-compose services
echo ""
echo "5. Checking docker-compose services..."
if grep -q "kubectl-proxy:" docker-compose.yml; then
    echo "   ✓ kubectl-proxy service found"
else
    echo "   ✗ kubectl-proxy service missing"
    exit 1
fi

if grep -q "kubectl-proxy-https:" docker-compose.yml; then
    echo "   ✓ kubectl-proxy-https service found"
else
    echo "   ✗ kubectl-proxy-https service missing"
    exit 1
fi

if grep -q "ansible:" docker-compose.yml; then
    echo "   ✓ ansible service found"
else
    echo "   ✗ ansible service missing"
    exit 1
fi

# Check environment variables in .env.example
echo ""
echo "6. Checking environment variables..."
REQUIRED_VARS=(
    "PROXY_URL"
    "PROXY_PROTOCOL"
    "ENABLE_HTTPS"
    "HTTPS_PORT"
    "CRD_GROUP"
    "CRD_VERSION"
    "RESOURCE_NAME"
    "RESOURCE_NAMESPACE"
    "VALIDATE_CERTS"
)

for var in "${REQUIRED_VARS[@]}"; do
    if grep -q "^$var=" .env.example || grep -q "^# $var=" .env.example; then
        echo "   ✓ $var defined in .env.example"
    else
        echo "   ✗ $var missing from .env.example"
        exit 1
    fi
done

# Check Ansible playbook content
echo ""
echo "7. Checking Ansible playbook features..."
if grep -q "uri:" ansible/create-custom-resources.yml; then
    echo "   ✓ Playbook uses uri module (curl equivalent)"
else
    echo "   ✗ uri module not found in playbook"
    exit 1
fi

if grep -q "validate_certs:" ansible/create-custom-resources.yml; then
    echo "   ✓ Playbook supports certificate validation"
else
    echo "   ✗ Certificate validation handling missing"
    exit 1
fi

if grep -q "proxy_protocol" ansible/create-custom-resources.yml; then
    echo "   ✓ Playbook supports HTTP/HTTPS protocol switching"
else
    echo "   ✗ Protocol switching not found"
    exit 1
fi

echo ""
echo "=== All validation checks passed! ==="
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env and customize settings"
echo "2. Start services: docker compose up -d"
echo "3. For HTTPS: docker compose --profile https up -d"
echo "4. Generate CRD: docker compose exec kubectl-proxy ./scripts/manage-crd.sh generate"
echo "5. Install CRD: docker compose exec kubectl-proxy ./scripts/manage-crd.sh install"
echo "6. Run Ansible: docker compose exec ansible ansible-playbook create-custom-resources.yml"
