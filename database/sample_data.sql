-- Sample cyber incident data for testing the Indian Cyber Threat Intelligence Platform

-- Insert sample incidents
INSERT INTO cyber_incidents (
    title, 
    description, 
    content, 
    severity, 
    status, 
    source_id, 
    incident_date, 
    url, 
    tags, 
    indicators_of_compromise,
    geographical_location,
    affected_systems,
    relevance_score
) VALUES 
(
    'Critical Banking Trojan Targets Indian Financial Institutions',
    'A sophisticated banking trojan has been detected targeting major Indian banks including SBI, ICICI, and HDFC.',
    'Security researchers have discovered a new variant of the banking trojan specifically designed to steal credentials from Indian banking customers. The malware uses advanced evasion techniques and targets popular banking applications.',
    'critical',
    'investigating',
    (SELECT id FROM sources WHERE name = 'CERT-In Advisories' LIMIT 1),
    '2024-01-15 10:30:00',
    'https://cert-in.org.in/s2cMainServlet?pageid=PUBVLNOTES01&VLCODE=CIVN-2024-0001',
    ARRAY['banking', 'trojan', 'malware', 'credentials'],
    '{"hashes": ["md5:a1b2c3d4e5f6g7h8i9j0", "sha256:1234567890abcdef"], "domains": ["malicious-bank.com", "fake-sbi.net"], "ips": ["192.168.1.100", "10.0.0.50"]}',
    'India',
    ARRAY['Online Banking Systems', 'Mobile Banking Apps', 'ATM Networks'],
    0.95
),
(
    'Government Portal Vulnerability Exposes Citizen Data',
    'A critical vulnerability in a government e-governance portal has been discovered that could expose sensitive citizen information.',
    'Security audit of the Digital India portal revealed SQL injection vulnerabilities that could allow unauthorized access to Aadhaar-linked data and other sensitive citizen information.',
    'high',
    'open',
    (SELECT id FROM sources WHERE name = 'CERT-In Advisories' LIMIT 1),
    '2024-01-14 14:20:00',
    'https://cert-in.org.in/s2cMainServlet?pageid=PUBVLNOTES01&VLCODE=CIVN-2024-0002',
    ARRAY['government', 'vulnerability', 'data_breach', 'sql_injection'],
    '{"cve": "CVE-2024-0001", "affected_versions": ["v2.1", "v2.2"], "patches": ["patch-2024-001"]}',
    'India',
    ARRAY['Government Portals', 'Citizen Database', 'Aadhaar System'],
    1.0
),
(
    'APT Group Targets Indian Defense Contractors',
    'Advanced Persistent Threat group believed to be state-sponsored has been targeting Indian defense contractors with spear-phishing campaigns.',
    'The APT group, tracked as "Operation Digital Siege", has been conducting targeted attacks against Indian defense organizations using sophisticated spear-phishing emails and custom malware.',
    'critical',
    'investigating',
    (SELECT id FROM sources WHERE name = 'GitHub Security Advisories' LIMIT 1),
    '2024-01-13 09:15:00',
    'https://github.com/advisories/GHSA-xxxx-yyyy-zzzz',
    ARRAY['apt', 'defense', 'spear_phishing', 'state_sponsored'],
    '{"campaign": "Operation Digital Siege", "techniques": ["T1566.001", "T1059.001"], "targets": ["defense", "aerospace"]}',
    'India',
    ARRAY['Defense Networks', 'Contractor Systems', 'R&D Facilities'],
    0.98
),
(
    'Ransomware Attack on Indian Healthcare System',
    'Major Indian hospital chain hit by ransomware attack, disrupting patient care services across multiple facilities.',
    'The WannaCry variant specifically targeted the hospital management systems, encrypting patient records and disrupting critical healthcare services across 15 facilities.',
    'high',
    'resolved',
    (SELECT id FROM sources WHERE name = 'Security News India' LIMIT 1),
    '2024-01-12 16:45:00',
    'https://example-security-blog.com/ransomware-healthcare-india',
    ARRAY['ransomware', 'healthcare', 'wannacry', 'patient_data'],
    '{"ransomware_family": "WannaCry", "ransom_amount": "$50000", "recovery_time": "72 hours"}',
    'Mumbai, India',
    ARRAY['Hospital Management Systems', 'Patient Records Database', 'Medical Equipment'],
    0.92
),
(
    'Cryptocurrency Exchange Security Breach',
    'Indian cryptocurrency exchange reports unauthorized access to user wallets and trading data.',
    'Security incident at major Indian crypto exchange resulted in unauthorized access to approximately 10,000 user accounts and theft of digital assets worth $2 million.',
    'high',
    'investigating',
    (SELECT id FROM sources WHERE name = 'Pastebin Security' LIMIT 1),
    '2024-01-11 11:30:00',
    'https://pastebin.com/crypto-breach-india',
    ARRAY['cryptocurrency', 'data_breach', 'financial', 'unauthorized_access'],
    '{"stolen_amount": "$2000000", "affected_users": 10000, "cryptocurrencies": ["BTC", "ETH", "INR"]}',
    'Bangalore, India',
    ARRAY['Trading Platform', 'User Wallets', 'KYC Database'],
    0.88
);

