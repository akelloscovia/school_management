from flask import Blueprint, request, current_app
from app import db
from app.models import Message, Announcement, User, Role
from app.utils.decorators import (
    token_required, validate_request_json,
    get_pagination_params, paginate_query
)
from app.utils.helpers import ResponseFormatter

communication_bp = Blueprint('communication', __name__)


# ============ MESSAGES ============

@communication_bp.route('/messages', methods=['POST'])
@token_required
@validate_request_json('recipient_id', 'body')
def send_message(current_user):
    """Send a message to another user"""
    data = request.get_json()
    
    recipient = User.query.get(data['recipient_id'])
    if not recipient:
        return ResponseFormatter.error('Recipient not found', status_code=404)
    
    try:
        message = Message(
            sender_id=current_user.id,
            recipient_id=data['recipient_id'],
            subject=data.get('subject'),
            body=data['body']
        )
        db.session.add(message)
        db.session.commit()
        
        return ResponseFormatter.success(
            data=message.to_dict(),
            message='Message sent successfully',
            status_code=201
        )
    except Exception as e:
        db.session.rollback()
        return ResponseFormatter.error(f'Error sending message: {str(e)}', status_code=500)


@communication_bp.route('/messages/inbox', methods=['GET'])
@token_required
def get_inbox(current_user):
    """Get messages received by current user"""
    page, per_page = get_pagination_params()
    
    is_read = request.args.get('is_read', type=lambda x: x.lower() == 'true' if x else None)
    
    query = Message.query.filter_by(recipient_id=current_user.id)
    
    if is_read is not None:
        query = query.filter_by(is_read=is_read)
    
    query = query.order_by(Message.created_at.desc())
    result = paginate_query(query, page, per_page)
    
    return ResponseFormatter.success(data=result)


@communication_bp.route('/messages/sent', methods=['GET'])
@token_required
def get_sent_messages(current_user):
    """Get messages sent by current user"""
    page, per_page = get_pagination_params()
    
    query = Message.query.filter_by(sender_id=current_user.id).order_by(Message.created_at.desc())
    result = paginate_query(query, page, per_page)
    
    return ResponseFormatter.success(data=result)


@communication_bp.route('/webhooks/admission-notification', methods=['POST'])
def admission_notification_webhook():
    """Webhook endpoint for creating admission notification messages"""
    data = request.get_json(silent=True) or {}
    secret = request.headers.get('X-WEBHOOK-SECRET') or data.get('webhook_secret')
    expected_secret = current_app.config.get('WEBHOOK_SECRET', '')

    if not expected_secret:
        return ResponseFormatter.error('Webhook is not configured on this server', status_code=500)
    if not secret or secret != expected_secret:
        return ResponseFormatter.error('Invalid webhook secret', status_code=401)

    subject = data.get('subject')
    body = data.get('body')
    if not subject or not body:
        return ResponseFormatter.error('Missing subject or body for admission notification', status_code=400)

    admin_users = User.query.join(Role).filter(Role.name == 'admin', User.is_active == True).all()
    if not admin_users:
        return ResponseFormatter.error('No active admin users found', status_code=404)

    messages = []
    try:
        for admin in admin_users:
            message = Message(
                sender_id=admin.id,
                recipient_id=admin.id,
                subject=subject,
                body=body
            )
            db.session.add(message)
            messages.append(message)
        db.session.commit()

        return ResponseFormatter.success(
            data={'created': len(messages)},
            message='Admission notification created',
            status_code=201
        )
    except Exception as e:
        db.session.rollback()
        return ResponseFormatter.error(f'Unable to create admission notification: {str(e)}', status_code=500)


@communication_bp.route('/webhooks/contact-message', methods=['POST'])
def contact_message_notification_webhook():
    """Webhook endpoint for creating contact message notifications"""
    data = request.get_json(silent=True) or {}
    secret = request.headers.get('X-WEBHOOK-SECRET') or data.get('webhook_secret')
    expected_secret = current_app.config.get('WEBHOOK_SECRET', '')

    if not expected_secret:
        return ResponseFormatter.error('Webhook is not configured on this server', status_code=500)
    if not secret or secret != expected_secret:
        return ResponseFormatter.error('Invalid webhook secret', status_code=401)

    subject = data.get('subject')
    body = data.get('body')
    if not subject or not body:
        return ResponseFormatter.error('Missing subject or body for contact message notification', status_code=400)

    admin_users = User.query.join(Role).filter(Role.name == 'admin', User.is_active == True).all()
    if not admin_users:
        return ResponseFormatter.error('No active admin users found', status_code=404)

    messages = []
    try:
        for admin in admin_users:
            message = Message(
                sender_id=admin.id,
                recipient_id=admin.id,
                subject=subject,
                body=body
            )
            db.session.add(message)
            messages.append(message)
        db.session.commit()

        return ResponseFormatter.success(
            data={'created': len(messages)},
            message='Contact message notification created',
            status_code=201
        )
    except Exception as e:
        db.session.rollback()
        return ResponseFormatter.error(f'Unable to create contact message notification: {str(e)}', status_code=500)


@communication_bp.route('/messages/<int:message_id>', methods=['GET'])
@token_required
def get_message(current_user, message_id):
    """Get a specific message"""
    message = Message.query.get(message_id)
    if not message:
        return ResponseFormatter.error('Message not found', status_code=404)
    
    # Check permissions
    if message.sender_id != current_user.id and message.recipient_id != current_user.id:
        return ResponseFormatter.error('Insufficient permissions', status_code=403)
    
    # Mark as read if recipient is viewing
    if message.recipient_id == current_user.id and not message.is_read:
        message.is_read = True
        db.session.commit()
    
    return ResponseFormatter.success(data=message.to_dict())


