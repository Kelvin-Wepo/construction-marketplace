from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from app.auth.forms import LoginForm, RegistrationForm, OTPVerificationForm
from app.auth.utils import send_otp, verify_otp
from . import auth
import random

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            if not user.is_verified:
                flash('Please verify your account first.', 'warning')
                return redirect(url_for('auth.verify_otp', user_id=user.id))
            
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if user with this email already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.login'))
        
        # Create new user
        user = User(
            email=form.email.data,
            phone_number=form.phone_number.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        
        # Check for referral code
        if form.referral_code.data:
            referrer = User.query.filter_by(referral_code=form.referral_code.data).first()
            if referrer:
                user.referred_by = referrer.id
        
        db.session.add(user)
        db.session.commit()
        
        # Generate and send OTP
        otp = random.randint(100000, 999999)
        session['otp'] = otp
        session['user_id'] = user.id
        
        # Send OTP via Africa's Talking SMS API
        send_otp(user.phone_number, otp)
        
        flash('Registration successful! Please verify your phone number.', 'success')
        return redirect(url_for('auth.verify_otp', user_id=user.id))
    
    return render_template('auth/register.html', form=form)

@auth.route('/verify-otp/<int:user_id>', methods=['GET', 'POST'])
def verify_otp(user_id):
    form = OTPVerificationForm()
    
    if form.validate_on_submit():
        user = User.query.get_or_404(user_id)
        stored_otp = session.get('otp')
        
        if stored_otp and int(form.otp.data) == stored_otp:
            user.is_verified = True
            db.session.commit()
            
            # Clear session data
            session.pop('otp', None)
            session.pop('user_id', None)
            
            flash('Phone number verified successfully! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Invalid OTP. Please try again.', 'danger')
    
    return render_template('auth/verify_otp.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
