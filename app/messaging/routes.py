from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db, socketio
from app.models import Message, User, Job
from app.messaging.forms import MessageForm
from . import messaging
from flask_socketio import emit, join_room
import os
from werkzeug.utils import secure_filename

@messaging.route('/messages')
@login_required
def index():
    # Get all conversations for the current user
    sent_messages = Message.query.filter_by(sender_id=current_user.id).all()
    received_messages = Message.query.filter_by(receiver_id=current_user.id).all()
    
    # Combine and get unique conversation partners
    conversation_partners = set()
    for msg in sent_messages:
        conversation_partners.add(msg.receiver_id)
    for msg in received_messages:
        conversation_partners.add(msg.sender_id)
    
    # Get user objects for conversation partners
    conversations = []
    for partner_id in conversation_partners:
        partner = User.query.get(partner_id)
        if partner:
            # Get the latest message
            latest_message = Message.query.filter(
                ((Message.sender_id == current_user.id) & (Message.receiver_id == partner_id)) |
                ((Message.sender_id == partner_id) & (Message.receiver_id == current_user.id))
            ).order_by(Message.created_at.desc()).first()
            
            conversations.append({
                'partner': partner,
                'latest_message': latest_message
            })
    
    # Sort conversations by latest message time
    conversations.sort(key=lambda x: x['latest_message'].created_at if x['latest_message'] else None, reverse=True)
    
    return render_template('messaging/index.html', conversations=conversations)

@messaging.route('/messages/<int:user_id>', methods=['GET', 'POST'])
@login_required
def conversation(user_id):
    partner = User.query.get_or_404(user_id)
    
    # Get all messages between current user and partner
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.created_at).all()
    
    # Mark all received messages as read
    for message in messages:
        if message.receiver_id == current_user.id and not message.is_read:
            message.is_read = True
    
    db.session.commit()
    
    # Get jobs that might be relevant to this conversation
    if current_user.role == 'client':
        jobs = Job.query.filter_by(client_id=current_user.id).all()
    else:
        jobs = Job.query.filter_by(personnel_id=current_user.id).all()
    
    form = MessageForm()
    form.job_id.choices = [(0, 'No Job Selected')] + [(job.id, job.title) for job in jobs]
    
    if form.validate_on_submit():
        attachment_url = None
        
        # Handle file upload if provided
        if form.attachment.data:
            filename = secure_filename(form.attachment.data.filename)
            upload_folder = os.path.join(current_app.root_path, 'static/uploads')
            os.makedirs(upload_folder, exist_ok=True)
            
            file_path = os.path.join(upload_folder, filename)
            form.attachment.data.save(file_path)
            
            # Store relative URL for database
            attachment_url = f'/static/uploads/{filename}'
        
        # Create new message
        message = Message(
            sender_id=current_user.id,
            receiver_id=user_id,
            content=form.content.data,
            attachment_url=attachment_url
        )
        
        # Associate with job if selected
        if form.job_id.data != 0:
            message.job_id = form.job_id.data
        
        db.session.add(message)
        db.session.commit()
        
        # Emit socket event for real-time update
        socketio.emit('new_message', {
            'sender_id': current_user.id,
            'receiver_id': user_id,
            'content': form.content.data,
            'attachment_url': attachment_url,
            'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }, room=f'user_{user_id}')
        
        # Clear form
        form.content.data = ''
        form.attachment.data = None
        
        return redirect(url_for('messaging.conversation', user_id=user_id))
    
    return render_template('messaging/conversation.html', partner=partner, messages=messages, form=form)

@socketio.on('connect')
def handle_connect():
    if current_user.is_authenticated:
        join_room(f'user_{current_user.id}')

@socketio.on('join')
def handle_join(data):
    room = data['room']
    join_room(room)

@messaging.route('/messages/job/<int:job_id>/<int:user_id>')
@login_required
def job_conversation(job_id, user_id):
    job = Job.query.get_or_404(job_id)
    
    # Ensure the current user is either the client or the personnel for this job
    if current_user.id != job.client_id and current_user.id != job.personnel_id:
        flash('You are not authorized to access this conversation.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Redirect to the regular conversation view with the job context
    return redirect(url_for('messaging.conversation', user_id=user_id, job_id=job_id))
