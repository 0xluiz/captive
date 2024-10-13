from app import mail, app, db
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from flask import url_for
from models import UserRequest

def generate_token(user_request):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    token = serializer.dumps({'email': user_request.email, 'request_id': user_request.id}, salt='email-confirm')
    user_request.token = token
    db.session.commit()
    return token

def send_approval_email(user_request):
    token = generate_token(user_request)
    approval_url = url_for('approve', token=token, _external=True)
    denial_url = url_for('deny', token=token, _external=True)

    msg = Message('Guest Access Approval Needed', recipients=[user_request.sponsor_email])
    msg.body = f'''
Hello,

User {user_request.name} ({user_request.email}) is requesting access.

Please approve or deny the request:

Approve: {approval_url}
Deny: {denial_url}

Thank you.
'''
    mail.send(msg)
