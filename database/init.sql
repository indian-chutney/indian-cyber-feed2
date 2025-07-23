-- Database initialization script
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create enum types
CREATE TYPE incident_severity AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE incident_status AS ENUM ('open', 'investigating', 'resolved', 'false_positive');
CREATE TYPE source_type AS ENUM ('forum', 'paste_site', 'social_media', 'blog', 'github', 'security_feed', 'news');
CREATE TYPE sector_type AS ENUM ('banking', 'government', 'healthcare', 'energy', 'telecom', 'defense', 'education', 'retail', 'other');

-- Sources table
CREATE TABLE sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    url TEXT NOT NULL,
    source_type source_type NOT NULL,
    is_active BOOLEAN DEFAULT true,
    scraping_interval INTEGER DEFAULT 3600, -- in seconds
    last_scraped TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- APT Groups table
CREATE TABLE apt_groups (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    aliases TEXT[],
    description TEXT,
    origin_country VARCHAR(100),
    first_seen DATE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sectors table
CREATE TABLE sectors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    sector_type sector_type NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cyber Incidents table
CREATE TABLE cyber_incidents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    content TEXT,
    severity incident_severity DEFAULT 'medium',
    status incident_status DEFAULT 'open',
    source_id UUID REFERENCES sources(id),
    apt_group_id UUID REFERENCES apt_groups(id),
    sector_id UUID REFERENCES sectors(id),
    incident_date TIMESTAMP,
    discovered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    url TEXT,
    external_id VARCHAR(255),
    tags TEXT[],
    indicators_of_compromise JSONB,
    geographical_location VARCHAR(255),
    affected_systems TEXT[],
    mitigation_steps TEXT,
    relevance_score FLOAT DEFAULT 0.5,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Classifications table for ML categorization
CREATE TABLE classifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    category VARCHAR(100) NOT NULL,
    description TEXT,
    keywords TEXT[],
    confidence_threshold FLOAT DEFAULT 0.7,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Incident Classifications mapping table
CREATE TABLE incident_classifications (
    incident_id UUID REFERENCES cyber_incidents(id) ON DELETE CASCADE,
    classification_id UUID REFERENCES classifications(id) ON DELETE CASCADE,
    confidence_score FLOAT NOT NULL,
    PRIMARY KEY (incident_id, classification_id)
);

-- Users table for authentication
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    is_admin BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_incidents_severity ON cyber_incidents(severity);
CREATE INDEX idx_incidents_status ON cyber_incidents(status);
CREATE INDEX idx_incidents_date ON cyber_incidents(incident_date);
CREATE INDEX idx_incidents_discovered ON cyber_incidents(discovered_date);
CREATE INDEX idx_incidents_relevance ON cyber_incidents(relevance_score);
CREATE INDEX idx_incidents_sector ON cyber_incidents(sector_id);
CREATE INDEX idx_incidents_apt ON cyber_incidents(apt_group_id);
CREATE INDEX idx_incidents_source ON cyber_incidents(source_id);

-- Full-text search indexes
CREATE INDEX idx_incidents_title_search ON cyber_incidents USING gin(to_tsvector('english', title));
CREATE INDEX idx_incidents_description_search ON cyber_incidents USING gin(to_tsvector('english', description));
CREATE INDEX idx_incidents_content_search ON cyber_incidents USING gin(to_tsvector('english', content));

-- Trigram indexes for fuzzy search
CREATE INDEX idx_incidents_title_trgm ON cyber_incidents USING gin(title gin_trgm_ops);
CREATE INDEX idx_incidents_description_trgm ON cyber_incidents USING gin(description gin_trgm_ops);

-- Insert default sectors
INSERT INTO sectors (name, sector_type, description) VALUES
('Banking and Financial Services', 'banking', 'Banks, financial institutions, payment systems'),
('Government and Public Services', 'government', 'Government agencies, public administration'),
('Healthcare', 'healthcare', 'Hospitals, healthcare providers, medical systems'),
('Energy and Utilities', 'energy', 'Power plants, oil and gas, utilities'),
('Telecommunications', 'telecom', 'Telecom providers, internet services'),
('Defense and Aerospace', 'defense', 'Military, defense contractors, aerospace'),
('Education', 'education', 'Universities, schools, educational institutions'),
('Retail and E-commerce', 'retail', 'Retail companies, e-commerce platforms'),
('Critical Infrastructure', 'other', 'Transportation, water, emergency services');

-- Insert default classifications
INSERT INTO classifications (name, category, description, keywords) VALUES
('Malware Attack', 'malware', 'Malicious software attacks', ARRAY['malware', 'virus', 'trojan', 'ransomware', 'spyware']),
('Phishing', 'social_engineering', 'Email and web-based phishing attacks', ARRAY['phishing', 'spear phishing', 'credential theft']),
('Data Breach', 'data_security', 'Unauthorized access to sensitive data', ARRAY['data breach', 'data leak', 'unauthorized access']),
('DDoS Attack', 'network_security', 'Distributed denial of service attacks', ARRAY['ddos', 'denial of service', 'botnet']),
('APT Campaign', 'advanced_threats', 'Advanced persistent threat activities', ARRAY['apt', 'advanced persistent threat', 'nation state']),
('Vulnerability Disclosure', 'vulnerabilities', 'Security vulnerabilities and exploits', ARRAY['vulnerability', 'exploit', 'zero-day', 'cve']),
('Insider Threat', 'insider_threats', 'Internal security threats', ARRAY['insider threat', 'employee misconduct', 'privilege abuse']);

-- Insert sample APT groups
INSERT INTO apt_groups (name, aliases, description, origin_country, first_seen) VALUES
('APT1', ARRAY['Comment Crew', 'PLA Unit 61398'], 'Chinese military-linked cyber espionage group', 'China', '2006-01-01'),
('Lazarus Group', ARRAY['Hidden Cobra', 'Zinc'], 'North Korean state-sponsored hacking group', 'North Korea', '2009-01-01'),
('APT28', ARRAY['Fancy Bear', 'Sofacy'], 'Russian military intelligence cyber unit', 'Russia', '2007-01-01'),
('APT29', ARRAY['Cozy Bear', 'The Dukes'], 'Russian foreign intelligence service', 'Russia', '2008-01-01'),
('Carbanak', ARRAY['FIN7'], 'Financial crime syndicate', 'Unknown', '2013-01-01');

-- Insert sample sources
INSERT INTO sources (name, url, source_type, scraping_interval) VALUES
('CERT-In Advisories', 'https://www.cert-in.org.in/s2cMainServlet?pageid=PUBVLNOTES01&VLCODE=CIVN-2023', 'security_feed', 3600),
('Indian Computer Emergency Response Team', 'https://www.cert-in.org.in/', 'security_feed', 7200),
('GitHub Security Advisories', 'https://github.com/advisories', 'github', 1800),
('Pastebin Security', 'https://pastebin.com/', 'paste_site', 900),
('Security News India', 'https://example-security-blog.com/rss', 'blog', 3600);

-- Function to update timestamp
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_sources_modtime BEFORE UPDATE ON sources FOR EACH ROW EXECUTE FUNCTION update_modified_column();
CREATE TRIGGER update_incidents_modtime BEFORE UPDATE ON cyber_incidents FOR EACH ROW EXECUTE FUNCTION update_modified_column();
CREATE TRIGGER update_apt_groups_modtime BEFORE UPDATE ON apt_groups FOR EACH ROW EXECUTE FUNCTION update_modified_column();