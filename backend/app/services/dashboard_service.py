from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from uuid import UUID
from app.models import models, schemas
from app.services.incident_service import IncidentService
from datetime import datetime, timedelta

class DashboardService:
    def __init__(self, db: Session):
        self.db = db
        self.incident_service = IncidentService(db)

    def get_dashboard_data(self) -> schemas.DashboardData:
        stats = self._get_incident_stats()
        sector_stats = self._get_sector_stats()
        apt_stats = self._get_apt_stats()
        recent_incidents = self.incident_service.get_recent_incidents(5)
        threat_trends = self._get_threat_trends(30)

        return schemas.DashboardData(
            stats=stats,
            sector_stats=sector_stats,
            apt_stats=apt_stats,
            recent_incidents=recent_incidents,
            threat_trends=threat_trends
        )

    def _get_incident_stats(self) -> schemas.IncidentStats:
        total_incidents = self.db.query(models.CyberIncident).count()
        
        severity_counts = self.db.query(
            models.CyberIncident.severity,
            func.count(models.CyberIncident.id)
        ).group_by(models.CyberIncident.severity).all()

        status_counts = self.db.query(
            models.CyberIncident.status,
            func.count(models.CyberIncident.id)
        ).group_by(models.CyberIncident.status).all()

        severity_dict = {severity.value: 0 for severity in models.IncidentSeverity}
        for severity, count in severity_counts:
            severity_dict[severity.value] = count

        status_dict = {status.value: 0 for status in models.IncidentStatus}
        for status, count in status_counts:
            status_dict[status.value] = count

        return schemas.IncidentStats(
            total_incidents=total_incidents,
            critical_incidents=severity_dict['critical'],
            high_incidents=severity_dict['high'],
            medium_incidents=severity_dict['medium'],
            low_incidents=severity_dict['low'],
            open_incidents=status_dict['open'],
            investigating_incidents=status_dict['investigating'],
            resolved_incidents=status_dict['resolved']
        )

    def _get_sector_stats(self) -> List[schemas.SectorStats]:
        results = self.db.query(
            models.Sector.name,
            func.count(models.CyberIncident.id).label('incident_count'),
            func.count(
                models.CyberIncident.id
            ).filter(models.CyberIncident.severity == models.IncidentSeverity.critical).label('critical_count'),
            func.max(models.CyberIncident.incident_date).label('last_incident_date')
        ).outerjoin(models.CyberIncident)\
         .group_by(models.Sector.id, models.Sector.name)\
         .order_by(desc('incident_count'))\
         .all()

        return [
            schemas.SectorStats(
                sector_name=name,
                incident_count=incident_count or 0,
                critical_count=critical_count or 0,
                last_incident_date=last_incident_date
            )
            for name, incident_count, critical_count, last_incident_date in results
        ]

    def _get_apt_stats(self) -> List[schemas.APTStats]:
        results = self.db.query(
            models.APTGroup.name,
            models.APTGroup.origin_country,
            func.count(models.CyberIncident.id).label('incident_count'),
            func.max(models.CyberIncident.incident_date).label('last_activity')
        ).outerjoin(models.CyberIncident)\
         .group_by(models.APTGroup.id, models.APTGroup.name, models.APTGroup.origin_country)\
         .order_by(desc('incident_count'))\
         .limit(10)\
         .all()

        return [
            schemas.APTStats(
                apt_name=name,
                origin_country=origin_country,
                incident_count=incident_count or 0,
                last_activity=last_activity
            )
            for name, origin_country, incident_count, last_activity in results
        ]

    def _get_threat_trends(self, days: int) -> List[schemas.ThreatTrend]:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        results = self.db.query(
            func.date(models.CyberIncident.discovered_date).label('date'),
            func.count(models.CyberIncident.id).label('incident_count')
        ).filter(models.CyberIncident.discovered_date >= start_date)\
         .group_by(func.date(models.CyberIncident.discovered_date))\
         .order_by('date')\
         .all()

        return [
            schemas.ThreatTrend(
                date=date,
                incident_count=incident_count,
                severity_breakdown={}  # Could be enhanced to include severity breakdown
            )
            for date, incident_count in results
        ]

    def get_recent_incidents(self, limit: int) -> List[schemas.CyberIncident]:
        return self.incident_service.get_recent_incidents(limit)

    def get_sector_breakdown(self):
        return self._get_sector_stats()

    def get_threat_trends(self, days: int):
        return self._get_threat_trends(days)