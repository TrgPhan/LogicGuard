from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
)

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="LogicGuard API",
    description="AI-powered writing analysis and feedback system",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(goals.router, prefix="/api/goals", tags=["Goals"])
app.include_router(writing_types.router, prefix="/api/writing-types", tags=["Writing Types"])
app.include_router(predefined_options.router, prefix="/api/predefined-options", tags=["Predefined Options"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["Feedback"])
app.include_router(logic_checks.router, prefix="/api", tags=["Logic Checks"])


@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "message": "LogicGuard API is running",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
