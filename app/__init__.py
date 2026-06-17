from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
import os

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()


def create_app(config_name=None):
    """Application factory"""

    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    from config import config

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # ----------------------------
    # CORS CONFIG
    # ----------------------------
    cors_origins = os.getenv(
        'CORS_ORIGINS',
        'http://localhost:5173,http://localhost:3000,http://localhost:8000,https://school-mgt-frontend-89tm.onrender.com'
    ).split(',')

    CORS(
        app,
        resources={r"/api/*": {
            "origins": cors_origins
        }},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # ----------------------------
    # JWT ERROR HANDLERS
    # ----------------------------
    @jwt.unauthorized_loader
    def unauthorized_response(callback):
        return {'success': False, 'error': callback}, 401

    @jwt.invalid_token_loader
    def invalid_token_response(callback):
        return {'success': False, 'error': callback}, 401

    @jwt.expired_token_loader
    def expired_token_response(jwt_header, jwt_payload):
        return {'success': False, 'error': 'Token has expired'}, 401

    @jwt.revoked_token_loader
    def revoked_token_response(jwt_header, jwt_payload):
        return {'success': False, 'error': 'Token has been revoked'}, 401

    @jwt.needs_fresh_token_loader
    def needs_fresh_token_response(callback):
        return {'success': False, 'error': callback}, 401

    # ----------------------------
    # REGISTER BLUEPRINTS
    # ----------------------------
    from app.routes.auth import auth_bp
    from app.routes.users import users_bp
    from app.routes.students import students_bp
    from app.routes.attendance import attendance_bp
    from app.routes.marks import marks_bp
    from app.routes.reports import reports_bp
    from app.routes.classes import classes_bp
    from app.routes.communication import communication_bp
    from app.routes.admissions import admissions_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(students_bp, url_prefix='/api/students')
    app.register_blueprint(attendance_bp, url_prefix='/api/attendance')
    app.register_blueprint(marks_bp, url_prefix='/api/marks')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')
    app.register_blueprint(classes_bp, url_prefix='/api/classes')
    app.register_blueprint(communication_bp, url_prefix='/api/communication')
    app.register_blueprint(admissions_bp, url_prefix='/api/admissions')

    # ----------------------------
    # ERROR HANDLERS
    # ----------------------------
    @app.errorhandler(400)
    def bad_request(error):
        return {'error': 'Bad request'}, 400

    @app.errorhandler(401)
    def unauthorized(error):
        return {'error': 'Unauthorized'}, 401

    @app.errorhandler(403)
    def forbidden(error):
        return {'error': 'Forbidden'}, 403

    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Internal server error'}, 500

    # Create tables
    with app.app_context():
        db.create_all()

    return app