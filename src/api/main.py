from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.db.connection import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database
    print("📦 Initializing database...")
    try:
        init_db()
        print("✅ Database initialized successfully.")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
    yield

app = FastAPI(
    title="VeriFAI LLM Backend API",
    description="Backend API for VeriFAI LLM security analysis tool",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
origins = os.getenv("CORS_ORIGINS", "http://localhost:8501,http://localhost:8502").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "verifai_llm-backend"}

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "VeriFAI LLM Backend API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

# Import and include routers
from src.api.routes import health, scans, results, chat, auth
from src.api import websocket

app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(scans.router, prefix="/api/scans", tags=["Scans"])
app.include_router(results.router, prefix="/api/results", tags=["Results"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(websocket.router, tags=["WebSocket"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

