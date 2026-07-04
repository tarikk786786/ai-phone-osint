#!/usr/bin/env bash
set -euo pipefail

# ═══════════════════════════════════════════════════════
# AI Phone Intelligence OSINT Platform — Setup Script
# ═══════════════════════════════════════════════════════

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "╔═══════════════════════════════════════════════╗"
echo "║   AI Phone Intelligence OSINT Platform        ║"
echo "║   Setup & Installation                        ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""

# ── Prerequisites ──────────────────────────────────────
echo "🔍 Checking prerequisites..."

command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is required but not installed."; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required but not installed."; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "❌ npm is required but not installed."; exit 1; }

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
NODE_VERSION=$(node --version 2>&1)
echo "   ✓ Python $PYTHON_VERSION"
echo "   ✓ Node $NODE_VERSION"
echo ""

# ── Environment ────────────────────────────────────────
echo "📝 Setting up environment..."
if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo "   ✓ Created backend/.env from .env.example"
    echo "   ⚠️  Edit backend/.env to add your API keys"
else
    echo "   ✓ backend/.env already exists"
fi

if [ ! -f frontend/.env.local ]; then
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > frontend/.env.local
    echo "   ✓ Created frontend/.env.local"
fi

# ── Backend Setup ──────────────────────────────────────
echo ""
echo "🐍 Setting up Python backend..."
cd backend

if [ ! -d venv ]; then
    python3 -m venv venv
    echo "   ✓ Created Python virtual environment"
fi

source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "   ✓ Installed Python dependencies"

cd "$SCRIPT_DIR"

# ── Frontend Setup ─────────────────────────────────────
echo ""
echo "⚛️  Setting up Next.js frontend..."
cd frontend

if [ ! -d node_modules ]; then
    npm install --silent 2>/dev/null || npm install
    echo "   ✓ Installed Node.js dependencies"
else
    echo "   ✓ node_modules already exists (use 'npm install' to update)"
fi

cd "$SCRIPT_DIR"

# ── Docker (optional) ──────────────────────────────────
echo ""
echo "🐳 Docker setup (optional)..."
if command -v docker >/dev/null 2>&1 && command -v docker-compose >/dev/null 2>&1; then
    echo "   ✓ Docker is available"
    echo "   Run 'docker-compose up -d' to start all services"
else
    echo "   ⚠️  Docker not found — skipping (install Docker for containerized setup)"
fi

# ── Complete ───────────────────────────────────────────
echo ""
echo "╔═══════════════════════════════════════════════╗"
echo "║   ✅ Setup complete!                          ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""
echo "  Backend:"
echo "    cd backend && source venv/bin/activate"
echo "    uvicorn app.main:app --reload --port 8000"
echo ""
echo "  Frontend:"
echo "    cd frontend && npm run dev"
echo ""
echo "  Docker (all services):"
echo "    docker-compose up -d"
echo ""
echo "  Open http://localhost:3000 in your browser"
echo ""
