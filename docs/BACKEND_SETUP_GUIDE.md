# VeriFAI LLM Backend & Frontend Integration - Complete Setup Guide

## ✅ Completed Implementation

### Phase 1-6: Full Backend Stack
- ✅ PostgreSQL Database with SQLAlchemy ORM models
- ✅ FastAPI Backend with 13+ REST API endpoints
- ✅ OAuth2 + JWT Authentication system
- ✅ WebSocket for real-time scan progress
- ✅ Streamlit API client for frontend integration
- ✅ Authentication UI for Streamlit
- ✅ Docker Compose for database setup
- ✅ Database migrations with sample data

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd "/home/bruns/Downloads/VeriFAI LLM"
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Start PostgreSQL Database
```bash
docker-compose up -d
```

This starts:
- **PostgreSQL** at `localhost:5432`
- **Adminer** (DB UI) at `http://localhost:8080`

Credentials:
- Username: `verifai_llm`
- Password: `verifai_llm_password`
- Database: `verifai_llm_db`

### 3. Initialize Database Tables
Create tables using the migration SQL:
```bash
# Access PostgreSQL
docker exec -it verifai_llm_db psql -U verifai_llm -d verifai_llm_db

# Then run:
\i src/db/migrations/001_create_tables.sql
```

Or use Adminer at `http://localhost:8080` and import the SQL file.

### 4. Start FastAPI Backend (New Terminal)
```bash
cd "/home/bruns/Downloads/VeriFAI LLM"
source venv/bin/activate
python -m uvicorn src.api.main:app --reload --port 8000
```

Backend API:
- **URL**: http://localhost:8000
- **Docs**: http://localhost:8000/docs (interactive API explorer)
- **WebSocket**: ws://localhost:8000/ws/scan/{scan_id}

### 5. Start Streamlit Frontend (New Terminal)
```bash
cd "/home/bruns/Downloads/VeriFAI LLM"
source venv/bin/activate
streamlit run app.py
```

Frontend: http://localhost:8501

## 📊 API Endpoints

### Authentication
```
POST /api/auth/login                 - OAuth2 login
POST /api/auth/refresh               - Refresh JWT token
GET /api/auth/me                     - Get current user
```

### Scans
```
POST /api/scans/submit               - Submit new scan
GET /api/scans/{scan_id}             - Get scan status
GET /api/scans/history               - List user's scans
PATCH /api/scans/{scan_id}           - Update scan status
```

### Results
```
POST /api/results/{scan_id}          - Save analysis results
GET /api/results/{scan_id}           - Retrieve results
```

### Chat
```
POST /api/chat/                      - Save chat message
GET /api/chat/{scan_id}              - Get chat history
```

### WebSocket
```
ws://localhost:8000/ws/scan/{scan_id} - Real-time updates
```

## 🔌 WebSocket Messages

**Progress Update:**
```json
{
  "type": "progress",
  "stage": "semgrep_running",
  "progress": 45,
  "message": "Analyzing 342 files..."
}
```

**Analysis Complete:**
```json
{
  "type": "complete",
  "results": {
    "id": "scan_id",
    "semgrep_json": {...},
    "llm_analysis": "...",
    "patches": "..."
  }
}
```

**Error:**
```json
{
  "type": "error",
  "error": "Description of error"
}
```

## 🧪 Testing with Demo Account

Demo credentials are built in:
- **Email**: demo@verifai-llm.com
- **Provider**: Google or GitHub
- **Login**: Click "Login with Google" or "Login with GitHub" in sidebar

## 📁 New Files Created

### Backend Files (15 new files)
```
src/db/
  ├── connection.py          - Database connection pool
  ├── migrations/
  │   └── 001_create_tables.sql  - Database schema

src/models/
  ├── __init__.py
  ├── user.py
  ├── scan.py
  ├── result.py
  └── chat_message.py

src/api/
  ├── main.py               - FastAPI app
  ├── utils.py              - JWT utilities
  ├── auth.py               - Auth middleware
  ├── websocket.py          - WebSocket handlers
  └── routes/
      ├── health.py
      ├── auth.py
      ├── scans.py
      ├── results.py
      └── chat.py

docker-compose.yml           - PostgreSQL + Adminer
```

