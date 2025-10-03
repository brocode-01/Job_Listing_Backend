from flask import Blueprint, request, jsonify
from datetime import datetime
from database import db
from models import Job
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

@api_bp.route('/jobs', methods=['GET'])
def get_jobs():
    """Get jobs with filtering and sorting"""
    try:
        query = Job.query
        
        # Apply filters if provided
        if request.args.get('location'):
            query = query.filter(Job.location.ilike(f"%{request.args.get('location')}%"))
        if request.args.get('company'):
            query = query.filter(Job.company.ilike(f"%{request.args.get('company')}%"))
        if request.args.get('job_type'):
            query = query.filter(Job.job_type.ilike(f"%{request.args.get('job_type')}%"))
        if request.args.get('experience'):
            query = query.filter(Job.experience_level.ilike(f"%{request.args.get('experience')}%"))
        
        # Apply sorting
        sort_by = request.args.get('sort_by', 'posted_date')
        sort_order = request.args.get('sort_order', 'desc')
        
        order_col = getattr(Job, sort_by, Job.posted_date)
        query = query.order_by(order_col.desc() if sort_order == 'desc' else order_col.asc())
        
        jobs = query.all()
        return jsonify([job.to_dict() for job in jobs])
        
    except Exception as e:
        logger.error(f"Error fetching jobs: {e}")
        return jsonify({'error': 'Failed to fetch jobs'}), 500

@api_bp.route('/jobs', methods=['POST'])
def add_job():
    """Add a new job listing"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'company', 'location']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        new_job = Job(
            title=data['title'],
            company=data['company'],
            location=data['location'],
            description=data.get('description', ''),
            salary=data.get('salary', ''),
            job_type=data.get('job_type', 'Full-time'),
            experience_level=data.get('experience_level', 'Not specified'),
            application_url=data.get('application_url', ''),
            scraped=False,
            posted_date=datetime.utcnow()
        )
        
        db.session.add(new_job)
        db.session.commit()
        
        return jsonify({
            'message': 'Job added successfully',
            'job': new_job.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Error adding job: {e}")
        return jsonify({'error': 'Failed to add job'}), 500

@api_bp.route('/jobs/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    """Delete a job listing"""
    try:
        job = Job.query.get_or_404(job_id)
        db.session.delete(job)
        db.session.commit()
        return jsonify({'message': 'Job deleted successfully'}), 200
    except Exception as e:
        logger.error(f"Error deleting job {job_id}: {e}")
        return jsonify({'error': 'Failed to delete job'}), 500

@api_bp.route('/jobs/<int:job_id>', methods=['PUT'])
def update_job(job_id):
    """Update a job listing"""
    try:
        job = Job.query.get_or_404(job_id)
        data = request.get_json()
        
        # Update fields if provided
        for field in ['title', 'company', 'location', 'description', 'salary', 
                     'job_type', 'experience_level', 'application_url']:
            if field in data:
                setattr(job, field, data[field])
        
        db.session.commit()
        return jsonify({
            'message': 'Job updated successfully',
            'job': job.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating job {job_id}: {e}")
        return jsonify({'error': 'Failed to update job'}), 500

@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get job statistics"""
    try:
        total_jobs = Job.query.count()
        scraped_jobs = Job.query.filter_by(scraped=True).count()
        
        # Get top companies and locations efficiently
        top_companies = db.session.query(
            Job.company, 
            db.func.count(Job.id).label('count')
        ).group_by(Job.company).order_by(
            db.func.count(Job.id).desc()
        ).limit(5).all()
        
        top_locations = db.session.query(
            Job.location, 
            db.func.count(Job.id).label('count')
        ).group_by(Job.location).order_by(
            db.func.count(Job.id).desc()
        ).limit(5).all()
        
        return jsonify({
            'total_jobs': total_jobs,
            'scraped_jobs': scraped_jobs,
            'manual_jobs': total_jobs - scraped_jobs,
            'top_companies': [{'name': c[0], 'count': c[1]} for c in top_companies],
            'top_locations': [{'name': l[0], 'count': l[1]} for l in top_locations]
        })
        
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        return jsonify({'error': 'Failed to fetch statistics'}), 500

@api_bp.route('/scrape', methods=['GET', 'POST'])
def trigger_scraping():
    """Trigger LinkedIn job scraping"""
    scraper = None
    try:
        from selenium_scraper import JobScraper
        
        logger.info("Starting job scraping")
        scraper = JobScraper(headless=True)
        scraped_jobs = scraper.scrape_jobs()
        
        added_count = 0
        for job_data in scraped_jobs:
            try:
                # Check for existing job
                if not Job.query.filter(
                    db.and_(
                        Job.title.ilike(job_data['title']),
                        Job.company.ilike(job_data['company'])
                    )
                ).first():
                    new_job = Job(
                        title=job_data['title'],
                        company=job_data['company'],
                        location=job_data.get('location', 'Not specified'),
                        description=job_data.get('description', ''),
                        salary=job_data.get('salary', ''),
                        job_type=job_data.get('job_type', 'Full-time'),
                        experience_level=job_data.get('experience_level', 'Not specified'),
                        application_url=job_data.get('application_url', ''),
                        scraped=True,
                        posted_date=datetime.utcnow()
                    )
                    db.session.add(new_job)
                    added_count += 1
            except Exception as e:
                logger.error(f"Error processing job: {e}")
                continue
        
        db.session.commit()
        
        return jsonify({
            'message': f'Successfully scraped jobs. Added {added_count} new jobs.',
            'total_scraped': len(scraped_jobs),
            'added': added_count,
            'jobs': [job.to_dict() for job in Job.query.filter_by(scraped=True).order_by(Job.posted_date.desc()).limit(5).all()]
        }), 200
        
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if scraper:
            scraper.close()

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })