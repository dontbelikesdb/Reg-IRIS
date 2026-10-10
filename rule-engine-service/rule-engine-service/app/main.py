from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.impact import router as impact_router
from app.api.internal import router as internal_router
from app.api.rules import router as rules_router

app = FastAPI(
    title="Reg IRIS - Core Regulatory & Impact API",
    description="Regulatory search, JSON-driven compliance rule evaluation, and trade impact analysis.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

app.include_router(rules_router)
app.include_router(impact_router)
app.include_router(internal_router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "core-api-service"}