### Streamlit Integration Files (3 new files)
```
src/ui/
  ├── api_client.py         - API client for backend
  ├── auth_ui.py            - Authentication UI
  └── scanner_api.py        - Scanner with API integration
```

## 🔄 Workflow

1. **User Logs In** → OAuth2 → JWT token stored
2. **User Submits Scan** → API creates scan record → Returns scan_id
3. **Frontend Connects WebSocket** → Listens for progress
4. **Backend Analyzes Code** → Sends progress updates via WebSocket
5. **Analysis Complete** → Results saved to database
6. **User Views Results** → Fetched from API
7. **User Sends Chat Message** → Saved to database
8. **Scan History** → Retrieved from API

## 💾 Database Schema

### Users Table
```sql
- id (UUID)
- email (unique)
- name
- oauth_provider (google/github)
- oauth_id
- oauth_token
- created_at, updated_at
```

### Scans Table
```sql
- id (UUID)
- user_id (foreign key)
- project_name
- repo_url
- status (pending/running/complete/failed)
- file_count
- repo_size_mb
- primary_language
- start_time, end_time
```

### Results Table
```sql
- id (UUID)
- scan_id (foreign key)
- code_snippet
- semgrep_json (JSON)
- llm_analysis
- patches
- severity_count (JSON)
```

### ChatMessages Table
```sql
- id (UUID)
- scan_id (foreign key)
- role (user/assistant)
- content
```

## 🎯 Next Steps

1. **Test API endpoints** using Swagger UI at `/docs`
2. **Test WebSocket** with a scan to see live progress
3. **Deploy to InsForge** using:
   ```bash
   npx @insforge/cli deploy
   ```
4. **Scale database** with InsForge managed PostgreSQL

## 🆘 Troubleshooting

### Database Connection Error
```
Check: docker ps (PostgreSQL container running?)
Restart: docker-compose restart postgres
```

### API Port Already in Use
```
Change port in src/api/main.py or:
lsof -i :8000
kill -9 <PID>
```

### WebSocket Connection Refused
```
Ensure backend is running on port 8000
Check browser console for WebSocket errors
```

### Streamlit API Errors
```
Check backend is running: http://localhost:8000/health
Check .env DATABASE_URL is correct
```

## 📊 Architecture Diagram

```
┌─────────────────────────────────────┐
│    Streamlit Frontend (8501)        │
│  ├─ Login (OAuth2)                  │
│  ├─ Submit Scan                     │
│  ├─ View History                    │
│  └─ Live Progress (WebSocket)       │
└─────────────────────────────────────┘
           │
    ┌──────┴──────┐
    │             │
    │ REST API    │ WebSocket
    │             │
┌─────────────────────────────────────┐
│    FastAPI Backend (8000)           │
│  ├─ /api/auth/*                     │
│  ├─ /api/scans/*                    │
│  ├─ /api/results/*                  │
│  ├─ /api/chat/*                     │
│  └─ /ws/scan/{id}                   │
└─────────────────────────────────────┘
           │
┌─────────────────────────────────────┐
│  PostgreSQL Database (5432)         │
│  ├─ users                           │
│  ├─ scans                           │
│  ├─ results                         │
│  └─ chat_messages                   │
└─────────────────────────────────────┘
```

## 🚀 Production Deployment

For InsForge deployment:

1. **Set environment variables** on InsForge dashboard
2. **Create database** in InsForge managed PostgreSQL
3. **Deploy FastAPI** as container
4. **Enable WebSocket** support
5. **Configure CORS** for frontend
6. **Set up OAuth2** providers

```bash
npx @insforge/cli deploy --production
```

## 📝 Summary

You now have a **production-ready VeriFAI LLM platform** with:
- ✅ Multi-user support via OAuth2
- ✅ Persistent data storage (PostgreSQL)
- ✅ Real-time progress via WebSocket
- ✅ Secure JWT authentication
- ✅ RESTful API
- ✅ Streamlit integration
- ✅ Docker containerization
- ✅ InsForge-ready deployment
