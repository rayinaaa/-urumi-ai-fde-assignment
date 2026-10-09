# PowerShell Quickstart Script for Urumi AI Platform
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host " Starting Urumi AI Platform Development Mesh " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

if (-not (Test-Path ".env")) {
    Write-Host "Creating .env from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
}

Write-Host "Building and launching Docker Compose containers..." -ForegroundColor Green
docker compose up --build
