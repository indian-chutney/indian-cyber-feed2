import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from datetime import datetime
from abc import ABC, abstractmethod
import feedparser
import json
import re
from app.models.models import SourceType

class BaseScraper(ABC):
    def __init__(self, source_url: str, source_name: str):
        self.source_url = source_url
        self.source_name = source_name
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    @abstractmethod
    async def scrape(self) -> List[Dict[str, Any]]:
        pass

    def extract_indian_relevance_keywords(self, text: str) -> float:
        """Calculate relevance score for Indian cyber space"""
        indian_keywords = [
            'india', 'indian', 'cert-in', 'nciipc', 'meity', 'dit',
            'aadhaar', 'upi', 'digital india', 'cii', 'critical information infrastructure',
            'mumbai', 'delhi', 'bangalore', 'hyderabad', 'chennai', 'kolkata',
            'bharat', 'bharti', 'bsnl', 'airtel', 'jio', 'ongc', 'ntpc',
            'sbi', 'icici', 'hdfc', 'axis bank', 'pnb', 'canara bank',
            'indian railways', 'irctc', 'ril', 'tcs', 'infosys', 'wipro'
        ]
        
        text_lower = text.lower()
        matches = sum(1 for keyword in indian_keywords if keyword in text_lower)
        
        # Normalize score between 0 and 1
        return min(matches / 10.0, 1.0)

