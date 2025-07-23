from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, Float, Enum, ForeignKey, ARRAY, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from database.connection import Base

class IncidentSeverity(enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class IncidentStatus(enum.Enum):
    open = "open"
    investigating = "investigating"
    resolved = "resolved"
    false_positive = "false_positive"

class SourceType(enum.Enum):
    forum = "forum"
    paste_site = "paste_site"
    social_media = "social_media"
    blog = "blog"
    github = "github"
    security_feed = "security_feed"
    news = "news"

class SectorType(enum.Enum):
    banking = "banking"
    government = "government"
    healthcare = "healthcare"
    energy = "energy"
    telecom = "telecom"
    defense = "defense"
    education = "education"
    retail = "retail"
    other = "other"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    last_login = Column(DateTime)

class Source(Base):
    __tablename__ = "sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    url = Column(Text, nullable=False)
    source_type = Column(Enum(SourceType), nullable=False)
    is_active = Column(Boolean, default=True)
    scraping_interval = Column(Integer, default=3600)
    last_scraped = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    incidents = relationship("CyberIncident", back_populates="source")

class APTGroup(Base):
    __tablename__ = "apt_groups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    aliases = Column(ARRAY(String))
    description = Column(Text)
    origin_country = Column(String(100))
    first_seen = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    incidents = relationship("CyberIncident", back_populates="apt_group")

class Sector(Base):
    __tablename__ = "sectors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    sector_type = Column(Enum(SectorType), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=func.now())

    incidents = relationship("CyberIncident", back_populates="sector")

class Classification(Base):
    __tablename__ = "classifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text)
    keywords = Column(ARRAY(String))
    confidence_threshold = Column(Float, default=0.7)
    created_at = Column(DateTime, default=func.now())

class CyberIncident(Base):
    __tablename__ = "cyber_incidents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    content = Column(Text)
    severity = Column(Enum(IncidentSeverity), default=IncidentSeverity.medium)
    status = Column(Enum(IncidentStatus), default=IncidentStatus.open)
    source_id = Column(UUID(as_uuid=True), ForeignKey("sources.id"))
    apt_group_id = Column(UUID(as_uuid=True), ForeignKey("apt_groups.id"))
    sector_id = Column(UUID(as_uuid=True), ForeignKey("sectors.id"))
    incident_date = Column(DateTime)
    discovered_date = Column(DateTime, default=func.now())
    url = Column(Text)
    external_id = Column(String(255))
    tags = Column(ARRAY(String))
    indicators_of_compromise = Column(JSON)
    geographical_location = Column(String(255))
    affected_systems = Column(ARRAY(String))
    mitigation_steps = Column(Text)
    relevance_score = Column(Float, default=0.5)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    source = relationship("Source", back_populates="incidents")
    apt_group = relationship("APTGroup", back_populates="incidents")
    sector = relationship("Sector", back_populates="incidents")

class IncidentClassification(Base):
    __tablename__ = "incident_classifications"

    incident_id = Column(UUID(as_uuid=True), ForeignKey("cyber_incidents.id", ondelete="CASCADE"), primary_key=True)
    classification_id = Column(UUID(as_uuid=True), ForeignKey("classifications.id", ondelete="CASCADE"), primary_key=True)
    confidence_score = Column(Float, nullable=False)