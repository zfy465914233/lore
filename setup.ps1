<#
.SYNOPSIS
    Scholar Agent setup script for Windows.
.DESCRIPTION
    Checks prerequisites, installs dependencies, and runs 'scholar-agent init'
    to create data directories and register the MCP server.
.EXAMPLE
    .\setup.ps1
#>

$ErrorActionPreference = "Stop"

Write-Host "=== Scholar Agent Setup (Windows) ===" -ForegroundColor Cyan
Write-Host ""

# --- Step 0: Check Python ---
Write-Host "[0/4] Checking prerequisites..." -ForegroundColor Yellow

$pythonCmd = $null
foreach ($cmd in @("python", "python3", "py")) {
    if (Get-Command $cmd -ErrorAction SilentlyContinue) {
        $pythonCmd = $cmd
        break
    }
}

if (-not $pythonCmd) {
    Write-Host "ERROR: Python 3.10+ not found." -ForegroundColor Red
    Write-Host "  Install from: https://www.python.org/downloads/" -ForegroundColor Red
    Write-Host "  Make sure to check 'Add Python to PATH' during installation." -ForegroundColor Red
    exit 1
}

$pyVersion = & $pythonCmd --version 2>&1
Write-Host "  Python: $pyVersion" -ForegroundColor Green

# --- Step 1: Check poppler ---
Write-Host "[1/4] Checking system dependencies..." -ForegroundColor Yellow

if (Get-Command pdftotext -ErrorAction SilentlyContinue) {
    Write-Host "  poppler: OK" -ForegroundColor Green
} else {
    Write-Host "  poppler: NOT FOUND (optional, for PDF text extraction)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Install via one of:" -ForegroundColor Yellow
    Write-Host "    winget install poppler"
    Write-Host "    choco install poppler"
    Write-Host "    Or download from: https://github.com/oschwartz10612/poppler-windows/releases"
    Write-Host ""

    $response = Read-Host "  Try to install via winget? (y/N)"
    if ($response -eq "y" -or $response -eq "Y") {
        if (Get-Command winget -ErrorAction SilentlyContinue) {
            winget install --id poppler --accept-source-agreements --accept-package-agreements
        } else {
            Write-Host "  winget not available. Please install poppler manually." -ForegroundColor Yellow
        }
    }
}

# --- Step 2: Install scholar-agent ---
Write-Host "[2/4] Installing scholar-agent..." -ForegroundColor Yellow

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (Test-Path (Join-Path $scriptDir "pyproject.toml")) {
    # Running from source (git clone)
    Write-Host "  Installing from source (editable mode)..." -ForegroundColor Gray
    & $pythonCmd -m pip install -e $scriptDir --quiet 2>$null
    if ($LASTEXITCODE -ne 0) {
        & $pythonCmd -m pip install -e $scriptDir
    }
} else {
    Write-Host "ERROR: setup.ps1 must be run from the scholar-agent source directory." -ForegroundColor Red
    Write-Host "  git clone https://github.com/zfy465914233/scholar-agent.git" -ForegroundColor Gray
    Write-Host "  cd scholar-agent" -ForegroundColor Gray
    Write-Host "  .\setup.ps1" -ForegroundColor Gray
    exit 1
}

# --- Step 3: Run scholar-agent init ---
Write-Host "[3/4] Running 'scholar-agent init'..." -ForegroundColor Yellow
Write-Host ""

& $pythonCmd -m scholar_agent.cli init --format text

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "  'scholar-agent init' failed. Try running manually:" -ForegroundColor Yellow
    Write-Host "    scholar-agent init --skip-register" -ForegroundColor Gray
    Write-Host "    scholar-agent install claude --write" -ForegroundColor Gray
}

# --- Step 4: Done ---
Write-Host "[4/4] Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Data directory: $HOME\scholar\" -ForegroundColor Cyan
Write-Host "  knowledge\     - Your knowledge cards"
Write-Host "  paper-notes\   - Paper analysis notes"
Write-Host "  indexes\       - Search index"
Write-Host ""
Write-Host "CLI commands:" -ForegroundColor Cyan
Write-Host "  scholar-agent doctor          - Check environment"
Write-Host "  scholar-agent config show     - Show resolved config"
Write-Host "  scholar-agent install claude  - Register with Claude Code"
Write-Host "  scholar-agent install vscode  - Register with VS Code Copilot"
Write-Host ""
