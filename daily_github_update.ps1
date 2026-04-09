param(
    [string]$Message = ""
)

Write-Host ""
Write-Host "==============================================="
Write-Host " EnergyTrack Daily GitHub Update"
Write-Host "==============================================="
Write-Host ""

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "Git is not installed or not in PATH." -ForegroundColor Red
    Write-Host "Install Git from: https://git-scm.com/download/win"
    exit 1
}

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

$insideRepo = git rev-parse --is-inside-work-tree 2>$null
if ($LASTEXITCODE -ne 0 -or $insideRepo -ne "true") {
    Write-Host "This folder is not a Git repository." -ForegroundColor Red
    Write-Host "Run: git init"
    exit 1
}

$branch = git branch --show-current
if ([string]::IsNullOrWhiteSpace($branch)) {
    $branch = "main"
}

Write-Host "Current branch: $branch"
Write-Host ""
Write-Host "Current changes:"
& git status --short
Write-Host ""

if ([string]::IsNullOrWhiteSpace($Message)) {
    $Message = Read-Host "Enter commit message (example: docs: update README)"
}

if ([string]::IsNullOrWhiteSpace($Message)) {
    Write-Host "Commit message is required." -ForegroundColor Red
    exit 1
}

& git add .
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to stage files." -ForegroundColor Red
    exit 1
}

& git commit -m $Message
if ($LASTEXITCODE -ne 0) {
    Write-Host "Commit failed (nothing to commit or another error)." -ForegroundColor Yellow
    exit 1
}

& git push origin $branch
if ($LASTEXITCODE -ne 0) {
    Write-Host "Push failed. Check remote/authentication and retry." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Update pushed successfully to origin/$branch" -ForegroundColor Green