@communication_bp.route('/messages/<int:message_id>', methods=['DELETE'])
@token_required
def delete_message(current_user, message_id):
    """Delete a message"""
    message = Message.query.get(message_id)
    if not message:
        return ResponseFormatter.error('Message not found', status_code=404)
    
    # Check permissions
    if message.sender_id != current_user.id and message.recipient_id != current_user.id:
        return ResponseFormatter.error('Insufficient permissions', status_code=403)
    
    try:
        db.session.delete(message)
        db.session.commit()
        
        return ResponseFormatter.success(message='Message deleted successfully')
    except Exception as e:
        db.session.rollback()
        return ResponseFormatter.error(f'Error deleting message: {str(e)}', status_code=500)


@communication_bp.route('/messages/<int:message_id>/mark-read', methods=['POST'])
@token_required
def mark_message_read(current_user, message_id):
    """Mark message as read"""
    message = Message.query.get(message_id)
    if not message:
        return ResponseFormatter.error('Message not found', status_code=404)
    
    if message.recipient_id != current_user.id:
        return ResponseFormatter.error('Insufficient permissions', status_code=403)
    
    try:
        message.is_read = True
        db.session.commit()
        
        return ResponseFormatter.success(data=message.to_dict(), message='Message marked as read')
    except Exception as e:
        db.session.rollback()
        return ResponseFormatter.error(f'Error marking message: {str(e)}', status_code=500)


# ============ ANNOUNCEMENTS ============

@communication_bp.route('/announcements', methods=['POST'])
@token_required
@validate_request_json('title', 'content', 'announcement_type')
def create_announcement(current_user):
    """Create an announcement"""
    data = request.get_json()
    
    try:
        announcement = Announcement(
            title=data['title'],
            content=data['content'],
            created_by_id=current_user.id,
            announcement_type=data['announcement_type'],
            class_id=data.get('class_id'),
            priority=data.get('priority', 'normal'),
            expires_at=data.get('expires_at')
        )
        db.session.add(announcement)
        db.session.commit()
        
        return ResponseFormatter.success(
            data=announcement.to_dict(),
            message='Announcement created successfully',
            status_code=201
        )
    except Exception as e:
        db.session.rollback()
        return ResponseFormatter.error(f'Error creating announcement: {str(e)}', status_code=500)


@communication_bp.route('/announcements', methods=['GET'])
def get_announcements():
    """Get announcements"""
    page, per_page = get_pagination_params()
    
    announcement_type = request.args.get('type')
    priority = request.args.get('priority')
    class_id = request.args.get('class_id', type=int)
    
    query = Announcement.query
    
    if announcement_type:
        query = query.filter_by(announcement_type=announcement_type)
    if priority:
        query = query.filter_by(priority=priority)
    if class_id:
        query = query.filter_by(class_id=class_id)
    
    # Filter out expired announcements
    from datetime import datetime
    query = query.filter(
        db.or_(
            Announcement.expires_at.is_(None),
            Announcement.expires_at >= datetime.utcnow()
        )
    )
    
    query = query.order_by(Announcement.created_at.desc())
    result = paginate_query(query, page, per_page)
    
    return ResponseFormatter.success(data=result)


@communication_bp.route('/announcements/<int:announcement_id>', methods=['GET'])
def get_announcement(announcement_id):
    """Get a specific announcement"""
    announcement = Announcement.query.get(announcement_id)
    if not announcement:
        return ResponseFormatter.error('Announcement not found', status_code=404)
    
    return ResponseFormatter.success(data=announcement.to_dict())


@communication_bp.route('/announcements/<int:announcement_id>', methods=['PUT'])
@token_required
def update_announcement(current_user, announcement_id):
    """Update an announcement"""
    announcement = Announcement.query.get(announcement_id)
    if not announcement:
        return ResponseFormatter.error('Announcement not found', status_code=404)
    
    # Only creator or admin can update
    if announcement.created_by_id != current_user.id and current_user.role.name != 'admin':
        return ResponseFormatter.error('Insufficient permissions', status_code=403)
    
    data = request.get_json()
    
    try:
        announcement.title = data.get('title', announcement.title)
        announcement.content = data.get('content', announcement.content)
        announcement.priority = data.get('priority', announcement.priority)
        announcement.expires_at = data.get('expires_at', announcement.expires_at)
        
        db.session.commit()
        
        return ResponseFormatter.success(
            data=announcement.to_dict(),
            message='Announcement updated successfully'
        )
    except Exception as e:
        db.session.rollback()
        return ResponseFormatter.error(f'Error updating announcement: {str(e)}', status_code=500)


@communication_bp.route('/announcements/<int:announcement_id>', methods=['DELETE'])
@token_required
def delete_announcement(current_user, announcement_id):
    """Delete an announcement"""
    announcement = Announcement.query.get(announcement_id)
    if not announcement:
        return ResponseFormatter.error('Announcement not found', status_code=404)
    
    # Only creator or admin can delete
    if announcement.created_by_id != current_user.id and current_user.role.name != 'admin':
        return ResponseFormatter.error('Insufficient permissions', status_code=403)
    
    try:
        db.session.delete(announcement)
        db.session.commit()
        
        return ResponseFormatter.success(message='Announcement deleted successfully')
    except Exception as e:
        db.session.rollback()
        return ResponseFormatter.error(f'Error deleting announcement: {str(e)}', status_code=500)
