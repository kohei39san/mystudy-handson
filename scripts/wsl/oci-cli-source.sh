#!/bin/bash
# Usage: ./oci-cli-source.sh <region> <profile-name>

REGION="$1"
PROFILE_NAME="$2"

oci session authenticate --region "$REGION" --profile-name "$PROFILE_NAME"