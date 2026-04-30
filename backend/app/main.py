from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api.v1 import auth, documents, chat
from app.core.exceptions import register_handlers

settings = get_settings()

# ── Create App ─────────────────────────────────────────────────────

app = FastAPI(
    title="Luminary",
    description="Turn your documents into answers.",
    version="0.1.0",
    swagger_ui_parameters={"persistAuthorization": True},
)

# ── Middleware ─────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Exception Handlers ─────────────────────────────────────────────

register_handlers(app)

# ── Routers ────────────────────────────────────────────────────────

app.include_router(auth.router, prefix="/api/v1") 
app.include_router(documents.router, prefix="/api/v1")  
app.include_router(chat.router, prefix="/api/v1") 

# ── Startup / Shutdown ─────────────────────────────────────────────

@app.on_event("startup")
async def on_startup() -> None:
    print("Luminary is starting up...")


@app.on_event("shutdown")
async def on_shutdown() -> None:
    print("Luminary is shutting down...")


# ── Health Check ───────────────────────────────────────────────────

@app.get("/")
async def root():
    return {"message": "Luminary is running", "environment": settings.environment}