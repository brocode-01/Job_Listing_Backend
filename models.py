from datetime import datetime
from database import db

class Job(db.Model):
    """Job model for storing job listings"""
    
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    company = db.Column(db.String(200), nullable=False, index=True)
    location = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text)
    salary = db.Column(db.String(100))
    job_type = db.Column(db.String(50), index=True)
    experience_level = db.Column(db.String(50), index=True)
    posted_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    application_url = db.Column(db.String(500))
    scraped = db.Column(db.Boolean, default=False, index=True)

    def to_dict(self):
        """Convert job object to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'description': self.description,
            'salary': self.salary,
            'job_type': self.job_type,
            'experience_level': self.experience_level,
            'posted_date': self.posted_date.isoformat() if self.posted_date else None,
            'application_url': self.application_url,
            'scraped': self.scraped
        }
    
    def __repr__(self):
        """String representation"""
        return f'<Job {self.title} at {self.company}>'