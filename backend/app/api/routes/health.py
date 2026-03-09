"""Health check routes"""
from fastapi import APIRouter, Request

from app.core.config import settings

router = APIRouter()


@router.get("/")
async def root():
    return {
        "service": settings.api_title,
        "status": "running",
        "version": settings.api_version,
    }


@router.get("/health")
async def health():
    return {
        "status": "healthy",
        "llm_configured": bool(settings.anthropic_api_key),
        "model": settings.anthropic_model,
    }
