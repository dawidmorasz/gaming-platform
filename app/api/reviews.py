from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import User, Game, Order, Review
from datetime import datetime

reviews_bp = Blueprint('reviews', __name__, url_prefix='/api/reviews')

@reviews_bp.route('/game/<int:game_id>', methods=['GET'])
def get_game_reviews(game_id):
    """Get all reviews for a game"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        sort = request.args.get('sort', 'recent')
        
        query = Review.query.filter_by(game_id=game_id)
        
        if sort == 'helpful':
            query = query.order_by(Review.helpful_count.desc())
        elif sort == 'rating':
            query = query.order_by(Review.rating.desc())
        else:
            query = query.order_by(Review.created_at.desc())
        
        pagination = query.paginate(page=page, per_page=per_page)
        
        all_reviews = Review.query.filter_by(game_id=game_id).all()
        avg_rating = sum(r.rating for r in all_reviews) / len(all_reviews) if all_reviews else 0
        
        return jsonify({
            'reviews': [r.to_dict() for r in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'average_rating': round(avg_rating, 1)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@reviews_bp.route('/<int:game_id>', methods=['POST'])
@login_required
def create_review(game_id):
    """Create a review for a game"""
    try:
        order = Order.query.filter_by(user_id=current_user.id, game_id=game_id, status='completed').first()
        if not order:
            return jsonify({'error': 'You must own this game to review it'}), 403
        
        existing = Review.query.filter_by(game_id=game_id, user_id=current_user.id).first()
        if existing:
            return jsonify({'error': 'You already reviewed this game'}), 400
        
        data = request.get_json()
        
        if not data.get('rating'):
            return jsonify({'error': 'Rating required'}), 400
        
        rating = int(data.get('rating'))
        if rating < 1 or rating > 5:
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        
        review = Review(
            game_id=game_id,
            user_id=current_user.id,
            rating=rating,
            title=data.get('title'),
            content=data.get('content')
        )
        
        db.session.add(review)
        db.session.commit()
        
        return jsonify(review.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@reviews_bp.route('/<int:review_id>', methods=['PUT'])
@login_required
def update_review(review_id):
    """Update a review"""
    try:
        review = Review.query.get_or_404(review_id)
        
        if review.user_id != current_user.id:
            return jsonify({'error': 'You can only edit your own reviews'}), 403
        
        data = request.get_json()
        
        if 'rating' in data:
            rating = int(data['rating'])
            if rating < 1 or rating > 5:
                return jsonify({'error': 'Rating must be between 1 and 5'}), 400
            review.rating = rating
        
        if 'title' in data:
            review.title = data['title']
        
        if 'content' in data:
            review.content = data['content']
        
        review.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(review.to_dict()), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@reviews_bp.route('/<int:review_id>', methods=['DELETE'])
@login_required
def delete_review(review_id):
    """Delete a review"""
    try:
        review = Review.query.get_or_404(review_id)
        
        if review.user_id != current_user.id:
            return jsonify({'error': 'You can only delete your own reviews'}), 403
        
        db.session.delete(review)
        db.session.commit()
        
        return jsonify({'message': 'Review deleted'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@reviews_bp.route('/<int:review_id>/helpful', methods=['POST'])
@login_required
def mark_helpful(review_id):
    """Mark review as helpful"""
    try:
        review = Review.query.get_or_404(review_id)
        review.helpful_count += 1
        db.session.commit()
        
        return jsonify({'helpful_count': review.helpful_count}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500