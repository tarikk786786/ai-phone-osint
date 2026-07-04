# ═══════════════════════════════════════════════════════
# AI Phone Intelligence OSINT Platform — Setup Script (Windows)
# ═══════════════════════════════════════════════════════

Write-Host "╔═══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   AI Phone Intelligence OSINT Platform        ║" -ForegroundColor Cyan
Write-Host "║   Setup & Installation (Windows)              ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ── Prerequisites ──────────────────────────────────────
Write-Host "🔍 Checking prerequisites..." -ForegroundColor Yellow

try { python --version | Out-Null } catch { Write-Host "❌ Python 3 is required but not installed." -ForegroundColor Red; exit 1 }
try { node --version | Out-Null } catch { Write-Host "❌ Node.js is required but not installed." -ForegroundColor Red; exit 1 }
try { npm --version | Out-Null } catch { Write-Host "❌ npm is required but not installed." -ForegroundColor Red; exit 1 }

Write-Host "   ✓ Python " (python --version) -ForegroundColor Green
Write-Host "   ✓ Node " (node --version) -ForegroundColor Green
Write-Host ""

# ── Environment ────────────────────────────────────────
Write-Host "📝 Setting up environment..." -ForegroundColor Yellow
if (-not (Test-Path "backend\.env")) {
    Copy-Item "backend\.env.example" "backend\.env"
    Write-Host "   ✓ Created backend\.env from .env.example" -ForegroundColor Green
    Write-Host "   ⚠️  Edit backend\.env to add your API keys" -ForegroundColor Yellow
}

if (-not (Test-Path "frontend\.env.local")) {
    "NEXT_PUBLIC_API_URL=http://localhost:8000" | Out-File -FilePath "frontend\.env.local"
    Write-Host "   ✓ Created frontend\.env.local" -ForegroundColor Green
}

# ── Backend Setup ──────────────────────────────────────
Write-Host ""
Write-Host "🐍 Setting up Python backend..." -ForegroundColor Yellow
Set-Location backend

if (-not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "   ✓ Created Python virtual environment" -ForegroundColor Green
}

# Activate and install
$venvActivate = ".\venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    & $venvActivate
    python -m pip install -q --upgrade pip
    pip install -q -r requirements.txt
    Write-Host "   ✓ Installed Python dependencies" -ForegroundColor Green
    deactivate
}

Set-Location ..

# ── Frontend Setup ─────────────────────────────────────
Write-Host ""
Write-Host "⚛️  Setting up Next.js frontend..." -ForegroundColor Yellow
Set-Location frontend

if (-not (Test-Path "node_modules")) {
    npm install --silent 2>$null
    if ($LASTEXITCODE -ne 0) { npm install }
    Write-Host "   ✓ Installed Node.js dependencies" -ForegroundColor Green
}

Set-Location ..

# ── Complete ───────────────────────────────────────────
Write-Host ""
Write-Host "╔═══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   ✅ Setup complete!                          ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Backend:" -ForegroundColor White
Write-Host "    cd backend && .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "    uvicorn app.main:app --reload --port 8000" -ForegroundColor Gray
Write-Host ""
Write-Host "  Frontend:" -ForegroundColor White
Write-Host "    cd frontend && npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "  Docker (all services):" -ForegroundColor White
Write-Host "    docker-compose up -d" -ForegroundColor Gray
Write-Host ""
Write-Host "  Open http://localhost:3000 in your browser" -ForegroundColor White
