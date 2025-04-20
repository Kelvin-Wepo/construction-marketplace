from functools import wraps
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import User, Job, Bid, Message, Review, Referral
from app.admin.forms import AdminMessageForm
from app.auth.utils import send_otp
from . import admin

# Admin authentication decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.email != 'admin@example.com':
            flash('You must be an admin to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/')
@login_required
@admin_required
def index():
    # Dashboard statistics
    total_users = User.query.count()
    total_jobs = Job.query.count()
    total_bids = Bid.query.count()
    total_messages = Message.query.count()
    
    # Recent activity
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_jobs = Job.query.order_by(Job.created_at.desc()).limit(5).all()
    
    return render_template('admin/index.html', 
                          total_users=total_users,
                          total_jobs=total_jobs,
                          total_bids=total_bids,
                          total_messages=total_messages,
                          recent_users=recent_users,
                          recent_jobs=recent_jobs)

@admin.route('/users')
@login_required
@admin_required
def users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin.route('/users/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    user = User.query.get_or_404(user_id)
    
    # Get user's jobs, bids, reviews, and referrals
    if user.role == 'client':
        jobs = Job.query.filter_by(client_id=user.id).all()
        bids = []
    else:
        jobs = []
        bids = Bid.query.filter_by(personnel_id=user.id).all()
    
    reviews_given = Review.query.filter_by(reviewer_id=user.id).all()
    reviews_received = Review.query.filter_by(reviewee_id=user.id).all()
    referrals = Referral.query.filter_by(referrer_id=user.id).all()
    
    return render_template('admin/user_detail.html', 
                          user=user,
                          jobs=jobs,
                          bids=bids,
                          reviews_given=reviews_given,
                          reviews_received=reviews_received,
                          referrals=referrals)

@admin.route('/jobs')
@login_required
@admin_required
def jobs():
    jobs = Job.query.all()
    return render_template('admin/jobs.html', jobs=jobs)

@admin.route('/jobs/<int:job_id>')
@login_required
@admin_required
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    bids = Bid.query.filter_by(job_id=job.id).all()
    
    return render_template('admin/job_detail.html', job=job, bids=bids)

@admin.route('/message/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def message_user(user_id):
    user = User.query.get_or_404(user_id)
    form = AdminMessageForm()
    
    if form.validate_on_submit():
        # Send SMS via Africa's Talking
        message = form.message.data
        response = send_sms(user.phone_number, message)
        
        if response:
            flash(f'Message sent to {user.email}!', 'success')
        else:
            flash('Failed to send message. Please try again.', 'danger')
        
        return redirect(url_for('admin.user_detail', user_id=user.id))
    
    return render_template('admin/message_user.html', form=form, user=user)

@admin.route('/revoke-access/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def revoke_access(user_id):
    user = User.query.get_or_404(user_id)
    
    # Instead of deleting, we could set a flag or change status
    user.is_verified = False
    db.session.commit()
    
    # Notify user via SMS
    message = "Your access to Construction Marketplace has been revoked due to policy violations. Please contact support for more information."
    send_sms(user.phone_number, message)
    
    flash(f'Access revoked for {user.email}!', 'success')
    return redirect(url_for('admin.users'))

@admin.route('/referrals')
@login_required
@admin_required
def referrals():
    referrals = Referral.query.all()
    return render_template('admin/referrals.html', referrals=referrals)

def send_sms(phone_number, message):
    """Send SMS via Africa's Talking SMS API"""
    try:
        from africastalking.SMS import SMS
        sms = SMS()
        response = sms.send(message, [phone_number])
        return response
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return None
