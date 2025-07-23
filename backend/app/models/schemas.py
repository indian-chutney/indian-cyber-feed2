from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from app.models.models import IncidentSeverity, IncidentStatus, SourceType, SectorType

# User schemas
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: UUID
    is_active: bool
    is_admin: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

# Source schemas
class SourceBase(BaseModel):
    name: str
    url: str
    source_type: SourceType
    is_active: bool = True
    scraping_interval: int = 3600

class SourceCreate(SourceBase):
    pass

class Source(SourceBase):
    id: UUID
    last_scraped: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# APT Group schemas
class APTGroupBase(BaseModel):
    name: str
    aliases: Optional[List[str]] = []
    description: Optional[str] = None
    origin_country: Optional[str] = None
    first_seen: Optional[datetime] = None
    is_active: bool = True

class APTGroupCreate(APTGroupBase):
    pass

class APTGroup(APTGroupBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Sector schemas
class SectorBase(BaseModel):
    name: str
    sector_type: SectorType
    description: Optional[str] = None

class SectorCreate(SectorBase):
    pass

class Sector(SectorBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# Classification schemas
class ClassificationBase(BaseModel):
    name: str
    category: str
    description: Optional[str] = None
    keywords: Optional[List[str]] = []
    confidence_threshold: float = 0.7

class ClassificationCreate(ClassificationBase):
    pass

class Classification(ClassificationBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# Cyber Incident schemas
class CyberIncidentBase(BaseModel):
    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    severity: IncidentSeverity = IncidentSeverity.medium
    status: IncidentStatus = IncidentStatus.open
    incident_date: Optional[datetime] = None
    url: Optional[str] = None
    external_id: Optional[str] = None
    tags: Optional[List[str]] = []
    indicators_of_compromise: Optional[Dict[str, Any]] = {}
    geographical_location: Optional[str] = None
    affected_systems: Optional[List[str]] = []
    mitigation_steps: Optional[str] = None
    relevance_score: float = 0.5
    is_verified: bool = False

class CyberIncidentCreate(CyberIncidentBase):
    source_id: Optional[UUID] = None
    apt_group_id: Optional[UUID] = None
    sector_id: Optional[UUID] = None

class CyberIncident(CyberIncidentBase):
    id: UUID
    source_id: Optional[UUID] = None
    apt_group_id: Optional[UUID] = None
    sector_id: Optional[UUID] = None
    discovered_date: datetime
    created_at: datetime
    updated_at: datetime
    source: Optional[Source] = None
    apt_group: Optional[APTGroup] = None
    sector: Optional[Sector] = None

    class Config:
        from_attributes = True

# Dashboard and analytics schemas
class IncidentStats(BaseModel):
    total_incidents: int
    critical_incidents: int
    high_incidents: int
    medium_incidents: int
    low_incidents: int
    open_incidents: int
    investigating_incidents: int
    resolved_incidents: int

class SectorStats(BaseModel):
    sector_name: str
    incident_count: int
    critical_count: int
    last_incident_date: Optional[datetime]

class APTStats(BaseModel):
    apt_name: str
    incident_count: int
    origin_country: Optional[str]
    last_activity: Optional[datetime]

class ThreatTrend(BaseModel):
    date: datetime
    incident_count: int
    severity_breakdown: Dict[str, int]

class DashboardData(BaseModel):
    stats: IncidentStats
    sector_stats: List[SectorStats]
    apt_stats: List[APTStats]
    recent_incidents: List[CyberIncident]
    threat_trends: List[ThreatTrend]

# Search and filter schemas
class IncidentFilter(BaseModel):
    severity: Optional[List[IncidentSeverity]] = None
    status: Optional[List[IncidentStatus]] = None
    sector_ids: Optional[List[UUID]] = None
    apt_group_ids: Optional[List[UUID]] = None
    source_ids: Optional[List[UUID]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search_query: Optional[str] = None
    min_relevance_score: Optional[float] = None
    tags: Optional[List[str]] = None
    verified_only: Optional[bool] = None

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    per_page: int
    pages: int

# WebSocket message schemas
class WSMessage(BaseModel):
    type: str
    data: Dict[str, Any]

class IncidentAlert(BaseModel):
    incident_id: UUID
    title: str
    severity: IncidentSeverity
    sector: Optional[str] = None
    apt_group: Optional[str] = None
    timestamp: datetime