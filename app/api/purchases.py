from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import db, Order, Game
from datetime import datetime

purchases_bp = Blueprint('purchases', __name__, url_prefix='/api/purchases')

@purchases_bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    """
    Buy a game
    
    Expected data:
    {
        "game_id": 1
    }
    """
    try:
        data = request.get_json()
        game_id = data.get('game_id')
        
        game = Game.query.get_or_404(game_id)
        
        existing = Order.query.filter_by(
            user_id=current_user.id,
            game_id=game_id,
            status='completed'
        ).first()
        
        if existing:
            return jsonify({'error': 'You already own this game'}), 400
        
        order = Order(
            user_id=current_user.id,
            game_id=game_id,
            amount_paid=game.price,
            status='completed'  
        )
        
        db.session.add(order)
        db.session.commit()
        
        return jsonify({
            'message': 'Game purchased!',
            'order': order.to_dict(),
            'game': game.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@purchases_bp.route('/<int:order_id>', methods=['GET'])
@login_required
def get_order(order_id):
    """Get order details"""
    try:
        order = Order.query.get_or_404(order_id)
        
        if order.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        game = Game.query.get(order.game_id)
        
        result = order.to_dict()
        result['game'] = game.to_dict() if game else None
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 404


@purchases_bp.route('/history', methods=['GET'])
@login_required
def purchase_history():
    """Get all purchases by current user"""
    try:
        orders = Order.query.filter_by(
            user_id=current_user.id,
            status='completed'
        ).all()
        
        result = []
        for order in orders:
            game = Game.query.get(order.game_id)
            order_dict = order.to_dict()
            order_dict['game'] = game.to_dict() if game else None
            result.append(order_dict)
        
        return jsonify({
            'purchases': result,
            'total': len(result)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@purchases_bp.route('/library', methods=['GET'])
@login_required
def get_library():
    """Get all games owned by user"""
    try:
        orders = Order.query.filter_by(
            user_id=current_user.id,
            status='completed'
        ).all()
        
        games = []
        for order in orders:
            game = Game.query.get(order.game_id)
            if game:
                games.append(game.to_dict())
        
        return jsonify({
            'games': games,
            'total': len(games)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500