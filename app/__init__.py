from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_migrate import Migrate
import os

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
socketio = SocketIO()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///construction_marketplace.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Security headers
    @app.after_request
    def add_security_headers(response):
        csp = "; ".join([
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data:",
            "font-src 'self'",
            "connect-src 'self' ws: wss:"
        ])
        response.headers['Content-Security-Policy'] = csp
        return response
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    socketio.init_app(app)
    migrate.init_app(app, db)
    
    # Register blueprints
    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix='')
    
    from app.jobs import jobs as jobs_blueprint
    app.register_blueprint(jobs_blueprint)
    
    from app.messaging import messaging as messaging_blueprint
    app.register_blueprint(messaging_blueprint)
    
    from app.admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Register documentation route
        @app.route('/documentation')
        def documentation():
            from flask import render_template
            return render_template('documentation.html')
    
    return app
