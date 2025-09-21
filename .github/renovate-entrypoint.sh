#!/bin/bash
set -euo pipefail

echo "=== Starting Renovate Bot ==="

cd /github/workspace

apt update
apt install -y build-essential libpq-dev

runuser -u ubuntu -- renovate --platform=github

echo "=== Renovate Bot finished ==="
