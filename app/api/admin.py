from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import User, Game
from datetime import datetime
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

def admin_required(f):
    """Decorator to check if user is admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/users', methods=['GET'])
@login_required
@admin_required
def get_users():
    """Get all users"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        role = request.args.get('role')
        
        query = User.query
        
        if role:
            query = query.filter_by(role=role)
        
        pagination = query.paginate(page=page, per_page=per_page)
        
        return jsonify({
            'users': [u.to_dict() for u in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@login_required
@admin_required
def get_user(user_id):
    """Get user details"""
    try:
        user = User.query.get_or_404(user_id)
        data = user.to_dict()
        data['games_created'] = len(Game.query.filter_by(developer_id=user_id).all()) if user.role == 'developer' else 0
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404


@admin_bp.route('/users/<int:user_id>/role', methods=['PUT'])
@login_required
@admin_required
def update_user_role(user_id):
    """Update user role"""
    try:
        if user_id == current_user.id:
            return jsonify({'error': 'Cannot change your own role'}), 400
        
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        valid_roles = ['player', 'developer', 'admin']
        if data.get('role') not in valid_roles:
            return jsonify({'error': f'Role must be one of: {valid_roles}'}), 400
        
        user.role = data['role']
        db.session.commit()
        
        return jsonify({'message': f'User role changed to {data["role"]}', 'user': user.to_dict()}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/users/<int:user_id>/suspend', methods=['POST'])
@login_required
@admin_required
def suspend_user(user_id):
    """Suspend a user"""
    try:
        if user_id == current_user.id:
            return jsonify({'error': 'Cannot suspend yourself'}), 400
        
        user = User.query.get_or_404(user_id)
        user.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'User suspended'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/users/<int:user_id>/unsuspend', methods=['POST'])
@login_required
@admin_required
def unsuspend_user(user_id):
    """Unsuspend a user"""
    try:
        user = User.query.get_or_404(user_id)
        user.is_active = True
        db.session.commit()
        
        return jsonify({'message': 'User unsuspended'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/games', methods=['GET'])
@login_required
@admin_required
def get_all_games():
    """Get all games for moderation"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        pagination = Game.query.paginate(page=page, per_page=per_page)
        
        return jsonify({
            'games': [g.to_dict() for g in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/games/<int:game_id>/feature', methods=['POST'])
@login_required
@admin_required
def feature_game(game_id):
    """Feature a game on homepage"""
    try:
        game = Game.query.get_or_404(game_id)
        game.is_featured = True
        db.session.commit()
        
        return jsonify({'message': 'Game featured'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/games/<int:game_id>/unfeature', methods=['POST'])
@login_required
@admin_required
def unfeature_game(game_id):
    """Remove game from featured"""
    try:
        game = Game.query.get_or_404(game_id)
        game.is_featured = False
        db.session.commit()
        
        return jsonify({'message': 'Game unfeatured'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/games/<int:game_id>/remove', methods=['DELETE'])
@login_required
@admin_required
def remove_game(game_id):
    """Remove a game from platform"""
    try:
        game = Game.query.get_or_404(game_id)
        db.session.delete(game)
        db.session.commit()
        
        return jsonify({'message': 'Game removed'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/stats', methods=['GET'])
@login_required
@admin_required
def get_stats():
    """Get platform statistics"""
    try:
        total_users = User.query.count()
        total_games = Game.query.count()
        total_players = User.query.filter_by(role='player').count()
        total_developers = User.query.filter_by(role='developer').count()
        
        return jsonify({
            'total_users': total_users,
            'total_games': total_games,
            'total_players': total_players,
            'total_developers': total_developers
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500