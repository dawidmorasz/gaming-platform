import os
from flask import Flask, jsonify, render_template
from flask_login import LoginManager
from dotenv import load_dotenv
from app.db_mongo import get_mongo_db
from app.models_mongo import GameMetadata, GameAnalytics

load_dotenv()

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'app', 'templates'))

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gaming.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from app import db
db.init_app(app)

from app.models import User, Game, Order, Review

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()
    print("Database created!")

from app.auth.routes import auth_bp
from app.api.games import games_bp
from app.api.reviews import reviews_bp
from app.api.admin import admin_bp

app.register_blueprint(auth_bp)
app.register_blueprint(games_bp)
app.register_blueprint(reviews_bp)
app.register_blueprint(admin_bp)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/games')
def games():
    return render_template('games.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok'})

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Server error'}), 500

if __name__ == '__main__':
    print(f"Template folder: {app.template_folder}")
    print(f"Template folder exists: {os.path.exists(app.template_folder)}")
    if os.path.exists(app.template_folder):
        print(f"Files in template folder: {os.listdir(app.template_folder)}")
    app.run(debug=True, port=5000)