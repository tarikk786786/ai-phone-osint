# AI Phone Intelligence OSINT Platform

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-teal.svg)](https://fastapi.tiangolo.com/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

> **AI-powered phone number intelligence and OSINT platform.**
> Validate phone numbers, detect carriers, estimate geolocation, gather public OSINT data, and generate AI investigation reports — all from publicly available and lawful data sources.

---

## ⚠️ Ethical & Legal Notice

**This tool is designed for lawful purposes only**, including:
- **Security research** and fraud prevention
- **Spam/telemarketer identification**
- **Public OSINT intelligence gathering**
- **Phone number validation for business applications**

**This tool does NOT:**
- Determine real-time GPS locations of individuals
- Access private or protected data
- Violate any privacy laws or terms of service

All geolocation data is **estimated** from public telecom databases (area codes, carrier regions) — **NOT from GPS tracking**. Every result is clearly labeled as Verified Data, Estimated Data, Public Data, or AI Inference.

**Use responsibly. Misuse for stalking, harassment, or illegal surveillance is prohibited.**

---

## Features

### 📱 Phone Number Intelligence
- **Validation** — Validate phone numbers from 200+ countries using Google's `libphonenumber`
- **Carrier Detection** — Identify carrier, line type (mobile/VoIP/landline/fixed), and porting status
- **Country Detection** — Automatically detect country, region, and timezone from phone numbers
- **Formatting** — International (E.164), national, and local formatting

### 🛡️ OSINT & Risk Analysis
- **Spam Detection** — Check public spam/telemarketer databases
- **Risk Scoring** — AI-powered risk assessment with scores 0-100
- **Social Media Correlation** — Check public profiles on WhatsApp, Telegram, Signal
- **Public Breach Search** — Search public breach databases (opt-in)

### 🌍 Geolocation (Public Data Only)
- **Area Code Mapping** — Estimate location from area codes and carrier regions
- **OpenStreetMap** — Visualize estimated locations on interactive maps
- **Nominatim** — Reverse geocode coordinates to addresses (public data)
- **OpenCellID** — Cell tower location lookup from public database (opt-in)

### 🤖 AI Investigation Reports
- **Multi-Model Support** — OpenAI GPT-4o, Gemini 2.0, DeepSeek, Qwen, Ollama
- **Structured Reports** — Executive summary, risk assessment, evidence timeline, recommendations
- **Confidence Labeling** — All AI inferences are clearly labeled

### 📊 Export & Integration
- **PDF Reports** — Professional investigation reports with branding
- **CSV Export** — Bulk data export for analysis
- **JSON API** — Full REST API with OpenAPI/Swagger documentation
- **API Keys** — Programmatic access with rate limiting and audit logs

---

## Tech Stack

### Frontend
| Technology | Purpose |
|------------|---------|
| [Next.js 14](https://nextjs.org/) | React framework (App Router) |
| [React 18](https://react.dev/) | UI library |
| [TypeScript](https://www.typescriptlang.org/) | Type safety |
| [TailwindCSS](https://tailwindcss.com/) | Utility-first CSS |
| [Framer Motion](https://www.framer.com/motion/) | Animations |
| [React Leaflet](https://react-leaflet.js.org/) | Map visualization |
| [Recharts](https://recharts.org/) | Data charts |
| [Lucide Icons](https://lucide.dev/) | Icon library |

### Backend
| Technology | Purpose |
|------------|---------|
| [FastAPI](https://fastapi.tiangolo.com/) | Python web framework |
| [SQLAlchemy](https://www.sqlalchemy.org/) | PostgreSQL ORM (async) |
| [MongoDB](https://www.mongodb.com/) | Document storage (Motor) |
| [Redis](https://redis.io/) | Caching & rate limiting |
| [phonenumbers](https://github.com/daviddrysdale/python-phonenumbers) | Phone validation (libphonenumber port) |
| [Alembic](https://alembic.sqlalchemy.org/) | Database migrations |

### AI/ML
| Provider | Integration |
|----------|-------------|
| OpenAI GPT-4o / GPT-4o-mini | ✅ |
| Google Gemini 2.0 Flash | ✅ |
| DeepSeek Chat | ✅ |
| Qwen Max | ✅ |
| Ollama (local models) | ✅ |

### Infrastructure
| Technology | Purpose |
|------------|---------|
| Docker & Docker Compose | Containerization |
| GitHub Actions | CI/CD |
| PostgreSQL 16 | Primary database |
| MongoDB 7 | Document store |
| Redis 7 | Cache |

---

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 20+
- PostgreSQL 16 (or Docker)
- MongoDB 7 (or Docker)
- Redis 7 (or Docker)

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-phone-osint.git
cd ai-phone-osint

# Start all services
docker-compose up -d

# Access the app
open http://localhost:3000
```

### Option 2: Manual Setup

```bash
# Clone and enter the directory
git clone https://github.com/yourusername/ai-phone-osint.git
cd ai-phone-osint

# Run the setup script
bash setup.sh

# Start backend (terminal 1)
cd backend
source venv/bin/activate  # or .\venv\Scripts\Activate on Windows
uvicorn app.main:app --reload --port 8000

# Start frontend (terminal 2)
cd frontend
npm run dev

# Access the app
open http://localhost:3000
```

### Option 3: One-Click Deploy

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)
[![Deploy to Vercel](https://vercel.com/button)](https://vercel.com/new)

---

## API Documentation

Once the backend is running, interactive API docs are available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/health` | Health check |
| `POST` | `/api/v1/auth/register` | Register user |
| `POST` | `/api/v1/auth/login` | Login |
| `GET` | `/api/v1/lookup/validate` | Validate phone number |
| `GET` | `/api/v1/lookup/lookup` | Full intelligence lookup |
| `GET` | `/api/v1/lookup/history` | Lookup history |
| `GET` | `/api/v1/export/json/{id}` | Export JSON |
| `GET` | `/api/v1/export/csv` | Export CSV |
| `GET` | `/api/v1/export/pdf/{id}` | Export PDF report |
| `GET` | `/api/v1/admin/users` | List users (admin) |
| `GET` | `/api/v1/admin/stats` | System stats (admin) |

### Example API Call

```bash
# Validate a phone number
curl "http://localhost:8000/api/v1/lookup/validate?phone=%2B14155552671"

# Full intelligence lookup
curl "http://localhost:8000/api/v1/lookup/lookup?phone=%2B14155552671&include_osint=true&include_ai=true"
```

---

## Environment Variables

Copy `backend/.env.example` to `backend/.env` and configure:

```bash
# Required
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/phone_osint
SECRET_KEY=your-strong-secret-key

# Phone Validation APIs (at least one recommended)
NUMVERIFY_API_KEY=your_key
ABSTRACT_API_KEY=your_key
IPQUALITYSCORE_API_KEY=your_key

# AI Providers (optional)
OPENAI_API_KEY=your_key
GEMINI_API_KEY=your_key
DEEPSEEK_API_KEY=your_key

# Geolocation (optional)
OPENCELLID_API_KEY=your_key
```

---

## Project Structure

```
ai-phone-osint/
├── backend/                          # FastAPI backend
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/               # API endpoints
│   │   │   │   ├── auth.py           # Authentication
│   │   │   │   ├── lookup.py         # Phone lookup
│   │   │   │   ├── export.py         # Export endpoints
│   │   │   │   ├── admin.py          # Admin endpoints
│   │   │   │   └── health.py         # Health check
│   │   │   ├── deps.py               # Dependencies
│   │   │   └── router.py             # Router config
│   │   ├── core/
│   │   │   ├── config.py             # Settings
│   │   │   ├── database.py           # DB connections
│   │   │   └── security.py           # Auth utilities
│   │   ├── models/                   # SQLAlchemy models
│   │   ├── services/                 # Business logic
│   │   │   ├── phone_validator.py    # libphonenumber wrapper
│   │   │   ├── carrier_service.py    # Carrier lookup
│   │   │   ├── geolocation_service.py# Map/geo services
│   │   │   ├── osint_service.py      # OSINT gathering
│   │   │   ├── ai_service.py         # AI report generation
│   │   │   └── export_service.py     # PDF/CSV/JSON export
│   │   ├── utils/                    # Helper functions
│   │   └── main.py                   # FastAPI app entry
│   ├── tests/                        # Test suite
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/                         # Next.js frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx              # Landing page
│   │   │   ├── dashboard/            # Main dashboard
│   │   │   ├── admin/                # Admin panel
│   │   │   └── api/                  # API routes
│   │   ├── components/               # React components
│   │   └── lib/                      # Utilities
│   ├── package.json
│   ├── next.config.ts
│   └── Dockerfile
├── docker-compose.yml
├── Makefile
├── setup.sh
├── install.ps1
└── README.md
```

---

## Development

### Running Tests

```bash
# Backend tests
cd backend && pytest tests/ -v

# Frontend type check
cd frontend && npm run typecheck

# All tests
make test
```

### Code Quality

```bash
# Lint backend
cd backend && flake8 app/

# Lint frontend
cd frontend && npm run lint
```

### Database Migrations

```bash
# Create migration
make migration msg="add_users_table"

# Apply migration
make migrate
```

---

## Security

### Data Classification
All data in the platform is classified and labeled:

| Label | Meaning | Example |
|-------|---------|---------|
| ✅ Verified Data | Confirmed from authoritative source | Valid/invalid from libphonenumber |
| 📍 Estimated Data | Calculated or inferred | Location from area code |
| 🌐 Public Data | From publicly accessible sources | Spam database results |
| 🤖 AI Inference | AI-generated analysis | Risk assessment |

### Recommendations
1. **Never use this tool for real-time surveillance or tracking**
2. **Always comply with local privacy laws** (GDPR, CCPA, etc.)
3. **Do not use for stalking, harassment, or illegal purposes**
4. **Configure rate limiting** in production to prevent abuse
5. **Use HTTPS** in production
6. **Regularly rotate API keys and secrets**

---

## Deployment

### Render (Backend)
1. Create a Render Web Service
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables from `.env.example`

### Vercel (Frontend)
1. Import the `frontend/` directory as a Vercel project
2. Set environment variable: `NEXT_PUBLIC_API_URL=<your-render-url>`
3. Deploy

### Docker
```bash
docker-compose up -d
```

### Manual
```bash
# Backend
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm run build && npm start
```

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- [Google libphonenumber](https://github.com/google/libphonenumber) — Phone number validation library
- [OpenStreetMap](https://www.openstreetmap.org/) & [Nominatim](https://nominatim.openstreetmap.org/) — Geocoding services
- [OpenCellID](https://www.opencellid.org/) — Public cell tower database
- [PhoneInfoga](https://github.com/sundowndev/phoneinfoga) — OSINT inspiration
- [Sherlock](https://github.com/sherlock-project/sherlock) — Username search
- [Maigret](https://github.com/soxoj/maigret) — Identity analysis
- [SpiderFoot](https://github.com/smicallef/spiderfoot) — OSINT automation
- All contributors to the open-source OSINT community

---

## Disclaimer

**⚠️ This tool is provided for educational and lawful research purposes only.**
The developers assume no liability for any misuse or damage caused by this tool.
Users are responsible for complying with all applicable laws and regulations.
