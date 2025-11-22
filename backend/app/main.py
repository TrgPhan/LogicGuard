from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
from app.core.config import get_settings
from app.routers import (
    analysis,
    auth,
    documents,
    feedback,
    goals,
    logic_checks,
    predefined_options,
    users,
    writing_types,
    ai_functions,  # ✅ THÊM ROUTER AI FUNCTIONS
)

settings = get_settings()

# Configure CORS origins dynamically
def get_allowed_origins():
    """Get list of allowed CORS origins from settings"""
    origins = [settings.FRONTEND_URL]
    
    # Add custom origins if specified
    if settings.ALLOWED_ORIGINS:
        custom_origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",")]
        origins.extend(custom_origins)
    
    # Always allow localhost for development
    localhost_variants = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    for variant in localhost_variants:
        if variant not in origins:
            origins.append(variant)
    
    return origins


# Lifespan event handler (thay cho on_event startup)
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("📌 Creating tables on startup...")
    print(f"🌐 Allowed CORS origins: {get_allowed_origins()}")
    Base.metadata.create_all(bind=engine)
    yield
    print("🧹 Shutdown complete.")


# FastAPI app
app = FastAPI(
    title="LogicGuard API",
    description="AI-powered writing analysis and feedback system",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS with dynamic origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(goals.router, prefix="/api/goals", tags=["Goals"])
app.include_router(
    writing_types.router,
    prefix="/api/writing-types",
    tags=["Writing Types"],
)
app.include_router(
    predefined_options.router,
    prefix="/api/predefined-options",
    tags=["Predefined Options"],
)
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["Feedback"])

# Router logic checks cũ (đang dùng prefix="/api")
app.include_router(logic_checks.router, prefix="/api", tags=["Logic Checks"])

# ✅ AI Functions Gateway: /api/ai/functions/run
app.include_router(
    ai_functions.router,
    prefix="/api/ai",
    tags=["AI Functions"],
)


@app.get("/")
def read_root():
    return {
        "message": "LogicGuard API is running",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


# Optional: local dev mode
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