-- Update APT group associations
UPDATE cyber_incidents 
SET apt_group_id = (SELECT id FROM apt_groups WHERE name = 'APT1' LIMIT 1)
WHERE title LIKE '%APT Group%';

-- Update sector associations
UPDATE cyber_incidents 
SET sector_id = (SELECT id FROM sectors WHERE sector_type = 'banking' LIMIT 1)
WHERE title LIKE '%Banking%';

UPDATE cyber_incidents 
SET sector_id = (SELECT id FROM sectors WHERE sector_type = 'government' LIMIT 1)
WHERE title LIKE '%Government%';

UPDATE cyber_incidents 
SET sector_id = (SELECT id FROM sectors WHERE sector_type = 'defense' LIMIT 1)
WHERE title LIKE '%Defense%';

UPDATE cyber_incidents 
SET sector_id = (SELECT id FROM sectors WHERE sector_type = 'healthcare' LIMIT 1)
WHERE title LIKE '%Healthcare%';

-- Insert sample classifications
INSERT INTO incident_classifications (incident_id, classification_id, confidence_score)
SELECT 
    ci.id,
    c.id,
    CASE 
        WHEN 'malware' = ANY(ci.tags) AND c.name = 'Malware Attack' THEN 0.95
        WHEN 'vulnerability' = ANY(ci.tags) AND c.name = 'Vulnerability Disclosure' THEN 0.90
        WHEN 'apt' = ANY(ci.tags) AND c.name = 'APT Campaign' THEN 0.98
        WHEN 'ransomware' = ANY(ci.tags) AND c.name = 'Malware Attack' THEN 0.92
        WHEN 'data_breach' = ANY(ci.tags) AND c.name = 'Data Breach' THEN 0.88
        ELSE 0.70
    END
FROM cyber_incidents ci
CROSS JOIN classifications c
WHERE 
    ('malware' = ANY(ci.tags) AND c.name = 'Malware Attack') OR
    ('vulnerability' = ANY(ci.tags) AND c.name = 'Vulnerability Disclosure') OR
    ('apt' = ANY(ci.tags) AND c.name = 'APT Campaign') OR
    ('ransomware' = ANY(ci.tags) AND c.name = 'Malware Attack') OR
    ('data_breach' = ANY(ci.tags) AND c.name = 'Data Breach');

-- Create a test user (password: testpassword)
INSERT INTO users (username, email, hashed_password, is_active, is_admin)
VALUES (
    'admin',
    'admin@cyberintel.gov.in',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewrF3Frx3MjM6gSO', -- bcrypt hash for 'testpassword'
    true,
    true
);

-- Insert additional test user
INSERT INTO users (username, email, hashed_password, is_active, is_admin)
VALUES (
    'analyst',
    'analyst@cyberintel.gov.in',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewrF3Frx3MjM6gSO', -- bcrypt hash for 'testpassword'
    true,
    false
);