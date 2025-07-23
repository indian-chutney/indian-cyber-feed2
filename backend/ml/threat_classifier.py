import spacy
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from typing import List, Dict, Any, Tuple
import numpy as np
from app.models.models import IncidentSeverity
import re
import os

class ThreatClassifier:
    """ML model for classifying cyber threats and determining relevance to Indian cyber space"""
    
    def __init__(self):
        self.nlp = None
        self.severity_classifier = None
        self.relevance_classifier = None
        self.category_classifier = None
        self.models_loaded = False
        
    def load_models(self):
        """Load pre-trained models or train new ones if they don't exist"""
        try:
            # Load spaCy model
            self.nlp = spacy.load("en_core_web_sm")
            
            # Try to load existing models
            models_dir = "ml/models"
            if os.path.exists(f"{models_dir}/severity_classifier.pkl"):
                with open(f"{models_dir}/severity_classifier.pkl", 'rb') as f:
                    self.severity_classifier = pickle.load(f)
                    
            if os.path.exists(f"{models_dir}/relevance_classifier.pkl"):
                with open(f"{models_dir}/relevance_classifier.pkl", 'rb') as f:
                    self.relevance_classifier = pickle.load(f)
                    
            if os.path.exists(f"{models_dir}/category_classifier.pkl"):
                with open(f"{models_dir}/category_classifier.pkl", 'rb') as f:
                    self.category_classifier = pickle.load(f)
            
            # If models don't exist, train them with sample data
            if not all([self.severity_classifier, self.relevance_classifier, self.category_classifier]):
                self._train_models()
                
            self.models_loaded = True
            
        except Exception as e:
            print(f"Error loading models: {e}")
            self._train_models()

    def _train_models(self):
        """Train classification models with sample data"""
        print("Training ML models...")
        
        # Sample training data (in production, this would come from a larger dataset)
        training_data = self._get_sample_training_data()
        
        # Train severity classifier
        self._train_severity_classifier(training_data)
        
        # Train relevance classifier
        self._train_relevance_classifier(training_data)
        
        # Train category classifier
        self._train_category_classifier(training_data)
        
        # Save models
        self._save_models()

    def _get_sample_training_data(self) -> List[Dict[str, Any]]:
        """Generate sample training data for ML models"""
        return [
            {
                'text': 'Critical vulnerability in Indian banking system allows unauthorized access',
                'severity': 'critical',
                'relevance': 1.0,
                'category': 'vulnerability'
            },
            {
                'text': 'Ransomware attack targets major Indian corporation data breach',
                'severity': 'high',
                'relevance': 0.9,
                'category': 'malware'
            },
            {
                'text': 'Phishing campaign targeting Indian government employees',
                'severity': 'medium',
                'relevance': 0.8,
                'category': 'phishing'
            },
            {
                'text': 'DDoS attack on Indian e-commerce platform during festival season',
                'severity': 'high',
                'relevance': 0.9,
                'category': 'ddos'
            },
            {
                'text': 'APT group targets Indian defense contractors with sophisticated malware',
                'severity': 'critical',
                'relevance': 1.0,
                'category': 'apt'
            },
            {
                'text': 'Data leak exposes Indian citizen Aadhaar information on dark web',
                'severity': 'high',
                'relevance': 1.0,
                'category': 'data_breach'
            },
            {
                'text': 'Minor security update for international software package',
                'severity': 'low',
                'relevance': 0.1,
                'category': 'vulnerability'
            },
            {
                'text': 'Global malware campaign affects systems worldwide',
                'severity': 'medium',
                'relevance': 0.3,
                'category': 'malware'
            },
            {
                'text': 'CERT-In issues advisory for critical infrastructure protection',
                'severity': 'high',
                'relevance': 1.0,
                'category': 'advisory'
            },
            {
                'text': 'Indian Railways cybersecurity incident disrupts booking system',
                'severity': 'high',
                'relevance': 1.0,
                'category': 'infrastructure'
            }
        ]

    def _train_severity_classifier(self, training_data: List[Dict[str, Any]]):
        """Train the severity classification model"""
        texts = [item['text'] for item in training_data]
        severities = [item['severity'] for item in training_data]
        
        self.severity_classifier = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=1000, stop_words='english')),
            ('classifier', MultinomialNB())
        ])
        
        self.severity_classifier.fit(texts, severities)

    def _train_relevance_classifier(self, training_data: List[Dict[str, Any]]):
        """Train the relevance scoring model"""
        texts = [item['text'] for item in training_data]
        relevances = [1 if item['relevance'] > 0.5 else 0 for item in training_data]
        
        self.relevance_classifier = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=1000, stop_words='english')),
            ('classifier', MultinomialNB())
        ])
        
        self.relevance_classifier.fit(texts, relevances)

    def _train_category_classifier(self, training_data: List[Dict[str, Any]]):
        """Train the category classification model"""
        texts = [item['text'] for item in training_data]
        categories = [item['category'] for item in training_data]
        
        self.category_classifier = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=1000, stop_words='english')),
            ('classifier', MultinomialNB())
        ])
        
        self.category_classifier.fit(texts, categories)

    def _save_models(self):
        """Save trained models to disk"""
        models_dir = "ml/models"
        os.makedirs(models_dir, exist_ok=True)
        
        with open(f"{models_dir}/severity_classifier.pkl", 'wb') as f:
            pickle.dump(self.severity_classifier, f)
            
        with open(f"{models_dir}/relevance_classifier.pkl", 'wb') as f:
            pickle.dump(self.relevance_classifier, f)
            
        with open(f"{models_dir}/category_classifier.pkl", 'wb') as f:
            pickle.dump(self.category_classifier, f)

    def classify_incident(self, title: str, description: str = "", content: str = "") -> Dict[str, Any]:
        """Classify an incident and return predictions"""
        if not self.models_loaded:
            self.load_models()
        
        # Combine all text
        full_text = f"{title} {description} {content}".strip()
        
        # Extract features
        entities = self._extract_entities(full_text)
        keywords = self._extract_security_keywords(full_text)
        indian_relevance = self._calculate_indian_relevance(full_text)
        
        # Predict severity
        severity = self.predict_severity(full_text)
        
        # Predict category
        category = self.predict_category(full_text)
        
        # Calculate relevance score
        relevance_score = self.calculate_relevance_score(full_text)
        
        return {
            'severity': severity,
            'category': category,
            'relevance_score': relevance_score,
            'entities': entities,
            'keywords': keywords,
            'indian_relevance': indian_relevance
        }

    def predict_severity(self, text: str) -> str:
        """Predict incident severity"""
        if not self.severity_classifier:
            return 'medium'  # Default
        
        try:
            prediction = self.severity_classifier.predict([text])[0]
            return prediction
        except:
            return 'medium'

    def predict_category(self, text: str) -> str:
        """Predict incident category"""
        if not self.category_classifier:
            return 'unknown'  # Default
        
        try:
            prediction = self.category_classifier.predict([text])[0]
            return prediction
        except:
            return 'unknown'

    def calculate_relevance_score(self, text: str) -> float:
        """Calculate relevance score for Indian cyber space"""
        if not self.relevance_classifier:
            return self._calculate_indian_relevance(text)
        
        try:
            # Get probability of being relevant
            probabilities = self.relevance_classifier.predict_proba([text])[0]
            relevance_prob = probabilities[1] if len(probabilities) > 1 else 0.5
            
            # Combine with keyword-based relevance
            keyword_relevance = self._calculate_indian_relevance(text)
            
            # Weighted average
            final_score = (relevance_prob * 0.7) + (keyword_relevance * 0.3)
            return min(max(final_score, 0.0), 1.0)
        except:
            return self._calculate_indian_relevance(text)

    def _extract_entities(self, text: str) -> List[Dict[str, str]]:
        """Extract named entities from text using spaCy"""
        if not self.nlp:
            return []
        
        try:
            doc = self.nlp(text)
            entities = []
            
            for ent in doc.ents:
                entities.append({
                    'text': ent.text,
                    'label': ent.label_,
                    'description': spacy.explain(ent.label_) or ent.label_
                })
            
            return entities
        except:
            return []

    def _extract_security_keywords(self, text: str) -> List[str]:
        """Extract security-related keywords"""
        security_keywords = [
            'malware', 'ransomware', 'phishing', 'ddos', 'vulnerability', 'exploit',
            'breach', 'attack', 'threat', 'apt', 'backdoor', 'trojan', 'virus',
            'spyware', 'botnet', 'zero-day', 'cve', 'patch', 'mitigation'
        ]
        
        text_lower = text.lower()
        found_keywords = []
        
        for keyword in security_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords

    def _calculate_indian_relevance(self, text: str) -> float:
        """Calculate relevance to Indian cyber space using keywords"""
        indian_keywords = {
            'high_relevance': [
                'india', 'indian', 'cert-in', 'nciipc', 'meity', 'dit',
                'aadhaar', 'upi', 'digital india', 'cii', 'bharat'
            ],
            'medium_relevance': [
                'mumbai', 'delhi', 'bangalore', 'hyderabad', 'chennai', 'kolkata',
                'pune', 'ahmedabad', 'surat', 'jaipur', 'lucknow', 'kanpur'
            ],
            'low_relevance': [
                'south asia', 'asia pacific', 'apac', 'emerging markets'
            ]
        }
        
        text_lower = text.lower()
        score = 0.0
        
        # High relevance keywords
        for keyword in indian_keywords['high_relevance']:
            if keyword in text_lower:
                score += 0.3
        
        # Medium relevance keywords
        for keyword in indian_keywords['medium_relevance']:
            if keyword in text_lower:
                score += 0.1
        
        # Low relevance keywords
        for keyword in indian_keywords['low_relevance']:
            if keyword in text_lower:
                score += 0.05
        
        # Cap the score at 1.0
        return min(score, 1.0)

