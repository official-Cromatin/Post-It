#!/bin/bash
set -e

echo "=== Starting Renovate Bot ==="

apt update
apt install -y build-essential libpq-dev

runuser -u ubuntu renovate --platform=github

echo "=== Renovate Bot finished ==="
