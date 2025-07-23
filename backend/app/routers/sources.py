from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.models import schemas, models
from app.services.source_service import SourceService
from app.utils.auth import get_current_user
from database.connection import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.Source])
async def get_sources(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    source_service = SourceService(db)
    return source_service.get_all_sources()

@router.get("/{source_id}", response_model=schemas.Source)
async def get_source(
    source_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    source_service = SourceService(db)
    source = source_service.get_source_by_id(source_id)
    
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    return source

@router.post("/", response_model=schemas.Source)
async def create_source(
    source: schemas.SourceCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    source_service = SourceService(db)
    return source_service.create_source(source)

@router.put("/{source_id}", response_model=schemas.Source)
async def update_source(
    source_id: UUID,
    source_update: schemas.SourceCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    source_service = SourceService(db)
    source = source_service.update_source(source_id, source_update)
    
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    return source

@router.delete("/{source_id}")
async def delete_source(
    source_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    source_service = SourceService(db)
    success = source_service.delete_source(source_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Source not found")
    
    return {"message": "Source deleted successfully"}

@router.post("/{source_id}/scrape")
async def trigger_scraping(
    source_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    source_service = SourceService(db)
    source = source_service.get_source_by_id(source_id)
    
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    # Trigger scraping task (implementation depends on your task queue)
    # For now, return success message
    return {"message": f"Scraping triggered for source: {source.name}"}