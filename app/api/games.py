from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import User, Game, Order
from app.models_mongo import GameMetadata, GameAnalytics
from datetime import datetime

games_bp = Blueprint('games', __name__, url_prefix='/api/games')

game_metadata = GameMetadata()
game_analytics = GameAnalytics()

# EXISTING GAME ROUTES (SQL)

@games_bp.route('', methods=['GET'])
def get_games():
    """Get all games with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        genre = request.args.get('genre')
        
        query = Game.query
        
        if genre:
            query = query.filter_by(genre=genre)
        
        pagination = query.paginate(page=page, per_page=per_page)
        
        return jsonify({
            'games': [g.to_dict() for g in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@games_bp.route('/<int:game_id>', methods=['GET'])
def get_game(game_id):
    """Get single game"""
    try:
        game = Game.query.get_or_404(game_id)
        return jsonify(game.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404


@games_bp.route('', methods=['POST'])
@login_required
def create_game():
    """Create new game (developer only)"""
    try:
        if current_user.role != 'developer':
            return jsonify({'error': 'Only developers can create games'}), 403
        
        data = request.get_json()
        
        if not data.get('title'):
            return jsonify({'error': 'Title is required'}), 400
        
        game = Game(
            title=data.get('title'),
            description=data.get('description'),
            genre=data.get('genre'),
            price=data.get('price', 0),
            developer_id=current_user.id
        )
        
        db.session.add(game)
        db.session.commit()
        
        return jsonify(game.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@games_bp.route('/<int:game_id>', methods=['PUT'])
@login_required
def update_game(game_id):
    """Update game (developer only)"""
    try:
        game = Game.query.get_or_404(game_id)
        
        if game.developer_id != current_user.id:
            return jsonify({'error': 'You can only edit your own games'}), 403
        
        data = request.get_json()
        
        if 'title' in data:
            game.title = data['title']
        if 'description' in data:
            game.description = data['description']
        if 'genre' in data:
            game.genre = data['genre']
        if 'price' in data:
            game.price = data['price']
        
        db.session.commit()
        
        return jsonify(game.to_dict()), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@games_bp.route('/<int:game_id>', methods=['DELETE'])
@login_required
def delete_game(game_id):
    """Delete game (developer only)"""
    try:
        game = Game.query.get_or_404(game_id)
        
        if game.developer_id != current_user.id:
            return jsonify({'error': 'You can only delete your own games'}), 403
        
        db.session.delete(game)
        db.session.commit()
        
        return jsonify({'message': 'Game deleted'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# NEW MONGODB ROUTES (NoSQL)

@games_bp.route('/<int:game_id>/metadata', methods=['POST'])
@login_required
def add_game_metadata(game_id):
    """Add metadata to game (NoSQL - MongoDB)"""
    try:
        game = Game.query.get_or_404(game_id)
        
        if game.developer_id != current_user.id:
            return jsonify({'error': 'You can only edit metadata for your own games'}), 403
        
        data = request.get_json()
        
        result = game_metadata.save_metadata(game_id, {
            'tags': data.get('tags', []),
            'screenshots': data.get('screenshots', []),
            'videos': data.get('videos', []),
            'system_requirements': data.get('system_requirements', {}),
            'developer_notes': data.get('developer_notes', '')
        })
        
        return jsonify({
            'message': 'Metadata saved to MongoDB',
            'result': str(result)
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@games_bp.route('/<int:game_id>/metadata', methods=['GET'])
def get_game_metadata(game_id):
    """Get game metadata from MongoDB"""
    try:
        metadata = game_metadata.get_metadata(game_id)
        
        if metadata:
            metadata.pop('_id', None)  # Remove MongoDB ID
            return jsonify(metadata), 200
        else:
            return jsonify({'message': 'No metadata found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@games_bp.route('/<int:game_id>/analytics', methods=['GET'])
def get_game_analytics(game_id):
    """Get game analytics from MongoDB"""
    try:
        stats = game_analytics.get_stats(game_id)
        
        if stats:
            stats.pop('_id', None)
            return jsonify(stats), 200
        else:
            return jsonify({'views': 0, 'downloads': 0}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@games_bp.route('/<int:game_id>/view', methods=['POST'])
def record_game_view(game_id):
    """Record a game view (analytics)"""
    try:
        game_analytics.record_view(game_id)
        return jsonify({'message': 'View recorded'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@games_bp.route('/<int:game_id>/download', methods=['POST'])
def record_game_download(game_id):
    """Record a game download (analytics)"""
    try:
        game_analytics.record_download(game_id)
        return jsonify({'message': 'Download recorded'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500