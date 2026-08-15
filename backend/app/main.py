from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.utils.config import FRONTEND_URLS, LLM_MODE
from app.api.routes import scan, recommendations, ai, dashboard, history, debug
from app.database.seed import init_db
from app.database.session import engine

app = FastAPI(
    title="Before You Throw It Away - AI Reuse Backend",
    description="Two-Stage Computer vision object detection, deterministic recommendations & generative AI personalized guide backend using FastAPI",
    version="1.0.0"
)

@app.on_event("startup")
def on_startup():
    init_db()

# Configure CORS
origins = list(set(FRONTEND_URLS + [
    "https://ai-before-you-throw-it-away.netlify.app",
    "http://localhost:5173",
    "http://localhost:5174"
]))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(scan.router)
app.include_router(recommendations.router)
app.include_router(ai.router)
app.include_router(dashboard.router)
app.include_router(history.router)
app.include_router(debug.router)

@app.get("/api/health", tags=["Health"])
async def health_check():
    db_status = "connected" if engine is not None else "disconnected"
    ai_status = "available" if LLM_MODE in ["real", "mock"] else "unavailable"
    return {
        "status": "ok",
        "service": "before-you-throw-it-away-backend",
        "database": db_status,
        "ai": ai_status
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
