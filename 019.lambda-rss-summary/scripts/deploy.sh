#!/bin/bash
# Script to prepare Lambda deployment package with dependencies

# Exit on error
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BUILD_DIR="${SCRIPT_DIR}/build"
PACKAGE_DIR="${SCRIPT_DIR}/package"
ZIP_FILE="${SCRIPT_DIR}/lambda_function.zip"

echo "Cleaning up previous builds..."
rm -rf "${BUILD_DIR}" "${PACKAGE_DIR}" "${ZIP_FILE}"

echo "Creating build directories..."
mkdir -p "${BUILD_DIR}"
mkdir -p "${PACKAGE_DIR}"

echo "Installing dependencies..."
pip install -r "${SCRIPT_DIR}/requirements.txt" -t "${PACKAGE_DIR}"

echo "Copying Lambda function code..."
cp "${SCRIPT_DIR}/lambda_function.py" "${PACKAGE_DIR}/"

echo "Creating deployment package..."
cd "${PACKAGE_DIR}"
zip -r "${ZIP_FILE}" ./*

echo "Cleaning up build artifacts..."
rm -rf "${BUILD_DIR}" "${PACKAGE_DIR}"

echo "Deployment package created at: ${ZIP_FILE}"
echo "You can now deploy using AWS CLI or CloudFormation."