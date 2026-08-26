from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.database import engine, SessionLocal
from app.db.init_db import init_db
from app.api import dashboard, cases, payments, audit, batches, analytics, model

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables & seed initial data on startup
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Autonomous AI Revenue Recovery Engine with Deterministic Decision & Policy Guardrails",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(dashboard.router, prefix=settings.API_V1_STR)
app.include_router(cases.router, prefix=settings.API_V1_STR)
app.include_router(payments.router, prefix=settings.API_V1_STR)
app.include_router(audit.router, prefix=settings.API_V1_STR)
app.include_router(batches.router, prefix=settings.API_V1_STR)
app.include_router(analytics.router, prefix=settings.API_V1_STR)
app.include_router(model.router, prefix=settings.API_V1_STR)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "environment": "RAZORPAY TEST MODE" if settings.USE_RAZORPAY_REAL else "SIMULATION"
    }

@app.get("/")
def root():
    return {
        "message": "Welcome to RevivePay Revenue Recovery API Engine",
        "docs_url": "/docs",
        "environment": "RAZORPAY TEST MODE" if settings.USE_RAZORPAY_REAL else "SIMULATION"
    }
