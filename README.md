# Indian Cyber Threat Intelligence Platform

A comprehensive framework to crawl, collect, and analyze cyber incident activities specific to Indian cyber space for protecting Critical Information Infrastructure (CIIs).

## Features

- **Machine Learning Platform Discovery**: ML models to identify platforms that publish cyber incident activities
- **Data Collection Framework**: Robust cyber incidents feed generator with multi-source scrapers
- **Advanced Analytics**: Interactive dashboard with visualizations for threat trends and patterns
- **Real-time Processing**: WebSocket-based real-time updates and notifications
- **Comprehensive Database**: Well-structured PostgreSQL database with full-text search
- **REST API**: FastAPI-based API with authentication and authorization
- **Modern Frontend**: React-based interactive dashboard with Material-UI components

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/indian-chutney/indian-cyber-feed2.git
   cd indian-cyber-feed2
   ```

2. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - Frontend Dashboard: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/api/docs

### Manual Setup

1. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   
   # Setup environment variables
   cp config/.env.example .env
   
   # Run database migrations
   alembic upgrade head
   
   # Start the backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm start
   ```

3. **Database Setup**
   ```bash
   # Create PostgreSQL database
   createdb cyber_intelligence
   
   # Run initialization script
   psql cyber_intelligence < database/init.sql
   ```

## Architecture

### Backend Components

- **FastAPI Application** (`backend/app/`): REST API with WebSocket support
- **Data Models** (`backend/app/models/`): SQLAlchemy models and Pydantic schemas
- **Services** (`backend/app/services/`): Business logic layer
- **Scrapers** (`backend/scrapers/`): Web scrapers for various platforms
- **ML Components** (`backend/ml/`): Machine learning models for threat classification
- **Authentication** (`backend/app/auth/`): JWT-based authentication system

### Frontend Components

- **React Application** (`frontend/src/`): Modern SPA with Material-UI
- **Dashboard** (`frontend/src/pages/Dashboard.js`): Main dashboard with threat overview
- **Incidents** (`frontend/src/pages/Incidents.js`): Incident management interface
- **Analytics** (`frontend/src/pages/Analytics.js`): Advanced analytics and visualizations
- **Sources** (`frontend/src/pages/Sources.js`): Data source management

### Database Schema

- **cyber_incidents**: Main incidents table with metadata
- **sources**: Data source configuration
- **apt_groups**: Advanced Persistent Threat groups
- **sectors**: Indian sector classification
- **classifications**: ML-based threat categorization
- **users**: User authentication and authorization

## API Endpoints

### Authentication
- `POST /api/auth/token` - Login and get access token
- `POST /api/auth/register` - Register new user
- `GET /api/auth/me` - Get current user info

### Incidents
- `GET /api/incidents` - List incidents with filtering
- `GET /api/incidents/{id}` - Get specific incident
- `POST /api/incidents` - Create new incident
- `PUT /api/incidents/{id}` - Update incident
- `DELETE /api/incidents/{id}` - Delete incident

### Analytics
- `GET /api/analytics/trends` - Get incident trends
- `GET /api/analytics/apt-activity` - Get APT group activity
- `GET /api/analytics/sector-analysis` - Get sector-wise analysis
- `GET /api/analytics/threat-intelligence` - Get threat intelligence summary

### Sources
- `GET /api/sources` - List data sources
- `POST /api/sources` - Create new source
- `PUT /api/sources/{id}` - Update source
- `DELETE /api/sources/{id}` - Delete source
- `POST /api/sources/{id}/scrape` - Trigger manual scraping

## Data Sources

The platform supports multiple types of data sources:

- **Security Feeds**: CERT-In advisories, security bulletins
- **GitHub**: Security advisories and vulnerability reports
- **Paste Sites**: Monitoring for potential data leaks
- **Blogs**: Security research and threat intelligence blogs
- **Forums**: Cybersecurity discussion forums
- **Social Media**: Security-related social media monitoring

## Machine Learning Features

- **Threat Classification**: Automatic categorization of cyber incidents
- **Severity Assessment**: ML-based severity scoring
- **Relevance Scoring**: Indian cyber space relevance calculation
- **Platform Discovery**: Automatic discovery of new threat intelligence sources
- **Anomaly Detection**: Detection of emerging threats and patterns

## Security Features

- JWT-based authentication
- Role-based access control
- Rate limiting
- Input validation and sanitization
- SQL injection prevention
- XSS protection

## Deployment

### Production Deployment

1. **Update configuration**
   ```bash
   cp config/.env.production .env
   # Edit .env with production values
   ```

2. **Deploy with Docker**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

### Environment Variables

Key environment variables:

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`: JWT secret key
- `API_HOST`: API host address
- `API_PORT`: API port number
- `DEBUG`: Debug mode flag

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the GitHub repository
- Contact the development team

## Roadmap

- [ ] Advanced threat correlation
- [ ] Integration with threat intelligence feeds
- [ ] Mobile application
- [ ] Advanced visualization with D3.js
- [ ] Machine learning model improvements
- [ ] Real-time alerting system
- [ ] API rate limiting enhancements
- [ ] Multi-language support