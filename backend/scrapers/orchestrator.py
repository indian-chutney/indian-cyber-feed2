import asyncio
from sqlalchemy.orm import Session
from app.models import models, schemas
from app.services.incident_service import IncidentService
from app.services.source_service import SourceService
from scrapers.base_scraper import scrape_source
from datetime import datetime, timedelta
import structlog
from typing import List, Dict, Any

logger = structlog.get_logger()

class ScrapingOrchestrator:
    """Orchestrates the scraping of multiple sources"""
    
    def __init__(self, db: Session):
        self.db = db
        self.incident_service = IncidentService(db)
        self.source_service = SourceService(db)

    async def run_scheduled_scraping(self):
        """Run scraping for all active sources that are due for scraping"""
        logger.info("Starting scheduled scraping")
        
        active_sources = self.source_service.get_active_sources()
        tasks = []
        
        for source in active_sources:
            if self._is_due_for_scraping(source):
                task = self._scrape_single_source(source)
                tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            total_incidents = 0
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error scraping source {active_sources[i].name}: {result}")
                else:
                    total_incidents += len(result)
                    logger.info(f"Scraped {len(result)} incidents from {active_sources[i].name}")
            
            logger.info(f"Scraping completed. Total new incidents: {total_incidents}")
        else:
            logger.info("No sources due for scraping")

    async def scrape_all_sources(self):
        """Force scrape all active sources"""
        logger.info("Starting forced scraping of all sources")
        
        active_sources = self.source_service.get_active_sources()
        tasks = []
        
        for source in active_sources:
            task = self._scrape_single_source(source)
            tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            total_incidents = 0
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error scraping source {active_sources[i].name}: {result}")
                else:
                    total_incidents += len(result)
                    logger.info(f"Scraped {len(result)} incidents from {active_sources[i].name}")
            
            logger.info(f"Forced scraping completed. Total new incidents: {total_incidents}")

    async def _scrape_single_source(self, source: models.Source) -> List[Dict[str, Any]]:
        """Scrape a single source and save incidents"""
        try:
            logger.info(f"Scraping source: {source.name}")
            
            # Scrape the source
            raw_incidents = await scrape_source(source.source_type, source.url, source.name)
            
            # Process and save incidents
            saved_incidents = []
            for raw_incident in raw_incidents:
                # Check if incident already exists
                if not self._incident_exists(raw_incident, source.id):
                    incident_data = self._process_raw_incident(raw_incident, source.id)
                    
                    # Create incident
                    incident = self.incident_service.create_incident(
                        schemas.CyberIncidentCreate(**incident_data)
                    )
                    saved_incidents.append(incident)
            
            # Update source last_scraped timestamp
            source.last_scraped = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Saved {len(saved_incidents)} new incidents from {source.name}")
            return saved_incidents
            
        except Exception as e:
            logger.error(f"Error scraping source {source.name}: {e}")
            raise

    def _is_due_for_scraping(self, source: models.Source) -> bool:
        """Check if a source is due for scraping based on its interval"""
        if not source.last_scraped:
            return True
        
        time_since_last_scrape = datetime.utcnow() - source.last_scraped
        return time_since_last_scrape.total_seconds() >= source.scraping_interval

    def _incident_exists(self, raw_incident: Dict[str, Any], source_id) -> bool:
        """Check if an incident already exists in the database"""
        # Check by URL if available
        if raw_incident.get('url'):
            existing = self.db.query(models.CyberIncident)\
                             .filter(models.CyberIncident.url == raw_incident['url'])\
                             .first()
            if existing:
                return True
        
        # Check by external_id if available
        if raw_incident.get('external_id'):
            existing = self.db.query(models.CyberIncident)\
                             .filter(models.CyberIncident.external_id == raw_incident['external_id'])\
                             .first()
            if existing:
                return True
        
        # Check by title and source (fuzzy match)
        existing = self.db.query(models.CyberIncident)\
                         .filter(
                             models.CyberIncident.title == raw_incident.get('title', ''),
                             models.CyberIncident.source_id == source_id
                         )\
                         .first()
        
        return existing is not None

    def _process_raw_incident(self, raw_incident: Dict[str, Any], source_id) -> Dict[str, Any]:
        """Process raw incident data and prepare for database insertion"""
        
        # Determine sector based on content
        sector_id = self._determine_sector(raw_incident)
        
        # Determine APT group if mentioned
        apt_group_id = self._determine_apt_group(raw_incident)
        
        incident_data = {
            'title': raw_incident.get('title', ''),
            'description': raw_incident.get('description', ''),
            'content': raw_incident.get('content', ''),
            'severity': models.IncidentSeverity(raw_incident.get('severity', 'medium')),
            'source_id': source_id,
            'apt_group_id': apt_group_id,
            'sector_id': sector_id,
            'incident_date': raw_incident.get('incident_date', datetime.utcnow()),
            'url': raw_incident.get('url'),
            'external_id': raw_incident.get('external_id'),
            'tags': raw_incident.get('tags', []),
            'indicators_of_compromise': raw_incident.get('indicators_of_compromise', {}),
            'geographical_location': raw_incident.get('geographical_location'),
            'affected_systems': raw_incident.get('affected_systems', []),
            'mitigation_steps': raw_incident.get('mitigation_steps'),
            'relevance_score': raw_incident.get('relevance_score', 0.5),
            'is_verified': False  # New incidents start as unverified
        }
        
        return incident_data

    def _determine_sector(self, raw_incident: Dict[str, Any]) -> str:
        """Determine the most likely sector based on incident content"""
        content = f"{raw_incident.get('title', '')} {raw_incident.get('description', '')}"
        content_lower = content.lower()
        
        sector_keywords = {
            'banking': ['bank', 'financial', 'payment', 'atm', 'credit card', 'sbi', 'icici', 'hdfc'],
            'government': ['government', 'ministry', 'dept', 'department', 'gov.in', 'nic', 'digital india'],
            'healthcare': ['hospital', 'medical', 'health', 'patient', 'aiims', 'healthcare'],
            'energy': ['power', 'electricity', 'grid', 'ntpc', 'ongc', 'oil', 'gas', 'energy'],
            'telecom': ['telecom', 'mobile', 'phone', 'airtel', 'jio', 'bsnl', 'network'],
            'defense': ['defense', 'military', 'army', 'navy', 'air force', 'drdo', 'isro'],
            'education': ['university', 'college', 'school', 'education', 'student', 'academic'],
            'retail': ['retail', 'shopping', 'ecommerce', 'flipkart', 'amazon', 'store']
        }
        
        for sector_type, keywords in sector_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                sector = self.db.query(models.Sector)\
                               .filter(models.Sector.sector_type == models.SectorType(sector_type))\
                               .first()
                if sector:
                    return sector.id
        
        # Default to 'other' sector
        other_sector = self.db.query(models.Sector)\
                             .filter(models.Sector.sector_type == models.SectorType.other)\
                             .first()
        return other_sector.id if other_sector else None

    def _determine_apt_group(self, raw_incident: Dict[str, Any]) -> str:
        """Determine if an APT group is mentioned in the incident"""
        content = f"{raw_incident.get('title', '')} {raw_incident.get('description', '')}"
        content_lower = content.lower()
        
        apt_groups = self.db.query(models.APTGroup).all()
        
        for apt_group in apt_groups:
            # Check group name
            if apt_group.name.lower() in content_lower:
                return apt_group.id
            
            # Check aliases
            if apt_group.aliases:
                for alias in apt_group.aliases:
                    if alias.lower() in content_lower:
                        return apt_group.id
        
        return None