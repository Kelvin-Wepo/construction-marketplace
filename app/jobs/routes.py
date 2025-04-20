from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Job, Bid, Review, User
from app.jobs.forms import JobForm, BidForm, ReviewForm
from . import jobs

@jobs.route('/jobs')
def index():
    # Get all open jobs
    open_jobs = Job.query.filter_by(status='open').order_by(Job.created_at.desc()).all()
    
    # Filter by service type if provided
    service_type = request.args.get('service_type')
    if service_type:
        open_jobs = [job for job in open_jobs if job.service_type == service_type]
    
    return render_template('jobs/index.html', jobs=open_jobs)

@jobs.route('/jobs/create', methods=['GET', 'POST'])
@login_required
def create():
    if current_user.role != 'client':
        flash('Only clients can post jobs.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    form = JobForm()
    if form.validate_on_submit():
        job = Job(
            title=form.title.data,
            description=form.description.data,
            service_type=form.service_type.data,
            duration_days=form.duration_days.data,
            budget=form.budget.data,
            client_id=current_user.id
        )
        db.session.add(job)
        db.session.commit()
        
        flash('Job posted successfully!', 'success')
        return redirect(url_for('jobs.view', job_id=job.id))
    
    return render_template('jobs/create.html', form=form)

@jobs.route('/jobs/<int:job_id>')
def view(job_id):
    job = Job.query.get_or_404(job_id)
    bids = Bid.query.filter_by(job_id=job_id).all()
    
    # Check if current user has already bid on this job
    user_bid = None
    if current_user.is_authenticated and current_user.role == 'personnel':
        user_bid = Bid.query.filter_by(job_id=job_id, personnel_id=current_user.id).first()
    
    return render_template('jobs/view.html', job=job, bids=bids, user_bid=user_bid)

@jobs.route('/jobs/<int:job_id>/bid', methods=['GET', 'POST'])
@login_required
def bid(job_id):
    if current_user.role != 'personnel':
        flash('Only construction personnel can bid on jobs.', 'danger')
        return redirect(url_for('jobs.view', job_id=job_id))
    
    job = Job.query.get_or_404(job_id)
    
    # Check if job is still open
    if job.status != 'open':
        flash('This job is no longer accepting bids.', 'danger')
        return redirect(url_for('jobs.view', job_id=job_id))
    
    # Check if user has already bid on this job
    existing_bid = Bid.query.filter_by(job_id=job_id, personnel_id=current_user.id).first()
    if existing_bid:
        flash('You have already bid on this job.', 'warning')
        return redirect(url_for('jobs.view', job_id=job_id))
    
    form = BidForm()
    if form.validate_on_submit():
        bid = Bid(
            job_id=job_id,
            personnel_id=current_user.id,
            amount=form.amount.data,
            message=form.message.data,
            estimated_days=form.estimated_days.data
        )
        db.session.add(bid)
        db.session.commit()
        
        flash('Your bid has been submitted!', 'success')
        return redirect(url_for('jobs.view', job_id=job_id))
    
    return render_template('jobs/bid.html', form=form, job=job)

@jobs.route('/jobs/<int:job_id>/accept-bid/<int:bid_id>', methods=['POST'])
@login_required
def accept_bid(job_id, bid_id):
    job = Job.query.get_or_404(job_id)
    bid = Bid.query.get_or_404(bid_id)
    
    # Ensure the current user is the job owner
    if job.client_id != current_user.id:
        flash('You are not authorized to perform this action.', 'danger')
        return redirect(url_for('jobs.view', job_id=job_id))
    
    # Update job status and assign personnel
    job.status = 'in_progress'
    job.personnel_id = bid.personnel_id
    
    # Update bid status
    bid.status = 'accepted'
    
    # Reject all other bids
    other_bids = Bid.query.filter(Bid.job_id == job_id, Bid.id != bid_id).all()
    for other_bid in other_bids:
        other_bid.status = 'rejected'
    
    db.session.commit()
    
    flash('Bid accepted! The job is now in progress.', 'success')
    return redirect(url_for('jobs.view', job_id=job_id))

@jobs.route('/jobs/<int:job_id>/complete', methods=['POST'])
@login_required
def complete_job(job_id):
    job = Job.query.get_or_404(job_id)
    
    # Ensure the current user is the job owner
    if job.client_id != current_user.id:
        flash('You are not authorized to perform this action.', 'danger')
        return redirect(url_for('jobs.view', job_id=job_id))
    
    # Update job status
    job.status = 'completed'
    db.session.commit()
    
    flash('Job marked as completed! Please leave a review.', 'success')
    return redirect(url_for('jobs.review', job_id=job_id))

@jobs.route('/jobs/<int:job_id>/review', methods=['GET', 'POST'])
@login_required
def review(job_id):
    job = Job.query.get_or_404(job_id)
    
    # Ensure the job is completed
    if job.status != 'completed':
        flash('You can only review completed jobs.', 'warning')
        return redirect(url_for('jobs.view', job_id=job_id))
    
    # Determine who is being reviewed
    if current_user.id == job.client_id:
        reviewer_id = job.client_id
        reviewee_id = job.personnel_id
    elif current_user.id == job.personnel_id:
        reviewer_id = job.personnel_id
        reviewee_id = job.client_id
    else:
        flash('You are not authorized to review this job.', 'danger')
        return redirect(url_for('jobs.view', job_id=job_id))
    
    # Check if user has already reviewed this job
    existing_review = Review.query.filter_by(
        job_id=job_id, 
        reviewer_id=reviewer_id, 
        reviewee_id=reviewee_id
    ).first()
    
    if existing_review:
        flash('You have already reviewed this job.', 'warning')
        return redirect(url_for('jobs.view', job_id=job_id))
    
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            job_id=job_id,
            reviewer_id=reviewer_id,
            reviewee_id=reviewee_id,
            rating=form.rating.data,
            comment=form.comment.data
        )
        db.session.add(review)
        db.session.commit()
        
        flash('Your review has been submitted!', 'success')
        return redirect(url_for('jobs.view', job_id=job_id))
    
    return render_template('jobs/review.html', form=form, job=job)
