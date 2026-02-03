from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        email = data.get('email', '').strip().lower()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not email or not username or not password:
            return jsonify({'error': 'All fields required'}), 400
        
        if len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already taken'}), 400
        
        user = User(
            email=email,
            username=username,
            display_name=username
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'Registration successful',
            'user': user.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login a user"""
    try:
        data = request.get_json()
        
        email_or_username = data.get('email_or_username', '').strip()
        password = data.get('password', '')
        
        if not email_or_username or not password:
            return jsonify({'error': 'Email/username and password required'}), 400
        
        user = User.query.filter(
            (User.email == email_or_username.lower()) | 
            (User.username == email_or_username)
        ).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 401
        
        if not user.check_password(password):
            return jsonify({'error': 'Wrong password'}), 401
        
        login_user(user)
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Logout the current user"""
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200


@auth_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """Get current user's profile"""
    return jsonify(current_user.to_dict()), 200