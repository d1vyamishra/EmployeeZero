# 🤖 Employee Zero

> The autonomous AI employee managing inbound leads, scraping intelligence, and executing CRM operations 24/7.

[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2015-black?style=for-the-badge&logo=nextdotjs)](https://nextjs.org)
[![Python](https://img.shields.io/badge/Backend-Python%203.11-blue?style=for-the-badge&logo=python)](https://python.org)
[![Supabase](https://img.shields.io/badge/Database-Supabase-green?style=for-the-badge&logo=supabase)](https://supabase.com)
[![Vercel](https://img.shields.io/badge/Deploy-Vercel-black?style=for-the-badge&logo=vercel)](https://vercel.com)

---

## 🗺️ Quick Navigation Matrix

| Component | Directory | Purpose | Status |
| :--- | :--- | :--- | :--- |
| **Frontend Dashboard** | `/frontend` | Reactive lead analytics & live feed UI | 🚀 Production-Ready |
| **Backend Workers** | `/backend` | Async processing, email engines & scraping | ⚡ Operational |
| **Modules Core** | `/backend/modules` | Orchestration (LinkedIn, Scraper, AI Brain) | 🧠 Integrated |

---

## ⚡ System Architecture

```text
  [ Inbound Lead Source ] ──> [ Scraper / LinkedIn Agent ]
                                         │
                                         ▼
  [ React Dashboard ] <────> [ Supabase Database ] <────> [ Python Background Worker ]
     (Next.js App)               (RLS Enabled)                (OpenAI Orchestration)
🚀 Deployment Playbook
Frontend Installation (Next.js)
Bash
cd frontend
npm install
npm run dev
Backend Initialization (Python)
Bash
cd backend
python -m venv venv
# Windows execution environment
.\venv\Scripts\activate
pip install -r requirements.txt
python main.py
🛠️ Environment Configuration Guide
Ensure you have your environment variables locally tracked. Do not commit these variables to your public matrix:

Frontend Envs (/frontend/.env.local)
Ini, TOML
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url_string
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
Backend Envs (/backend/.env)
Ini, TOML
SUPABASE_URL=your_supabase_url_string
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
OPENAI_API_KEY=your_openai_api_credential_key
Detailed System Map
Plaintext
├── backend/
│   ├── modules/
│   │   ├── ai_brain.py         # Lead sentiment analysis & context creation
│   │   ├── email_sender.py     # High-deliverability SMTP dispatch engine
│   │   ├── linkedin_agent.py   # Automated social profile scraping
│   │   └── scraper.py          # Corporate intelligence web target scraper
│   ├── background_worker.py    # Async infinite loop task runner
│   └── main.py                 # Core API orchestration service
└── frontend/
    ├── app/
    │   ├── layout.tsx          # Shell layout wrapper
    │   └── page.tsx            # Live reactive operational dashboard
    └── lib/
        └── supabase.ts         # Unified DB instance initiator
🛡️ Production Readiness Checklist
[x] Global Git optimization complete (.gitignore deployed)

[x] Primary deployment tree unified to main branch

[ ] Row Level Security (RLS) policies verified in Supabase

[ ] Safe-loop guard checks deployed in background automation

[ ] Production frontend build deployment (Vercel mapping)
