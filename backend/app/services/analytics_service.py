from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.models import models

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_incident_trends(self, days: int, sector_id: Optional[str] = None, severity: Optional[str] = None) -> Dict[str, Any]:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = self.db.query(
            func.date(models.CyberIncident.discovered_date).label('date'),
            func.count(models.CyberIncident.id).label('count')
        ).filter(models.CyberIncident.discovered_date >= start_date)
        
        if sector_id:
            query = query.filter(models.CyberIncident.sector_id == sector_id)
        
        if severity:
            query = query.filter(models.CyberIncident.severity == severity)
        
        results = query.group_by(func.date(models.CyberIncident.discovered_date))\
                      .order_by('date')\
                      .all()
        
        return {
            'trends': [{'date': str(date), 'count': count} for date, count in results],
            'total_incidents': sum(count for _, count in results),
            'period_days': days
        }

    def get_apt_activity(self, days: int) -> Dict[str, Any]:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        results = self.db.query(
            models.APTGroup.name,
            models.APTGroup.origin_country,
            func.count(models.CyberIncident.id).label('incident_count'),
            func.max(models.CyberIncident.incident_date).label('last_activity')
        ).join(models.CyberIncident)\
         .filter(models.CyberIncident.discovered_date >= start_date)\
         .group_by(models.APTGroup.id, models.APTGroup.name, models.APTGroup.origin_country)\
         .order_by(desc('incident_count'))\
         .all()
        
        return {
            'apt_groups': [
                {
                    'name': name,
                    'origin_country': origin_country,
                    'incident_count': incident_count,
                    'last_activity': str(last_activity) if last_activity else None
                }
                for name, origin_country, incident_count, last_activity in results
            ],
            'period_days': days
        }

    def get_sector_analysis(self, days: int) -> Dict[str, Any]:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        results = self.db.query(
            models.Sector.name,
            models.Sector.sector_type,
            func.count(models.CyberIncident.id).label('incident_count'),
            func.count(
                models.CyberIncident.id
            ).filter(models.CyberIncident.severity == models.IncidentSeverity.critical).label('critical_count'),
            func.avg(models.CyberIncident.relevance_score).label('avg_relevance')
        ).join(models.CyberIncident)\
         .filter(models.CyberIncident.discovered_date >= start_date)\
         .group_by(models.Sector.id, models.Sector.name, models.Sector.sector_type)\
         .order_by(desc('incident_count'))\
         .all()
        
        return {
            'sectors': [
                {
                    'name': name,
                    'type': sector_type.value,
                    'incident_count': incident_count,
                    'critical_count': critical_count,
                    'avg_relevance_score': float(avg_relevance) if avg_relevance else 0.0
                }
                for name, sector_type, incident_count, critical_count, avg_relevance in results
            ],
            'period_days': days
        }

    def get_threat_intelligence_summary(self, days: int) -> Dict[str, Any]:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # High-severity incidents
        high_severity_incidents = self.db.query(models.CyberIncident)\
                                        .filter(
                                            and_(
                                                models.CyberIncident.discovered_date >= start_date,
                                                models.CyberIncident.severity.in_([
                                                    models.IncidentSeverity.high,
                                                    models.IncidentSeverity.critical
                                                ])
                                            )
                                        )\
                                        .order_by(desc(models.CyberIncident.discovered_date))\
                                        .limit(10)\
                                        .all()
        
        # Top threat indicators
        ioc_results = self.db.query(
            models.CyberIncident.indicators_of_compromise
        ).filter(
            and_(
                models.CyberIncident.discovered_date >= start_date,
                models.CyberIncident.indicators_of_compromise.isnot(None)
            )
        ).all()
        
        # Emerging threats (recent incidents with high relevance scores)
        emerging_threats = self.db.query(models.CyberIncident)\
                                 .filter(
                                     and_(
                                         models.CyberIncident.discovered_date >= start_date,
                                         models.CyberIncident.relevance_score >= 0.8
                                     )
                                 )\
                                 .order_by(desc(models.CyberIncident.relevance_score))\
                                 .limit(5)\
                                 .all()
        
        return {
            'high_severity_incidents': [
                {
                    'id': str(incident.id),
                    'title': incident.title,
                    'severity': incident.severity.value,
                    'discovered_date': str(incident.discovered_date),
                    'relevance_score': incident.relevance_score
                }
                for incident in high_severity_incidents
            ],
            'emerging_threats': [
                {
                    'id': str(incident.id),
                    'title': incident.title,
                    'relevance_score': incident.relevance_score,
                    'discovered_date': str(incident.discovered_date)
                }
                for incident in emerging_threats
            ],
            'total_iocs': len([ioc for ioc, in ioc_results if ioc]),
            'period_days': days
        }

    def get_geographic_distribution(self, days: int) -> Dict[str, Any]:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        results = self.db.query(
            models.CyberIncident.geographical_location,
            func.count(models.CyberIncident.id).label('incident_count')
        ).filter(
            and_(
                models.CyberIncident.discovered_date >= start_date,
                models.CyberIncident.geographical_location.isnot(None)
            )
        ).group_by(models.CyberIncident.geographical_location)\
         .order_by(desc('incident_count'))\
         .all()
        
        return {
            'geographic_data': [
                {
                    'location': location,
                    'incident_count': incident_count
                }
                for location, incident_count in results
            ],
            'period_days': days
        }