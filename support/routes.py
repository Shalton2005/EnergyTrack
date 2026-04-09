"""
Support ticket module for user assistance
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models.database import db, SupportTicket
from datetime import datetime

support_bp = Blueprint('support', __name__, url_prefix='/support')


def send_support_email(ticket, to_admin=False):
    """Send email notification for support ticket"""
    try:
        from flask import current_app
        from flask_mail import Message, Mail
        
        if not current_app.config.get('MAIL_USERNAME'):
            print(f"Support ticket #{ticket.id} created: {ticket.subject}")
            return False
        
        mail = Mail(current_app)
        
        if to_admin:
            # Email to admin
            subject = f"New Support Ticket #{ticket.id}: {ticket.subject}"
            recipient = current_app.config.get('ADMIN_EMAIL', 'admin@energytrack.local')
            body = f"""
            New support ticket received:
            
            From: {ticket.name} ({ticket.email})
            Subject: {ticket.subject}
            Priority: {ticket.priority}
            
            Message:
            {ticket.message}
            
            Please login to admin panel to respond.
            """
        else:
            # Email to user
            subject = f"Support Ticket #{ticket.id} Received - {ticket.subject}"
            recipient = ticket.email
            body = f"""
            Hello {ticket.name},
            
            Thank you for contacting EnergyTrack support!
            
            Your support ticket has been received and our team will respond within 24 hours.
            
            Ticket Details:
            Ticket ID: #{ticket.id}
            Subject: {ticket.subject}
            Priority: {ticket.priority}
            
            We appreciate your patience.
            
            Best regards,
            EnergyTrack Support Team
            """
        
        msg = Message(subject=subject, recipients=[recipient], body=body)
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False


@support_bp.route('/submit', methods=['POST'])
def submit_ticket():
    """Submit a new support ticket"""
    name = request.form.get('name')
    email = request.form.get('email')
    subject = request.form.get('subject')
    message = request.form.get('message')
    
    if not all([name, email, subject, message]):
        flash('All fields are required', 'danger')
        return redirect(url_for('main.index'))
    
    # Create ticket
    ticket = SupportTicket(
        user_id=current_user.id if current_user.is_authenticated else None,
        name=name,
        email=email,
        subject=subject,
        message=message,
        priority='medium'
    )
    
    db.session.add(ticket)
    db.session.commit()
    
    # Send emails
    try:
        send_support_email(ticket, to_admin=True)
        send_support_email(ticket, to_admin=False)
    except:
        pass
    
    flash(f'Support ticket #{ticket.id} submitted successfully! We will respond within 24 hours.', 'success')
    return redirect(url_for('main.index'))


@support_bp.route('/my-tickets')
@login_required
def my_tickets():
    """View user's support tickets"""
    tickets = SupportTicket.query.filter_by(user_id=current_user.id).order_by(SupportTicket.created_at.desc()).all()
    return render_template('support/my_tickets.html', tickets=tickets)


@support_bp.route('/ticket/<int:ticket_id>')
@login_required
def view_ticket(ticket_id):
    """View a specific ticket"""
    ticket = SupportTicket.query.get_or_404(ticket_id)
    
    # Check if user owns this ticket
    if ticket.user_id != current_user.id and not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('support.my_tickets'))
    
    return render_template('support/view_ticket.html', ticket=ticket)

