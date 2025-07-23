from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models import schemas
from app.services.dashboard_service import DashboardService
from app.utils.auth import get_current_user
from database.connection import get_db
from app.models.models import User

router = APIRouter()

@router.get("/stats", response_model=schemas.DashboardData)
async def get_dashboard_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    dashboard_service = DashboardService(db)
    return dashboard_service.get_dashboard_data()

@router.get("/recent-incidents", response_model=list[schemas.CyberIncident])
async def get_recent_incidents(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    dashboard_service = DashboardService(db)
    return dashboard_service.get_recent_incidents(limit)

@router.get("/sector-breakdown")
async def get_sector_breakdown(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    dashboard_service = DashboardService(db)
    return dashboard_service.get_sector_breakdown()

@router.get("/threat-trends")
async def get_threat_trends(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    dashboard_service = DashboardService(db)
    return dashboard_service.get_threat_trends(days)