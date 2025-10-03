# JobHunt Pro - Job Listings Backend

A powerful Flask-based RESTful API backend for the [JobHunt Pro](https://github.com/brocode-01/Job_Listing_Frontend.git) application. Features intelligent job scraping from LinkedIn with advanced filtering and prioritization.

## 🔗 Project Components

- **Frontend**: [Job-Listing-Frontend](https://github.com/brocode-01/Job_Listing_Frontend.git)
  - Modern React-based UI
  - Responsive design
  - Real-time job updates
  - Advanced search and filtering
  - Beautiful job cards
  - Intuitive user interface

- **Backend** (This Repository):
  - RESTful API
  - LinkedIn job scraping
  - Database management
  - Job analytics
  - Search optimization

## 🌟 Features

- **RESTful API Integration**
  - Complete CRUD operations for job listings
  - Advanced filtering and sorting
  - Real-time statistics and metrics
  - Health monitoring endpoint
  - Frontend-ready response format
  - CORS enabled for frontend

- **Intelligent LinkedIn Scraping**
  - Automated job scraping with smart filtering
  - Focus on full-time, mid to senior positions
  - Advanced job prioritization system
  - Technology-aware ranking
  - Quality-based sorting
  - Last 24 hours listings

- **Data Management**
  - SQLite database with SQLAlchemy ORM
  - Efficient query optimization
  - Data validation and sanitization
  - Error handling and logging

## 🚀 Getting Started

### Prerequisites

- Python 3.x
- Chrome WebDriver
- Virtual environment (recommended)
- Frontend repository cloned (optional)

### Installation

1. Clone both repositories:
```bash
# Clone backend
git clone <backend-repository-url>
cd job-listings-backend

# Clone frontend (in a different directory)
git clone https://github.com/brocode-01/Job_Listing_Frontend.git
```

2. Setup backend:
```bash
# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Chrome WebDriver
# Download from https://chromedriver.chromium.org/
# Add to system PATH
```

3. Start the backend server:
```bash
python app.py
```
The API will be available at `http://localhost:5000`

4. Setup frontend (optional):
```bash
cd Job-Listing-Frontend
npm install
npm start
```
The frontend will be available at `http://localhost:3000`

## 📁 Project Structure

```
job-listings-backend/
├── app.py              # Application entry point
├── routes.py           # API route definitions
├── models.py           # Database models
├── database.py         # Database configuration
├── selenium_scraper.py # Intelligent LinkedIn scraping
└── requirements.txt    # Project dependencies
```

## 🔌 API Endpoints

### Jobs
- `GET /api/jobs`
  - Get all jobs with filtering and sorting
  - Query Parameters:
    - `location`: Filter by location
    - `company`: Filter by company
    - `job_type`: Filter by job type
    - `experience`: Filter by experience level
    - `sort_by`: Sort by field (title, company, location, posted_date)
    - `sort_order`: Sort order (asc, desc)
  - Used by: Frontend job listing page

- `POST /api/jobs`
  - Create new job listing
  - Required fields: title, company, location
  - Used by: Frontend job posting form

- `PUT /api/jobs/<job_id>`
  - Update existing job
  - Used by: Frontend job edit form

- `DELETE /api/jobs/<job_id>`
  - Remove job listing
  - Used by: Frontend job management

### Job Scraping
- `POST /api/scrape` or `GET /api/scrape`
  - Scrape top 5 software engineering jobs from LinkedIn
  - Smart filtering and prioritization:
    - Full-time positions only
    - Mid to senior level roles
    - Technology-focused positions
    - Quality job descriptions
  - Used by: Frontend scraping trigger button
  - Returns:
    ```json
    {
      "message": "Successfully scraped top software engineering jobs",
      "total_scraped": 5,
      "added": 3,
      "jobs": [
        {
          "id": 1,
          "title": "Senior Software Engineer",
          "company": "Tech Corp",
          "location": "Remote",
          "salary": "$150,000 - $200,000",
          "job_type": "Full-time",
          "experience_level": "Senior",
          "application_url": "https://linkedin.com/jobs/...",
          "posted_date": "2024-01-01T00:00:00",
          "scraped": true
        }
      ]
    }
    ```

### Statistics
- `GET /api/stats`
  - Get job statistics
  - Returns counts of total, scraped, and manual jobs
  - Lists top companies and locations
  - Used by: Frontend dashboard

### System
- `GET /api/health`
  - Health check endpoint
  - Returns system status and timestamp
  - Used by: Frontend system status

## 🛠️ Development

### Database Schema

The `Job` model includes:
- `id`: Integer (Primary Key)
- `title`: String (Required)
- `company`: String (Required)
- `location`: String (Required)
- `description`: Text
- `salary`: String
- `job_type`: String
- `experience_level`: String
- `application_url`: String
- `posted_date`: DateTime
- `scraped`: Boolean

### LinkedIn Scraping Features

The scraper includes sophisticated job filtering and ranking:

**Smart Filtering**:
- Full-time positions only
- Mid to senior level roles
- Easy apply jobs
- Last 24 hours listings
- Technology-focused positions

**Priority Scoring System**:
- Experience Level Weighting:
  - Senior roles (+5 points)
  - Mid-level roles (+3 points)
  - Junior/Intern roles (-2 points)
- Position Type Impact:
  - Permanent roles preferred
  - Internships/temporary (-3 points)
- Technology Bonuses:
  - Popular tech stack mentions (+2 each)
  - Includes: Python, JavaScript, React, Node, AWS, etc.
- Location Benefits:
  - Remote positions (+2 points)
- Quality Metrics:
  - Salary information available
  - Detailed job descriptions
  - Easy application process

**Technical Features**:
- Headless browser operation
- Anti-detection measures
- Efficient data extraction
- Automatic error recovery
- Resource optimization

## 🔒 Security Features

- CORS protection for frontend integration
- Input validation
- SQL injection prevention
- Scraper anti-detection
- Error handling and logging