class CERTInScraper(BaseScraper):
    """Scraper for CERT-In advisories"""
    
    async def scrape(self) -> List[Dict[str, Any]]:
        try:
            async with self.session.get(self.source_url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                incidents = []
                # Parse CERT-In advisory structure
                advisory_rows = soup.find_all('tr')
                
                for row in advisory_rows:
                    cells = row.find_all('td')
                    if len(cells) >= 3:
                        title = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                        date_str = cells[0].get_text(strip=True) if len(cells) > 0 else ""
                        link = cells[1].find('a')['href'] if cells[1].find('a') else ""
                        
                        if title and date_str:
                            incident = {
                                'title': title,
                                'url': f"https://www.cert-in.org.in{link}" if link.startswith('/') else link,
                                'incident_date': self._parse_date(date_str),
                                'severity': self._determine_severity(title),
                                'description': title,
                                'source_type': SourceType.security_feed.value,
                                'geographical_location': 'India',
                                'relevance_score': self.extract_indian_relevance_keywords(title),
                                'tags': self._extract_tags(title)
                            }
                            incidents.append(incident)
                
                return incidents
        except Exception as e:
            print(f"Error scraping CERT-In: {e}")
            return []

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        try:
            # Try different date formats
            for fmt in ['%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d']:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
        except:
            pass
        return datetime.utcnow()

    def _determine_severity(self, title: str) -> str:
        title_lower = title.lower()
        if any(keyword in title_lower for keyword in ['critical', 'high risk', 'severe']):
            return 'critical'
        elif any(keyword in title_lower for keyword in ['high', 'important']):
            return 'high'
        elif any(keyword in title_lower for keyword in ['medium', 'moderate']):
            return 'medium'
        else:
            return 'low'

    def _extract_tags(self, title: str) -> List[str]:
        tags = []
        title_lower = title.lower()
        
        tag_keywords = {
            'malware': ['malware', 'virus', 'trojan', 'ransomware'],
            'vulnerability': ['vulnerability', 'cve', 'exploit', 'patch'],
            'phishing': ['phishing', 'spoofing', 'social engineering'],
            'ddos': ['ddos', 'denial of service', 'botnet'],
            'data_breach': ['data breach', 'leak', 'unauthorized access']
        }
        
        for tag, keywords in tag_keywords.items():
            if any(keyword in title_lower for keyword in keywords):
                tags.append(tag)
        
        return tags

class GitHubAdvisoryScraper(BaseScraper):
    """Scraper for GitHub Security Advisories"""
    
    async def scrape(self) -> List[Dict[str, Any]]:
        try:
            # GitHub Security Advisories API
            api_url = "https://api.github.com/advisories"
            async with self.session.get(api_url) as response:
                advisories = await response.json()
                
                incidents = []
                for advisory in advisories:
                    incident = {
                        'title': advisory.get('summary', ''),
                        'description': advisory.get('description', ''),
                        'url': advisory.get('html_url', ''),
                        'external_id': advisory.get('ghsa_id', ''),
                        'incident_date': datetime.fromisoformat(advisory.get('published_at', '').replace('Z', '+00:00')),
                        'severity': advisory.get('severity', 'medium').lower(),
                        'source_type': SourceType.github.value,
                        'tags': advisory.get('cwe_ids', []),
                        'relevance_score': self.extract_indian_relevance_keywords(
                            f"{advisory.get('summary', '')} {advisory.get('description', '')}"
                        ),
                        'indicators_of_compromise': {
                            'cve_ids': advisory.get('cve_id', ''),
                            'cvss_score': advisory.get('cvss', {}).get('score', 0)
                        }
                    }
                    incidents.append(incident)
                
                return incidents
        except Exception as e:
            print(f"Error scraping GitHub advisories: {e}")
            return []

class PastebinScraper(BaseScraper):
    """Scraper for Pastebin - looking for potential data leaks"""
    
    async def scrape(self) -> List[Dict[str, Any]]:
        try:
            # Note: This is a simplified example. In production, you'd need proper rate limiting
            # and potentially use Pastebin's API
            search_terms = ['india', 'indian', 'database', 'leak', 'breach', 'credentials']
            incidents = []
            
            for term in search_terms:
                search_url = f"https://pastebin.com/search?q={term}"
                async with self.session.get(search_url) as response:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Parse search results (this is a simplified example)
                    results = soup.find_all('div', class_='paste_box_line')
                    
                    for result in results[:5]:  # Limit results
                        title_elem = result.find('a')
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            url = f"https://pastebin.com{title_elem['href']}"
                            
                            incident = {
                                'title': f"Potential data leak: {title}",
                                'description': f"Paste found containing '{term}' keyword",
                                'url': url,
                                'incident_date': datetime.utcnow(),
                                'severity': 'medium',
                                'source_type': SourceType.paste_site.value,
                                'tags': ['data_leak', 'paste_site', term],
                                'relevance_score': self.extract_indian_relevance_keywords(title),
                                'geographical_location': 'Unknown'
                            }
                            incidents.append(incident)
            
            return incidents
        except Exception as e:
            print(f"Error scraping Pastebin: {e}")
            return []

class RSSFeedScraper(BaseScraper):
    """Scraper for RSS feeds from security blogs"""
    
    async def scrape(self) -> List[Dict[str, Any]]:
        try:
            async with self.session.get(self.source_url) as response:
                rss_content = await response.text()
                feed = feedparser.parse(rss_content)
                
                incidents = []
                for entry in feed.entries:
                    incident = {
                        'title': entry.get('title', ''),
                        'description': entry.get('summary', ''),
                        'content': entry.get('content', [{}])[0].get('value', '') if entry.get('content') else '',
                        'url': entry.get('link', ''),
                        'incident_date': datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.utcnow(),
                        'severity': self._determine_severity_from_content(entry.get('title', '') + ' ' + entry.get('summary', '')),
                        'source_type': SourceType.blog.value,
                        'tags': self._extract_tags_from_content(entry.get('title', '') + ' ' + entry.get('summary', '')),
                        'relevance_score': self.extract_indian_relevance_keywords(
                            f"{entry.get('title', '')} {entry.get('summary', '')}"
                        )
                    }
                    incidents.append(incident)
                
                return incidents
        except Exception as e:
            print(f"Error scraping RSS feed: {e}")
            return []

    def _determine_severity_from_content(self, content: str) -> str:
        content_lower = content.lower()
        if any(keyword in content_lower for keyword in ['critical', 'zero-day', 'breach', 'attack']):
            return 'high'
        elif any(keyword in content_lower for keyword in ['vulnerability', 'exploit', 'malware']):
            return 'medium'
        else:
            return 'low'

    def _extract_tags_from_content(self, content: str) -> List[str]:
        tags = []
        content_lower = content.lower()
        
        if 'malware' in content_lower:
            tags.append('malware')
        if 'phishing' in content_lower:
            tags.append('phishing')
        if 'vulnerability' in content_lower:
            tags.append('vulnerability')
        if 'apt' in content_lower:
            tags.append('apt')
        if 'ransomware' in content_lower:
            tags.append('ransomware')
        
        return tags

class ScraperFactory:
    """Factory class to create appropriate scrapers based on source type"""
    
    @staticmethod
    def create_scraper(source_type: SourceType, source_url: str, source_name: str) -> BaseScraper:
        if source_type == SourceType.security_feed:
            if 'cert-in' in source_url.lower():
                return CERTInScraper(source_url, source_name)
            else:
                return RSSFeedScraper(source_url, source_name)
        elif source_type == SourceType.github:
            return GitHubAdvisoryScraper(source_url, source_name)
        elif source_type == SourceType.paste_site:
            return PastebinScraper(source_url, source_name)
        elif source_type == SourceType.blog:
            return RSSFeedScraper(source_url, source_name)
        else:
            return RSSFeedScraper(source_url, source_name)  # Default to RSS

async def scrape_source(source_type: SourceType, source_url: str, source_name: str) -> List[Dict[str, Any]]:
    """Convenience function to scrape a single source"""
    scraper = ScraperFactory.create_scraper(source_type, source_url, source_name)
    async with scraper:
        return await scraper.scrape()