from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, func, text
from typing import List, Tuple, Optional
from uuid import UUID
from app.models import models, schemas
from datetime import datetime

class IncidentService:
    def __init__(self, db: Session):
        self.db = db

    def get_incidents_paginated(self, page: int, per_page: int, filters: schemas.IncidentFilter = None) -> Tuple[List[models.CyberIncident], int]:
        query = self.db.query(models.CyberIncident).options(
            joinedload(models.CyberIncident.source),
            joinedload(models.CyberIncident.apt_group),
            joinedload(models.CyberIncident.sector)
        )

        # Apply filters
        if filters:
            if filters.severity:
                query = query.filter(models.CyberIncident.severity.in_(filters.severity))
            
            if filters.status:
                query = query.filter(models.CyberIncident.status.in_(filters.status))
            
            if filters.sector_ids:
                query = query.filter(models.CyberIncident.sector_id.in_(filters.sector_ids))
            
            if filters.apt_group_ids:
                query = query.filter(models.CyberIncident.apt_group_id.in_(filters.apt_group_ids))
            
            if filters.source_ids:
                query = query.filter(models.CyberIncident.source_id.in_(filters.source_ids))
            
            if filters.date_from:
                query = query.filter(models.CyberIncident.incident_date >= filters.date_from)
            
            if filters.date_to:
                query = query.filter(models.CyberIncident.incident_date <= filters.date_to)
            
            if filters.min_relevance_score:
                query = query.filter(models.CyberIncident.relevance_score >= filters.min_relevance_score)
            
            if filters.verified_only:
                query = query.filter(models.CyberIncident.is_verified == True)
            
            if filters.tags:
                for tag in filters.tags:
                    query = query.filter(models.CyberIncident.tags.contains([tag]))
            
            if filters.search_query:
                search_filter = or_(
                    models.CyberIncident.title.ilike(f"%{filters.search_query}%"),
                    models.CyberIncident.description.ilike(f"%{filters.search_query}%"),
                    models.CyberIncident.content.ilike(f"%{filters.search_query}%")
                )
                query = query.filter(search_filter)

        total = query.count()
        
        incidents = query.order_by(desc(models.CyberIncident.discovered_date))\
                        .offset((page - 1) * per_page)\
                        .limit(per_page)\
                        .all()

        return incidents, total

    def get_incident_by_id(self, incident_id: UUID) -> Optional[models.CyberIncident]:
        return self.db.query(models.CyberIncident)\
                     .options(
                         joinedload(models.CyberIncident.source),
                         joinedload(models.CyberIncident.apt_group),
                         joinedload(models.CyberIncident.sector)
                     )\
                     .filter(models.CyberIncident.id == incident_id)\
                     .first()

    def create_incident(self, incident: schemas.CyberIncidentCreate) -> models.CyberIncident:
        db_incident = models.CyberIncident(**incident.dict())
        self.db.add(db_incident)
        self.db.commit()
        self.db.refresh(db_incident)
        return db_incident

    def update_incident(self, incident_id: UUID, incident_update: schemas.CyberIncidentCreate) -> Optional[models.CyberIncident]:
        db_incident = self.get_incident_by_id(incident_id)
        if not db_incident:
            return None

        for field, value in incident_update.dict(exclude_unset=True).items():
            setattr(db_incident, field, value)

        self.db.commit()
        self.db.refresh(db_incident)
        return db_incident

    def delete_incident(self, incident_id: UUID) -> bool:
        db_incident = self.get_incident_by_id(incident_id)
        if not db_incident:
            return False

        self.db.delete(db_incident)
        self.db.commit()
        return True

    def full_text_search(self, query: str, page: int, per_page: int) -> Tuple[List[models.CyberIncident], int]:
        # PostgreSQL full-text search
        search_query = self.db.query(models.CyberIncident)\
                             .options(
                                 joinedload(models.CyberIncident.source),
                                 joinedload(models.CyberIncident.apt_group),
                                 joinedload(models.CyberIncident.sector)
                             )\
                             .filter(
                                 or_(
                                     func.to_tsvector('english', models.CyberIncident.title).match(query),
                                     func.to_tsvector('english', models.CyberIncident.description).match(query),
                                     func.to_tsvector('english', models.CyberIncident.content).match(query)
                                 )
                             )

        total = search_query.count()
        
        incidents = search_query.order_by(desc(models.CyberIncident.relevance_score))\
                               .offset((page - 1) * per_page)\
                               .limit(per_page)\
                               .all()

        return incidents, total

    def get_recent_incidents(self, limit: int = 10) -> List[models.CyberIncident]:
        return self.db.query(models.CyberIncident)\
                     .options(
                         joinedload(models.CyberIncident.source),
                         joinedload(models.CyberIncident.apt_group),
                         joinedload(models.CyberIncident.sector)
                     )\
                     .order_by(desc(models.CyberIncident.discovered_date))\
                     .limit(limit)\
                     .all()