class PlatformDiscovery:
    """ML-based platform discovery for finding new threat intelligence sources"""
    
    def __init__(self):
        self.nlp = None
        self.discovery_patterns = [
            r'security\s+(blog|feed|advisory)',
            r'vulnerability\s+(database|tracker|feed)',
            r'threat\s+(intelligence|research|analysis)',
            r'cyber\s+(security|threat|incident)',
            r'(cert|csirt|soc)\s+(advisory|bulletin|alert)',
            r'malware\s+(analysis|research|tracker)',
            r'(breach|leak|compromise)\s+(report|notification)'
        ]

    def discover_platforms(self, search_queries: List[str]) -> List[Dict[str, Any]]:
        """Discover potential threat intelligence platforms"""
        discovered_platforms = []
        
        for query in search_queries:
            # This would integrate with search engines or web crawling
            # For now, return sample platforms
            platforms = self._simulate_platform_discovery(query)
            discovered_platforms.extend(platforms)
        
        return discovered_platforms

    def _simulate_platform_discovery(self, query: str) -> List[Dict[str, Any]]:
        """Simulate platform discovery (replace with actual search logic)"""
        sample_platforms = [
            {
                'name': 'Indian Cyber Security Blog',
                'url': 'https://example-indian-cybersec.com',
                'type': 'blog',
                'relevance_score': 0.8,
                'description': 'Blog focused on Indian cybersecurity incidents'
            },
            {
                'name': 'CERT-In RSS Feed',
                'url': 'https://cert-in.org.in/rss.xml',
                'type': 'security_feed',
                'relevance_score': 1.0,
                'description': 'Official CERT-In security advisories'
            }
        ]
        
        # Filter based on query relevance
        return [p for p in sample_platforms if query.lower() in p['description'].lower()]

# Initialize global classifier instance
threat_classifier = ThreatClassifier()
platform_discovery = PlatformDiscovery()