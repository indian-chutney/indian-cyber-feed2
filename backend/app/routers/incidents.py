from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.models import schemas, models
from app.services.incident_service import IncidentService
from app.utils.auth import get_current_user
from database.connection import get_db

router = APIRouter()

@router.get("/", response_model=schemas.PaginatedResponse)
async def get_incidents(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    severity: Optional[List[str]] = Query(None),
    status: Optional[List[str]] = Query(None),
    sector_id: Optional[UUID] = None,
    apt_group_id: Optional[UUID] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    incident_service = IncidentService(db)
    
    filters = schemas.IncidentFilter(
        severity=severity,
        status=status,
        sector_ids=[sector_id] if sector_id else None,
        apt_group_ids=[apt_group_id] if apt_group_id else None,
        search_query=search
    )
    
    incidents, total = incident_service.get_incidents_paginated(
        page=page, per_page=per_page, filters=filters
    )
    
    return schemas.PaginatedResponse(
        items=incidents,
        total=total,
        page=page,
        per_page=per_page,
        pages=(total + per_page - 1) // per_page
    )

@router.get("/{incident_id}", response_model=schemas.CyberIncident)
async def get_incident(
    incident_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    incident_service = IncidentService(db)
    incident = incident_service.get_incident_by_id(incident_id)
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    return incident

@router.post("/", response_model=schemas.CyberIncident)
async def create_incident(
    incident: schemas.CyberIncidentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    incident_service = IncidentService(db)
    return incident_service.create_incident(incident)

@router.put("/{incident_id}", response_model=schemas.CyberIncident)
async def update_incident(
    incident_id: UUID,
    incident_update: schemas.CyberIncidentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    incident_service = IncidentService(db)
    incident = incident_service.update_incident(incident_id, incident_update)
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    return incident

@router.delete("/{incident_id}")
async def delete_incident(
    incident_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    incident_service = IncidentService(db)
    success = incident_service.delete_incident(incident_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    return {"message": "Incident deleted successfully"}

@router.get("/search/full-text")
async def search_incidents(
    query: str = Query(..., min_length=3),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    incident_service = IncidentService(db)
    incidents, total = incident_service.full_text_search(query, page, per_page)
    
    return schemas.PaginatedResponse(
        items=incidents,
        total=total,
        page=page,
        per_page=per_page,
        pages=(total + per_page - 1) // per_page
    )