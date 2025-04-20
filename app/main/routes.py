from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import Job, User, Review, Referral, Bid
from app import db
from . import main

@main.route('/', methods=['GET'])
def index():
    print("Accessing index route")  # Debug print
    # Get recent jobs for the homepage
    recent_jobs = Job.query.filter_by(status='open').order_by(Job.created_at.desc()).limit(5).all()
    print(f"Found {len(recent_jobs)} recent jobs")  # Debug print
    
    # Get top-rated construction personnel
    top_personnel = User.query.filter_by(role='personnel').join(
        Review, User.id == Review.reviewee_id
    ).group_by(User.id).order_by(db.func.avg(Review.rating).desc()).limit(5).all()
    print(f"Found {len(top_personnel)} top personnel")  # Debug print
    
    return render_template('main/index.html', recent_jobs=recent_jobs, top_personnel=top_personnel)

@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'client':
        # Get client's posted jobs
        jobs = Job.query.filter_by(client_id=current_user.id).order_by(Job.created_at.desc()).all()
        return render_template('main/client_dashboard.html', jobs=jobs)
    else:
        # Get jobs that the personnel has bid on
        bids = Bid.query.filter_by(personnel_id=current_user.id).all()
        bid_job_ids = [bid.job_id for bid in bids]
        
        # Get jobs that match the personnel's skills
        available_jobs = Job.query.filter_by(status='open').all()
        
        return render_template('main/personnel_dashboard.html', bids=bids, available_jobs=available_jobs)

@main.route('/profile')
@login_required
def profile():
    # Get user's reviews
    reviews_received = Review.query.filter_by(reviewee_id=current_user.id).all()
    
    # Calculate average rating
    avg_rating = 0
    if reviews_received:
        total = sum(review.rating for review in reviews_received)
        avg_rating = total / len(reviews_received)
    
    # Get referral information
    referrals = Referral.query.filter_by(referrer_id=current_user.id).all()
    
    return render_template('main/profile.html', 
                          user=current_user, 
                          reviews=reviews_received, 
                          avg_rating=avg_rating,
                          referrals=referrals)
