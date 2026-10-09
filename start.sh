#!/usr/bin/env bash
set -e

echo "============================================="
echo " Starting Urumi AI Platform Development Mesh "
echo "============================================="

if [ ! -f ".env" ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
fi

echo "Building and launching Docker Compose containers..."
docker compose up --build
