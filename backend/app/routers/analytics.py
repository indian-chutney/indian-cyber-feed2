from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
from app.services.analytics_service import AnalyticsService
from app.utils.auth import get_current_user
from database.connection import get_db
from app.models.models import User

router = APIRouter()

@router.get("/trends")
async def get_incident_trends(
    days: int = Query(30, ge=1, le=365),
    sector_id: Optional[str] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    analytics_service = AnalyticsService(db)
    return analytics_service.get_incident_trends(days, sector_id, severity)

@router.get("/apt-activity")
async def get_apt_activity(
    days: int = Query(90, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    analytics_service = AnalyticsService(db)
    return analytics_service.get_apt_activity(days)

@router.get("/sector-analysis")
async def get_sector_analysis(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    analytics_service = AnalyticsService(db)
    return analytics_service.get_sector_analysis(days)

@router.get("/threat-intelligence")
async def get_threat_intelligence(
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    analytics_service = AnalyticsService(db)
    return analytics_service.get_threat_intelligence_summary(days)

@router.get("/geographic-distribution")
async def get_geographic_distribution(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    analytics_service = AnalyticsService(db)
    return analytics_service.get_geographic_distribution(days)