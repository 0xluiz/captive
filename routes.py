from flask import render_template, request, session, redirect, jsonify, url_for, flash
from app import app, db
from models import UserRequest
from utils import send_approval_email, generate_random_password
from radius_db import add_user_to_radius
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
import re

@app.route('/', methods=['GET'])
def landing_page():
    # Capture query parameters from FortiGate
    session['magic'] = request.args.get('magic')
    session['post_url'] = request.args.get('post')
    session['userip'] = request.args.get('userip')
    session['user_mac'] = request.args.get('usermac')

    allowed_domains = app.config['ALLOWED_SPONSOR_DOMAINS']

    # Render the login page, passing allowed_domains to the template
    return render_template('login.html', allowed_domains=allowed_domains)

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name'].strip()
    email = request.form['email'].strip()
    sponsor_email = request.form['sponsor_email'].strip()

    # Input Validation
    if not name or not email or not sponsor_email:
        flash('All fields are required.')
        return redirect(url_for('landing_page'))

    # Validate Email Formats
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(email_regex, email):
        flash('Invalid guest email address.')
        return redirect(url_for('landing_page'))
    if not re.match(email_regex, sponsor_email):
        flash('Invalid sponsor email address.')
        return redirect(url_for('landing_page'))

    # Validate Sponsor Email Domain
    allowed_domains = app.config['ALLOWED_SPONSOR_DOMAINS']
    sponsor_domain = sponsor_email.split('@')[-1]
    if sponsor_domain.lower() not in [domain.lower() for domain in allowed_domains]:
        message = f"Sponsor email must be from the following domain(s): {', '.join(allowed_domains)}"
        flash(message)
        return redirect(url_for('landing_page'))

    # Create a new UserRequest object
    user_request = UserRequest(
        name=name,
        email=email,
        sponsor_email=sponsor_email,
        magic=session.get('magic'),
        post_url=session.get('post_url'),
        user_ip=session.get('userip'),
        user_mac=session.get('user_mac')
    )

    # Save the user request to the database
    db.session.add(user_request)
    db.session.commit()

    # Send approval email to sponsor
    send_approval_email(user_request)

    # Pass request_id to the template
    return render_template('standby.html', request_id=user_request.id)

@app.route('/check_status', methods=['POST'])
def check_status():
    data = request.get_json()
    request_id = data.get('request_id')
    user_request = UserRequest.query.filter_by(id=request_id).first()

    if user_request and user_request.approved:
        return jsonify({'approved': True})
    else:
        return jsonify({'approved': False})

@app.route('/authenticate', methods=['GET'])
def authenticate():
    request_id = request.args.get('request_id')
    user_request = UserRequest.query.filter_by(id=request_id).first()

    if user_request and user_request.approved:
        return authenticate_with_fortigate(user_request)
    else:
        message = "Your request is still pending approval or has been denied."
        return render_template('error.html', message=message)

@app.route('/approve', methods=['GET'])
def approve():
    token = request.args.get('token')
    user_request = validate_token(token)
    if user_request:
        user_request.approved = True
        db.session.commit()
        message = "You have approved the access request."
        return render_template('sponsor_confirmation.html', message=message)
    else:
        message = "Invalid or expired token."
        return render_template('error.html', message=message)

@app.route('/deny', methods=['GET'])
def deny():
    token = request.args.get('token')
    user_request = validate_token(token)
    if user_request:
        user_request.approved = False
        db.session.commit()
        message = "You have denied the access request."
        return render_template('sponsor_confirmation.html', message=message)
    else:
        message = "Invalid or expired token."
        return render_template('error.html', message=message)

def validate_token(token):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        data = serializer.loads(token, salt='email-confirm', max_age=3600)
        request_id = data.get('request_id')
        user_request = UserRequest.query.filter_by(id=request_id, token=token).first()
        return user_request
    except (SignatureExpired, BadSignature):
        return None

def authenticate_with_fortigate(user_request):
    # Generate a unique password for the guest
    password = generate_random_password()
    username = user_request.email

    # Add user to FreeRADIUS database
    add_user_to_radius(username, password)

    # Return the rendered template
    return render_template('auth_redirect.html',
                           post_url=user_request.post_url,
                           magic=user_request.magic,
                           username=username,
                           password=password)
