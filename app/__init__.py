from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
import os

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()


def ensure_default_roles_and_admin():
    from app.models import Role, User

    default_roles = [
        'admin',
        'teacher',
        'student',
        'parent',
        'accountant'
    ]

    for role_name in default_roles:
        if not Role.query.filter_by(name=role_name).first():
            db.session.add(Role(name=role_name, description=role_name.capitalize()))

    db.session.commit()

    admin_email = os.getenv('ADMIN_EMAIL', 'admin@hilltop.com').strip().lower()
    admin_password = os.getenv('ADMIN_PASSWORD') or 'ilovehilltop'

    if not User.query.filter(db.func.lower(User.email) == admin_email).first():
        admin_role = Role.query.filter_by(name='admin').first()
        admin = User(
            first_name='Admin',
            last_name='User',
            email=admin_email,
            phone=os.getenv('ADMIN_PHONE', '1234567890'),
            role_id=admin_role.id
        )
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()
        print(f'Created default admin user: {admin_email}')
        print(f'Admin password: {admin_password}')


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
        'http://localhost:5173,http://localhost:5174,http://localhost:3000,http://localhost:8000,https://school-mgt-frontend-89tm.onrender.com'
    ).split(',')

    # In development allow all origins to avoid CORS issues from different dev ports
    if config_name == 'development':
        CORS(
            app,
            resources={r"/api/*": {"origins": "*"}},
            supports_credentials=True,
            allow_headers=["Content-Type", "Authorization"],
            methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        )
        @app.after_request
        def add_dev_cors_headers(response):
            origin = request.headers.get('Origin') or '*'
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
            response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
            return response
    else:
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
    from app.routes.contact import contact_bp
    from app.routes.admissions import admissions_bp
    from app.routes.finance import finance_bp
    from app.routes.library import library_bp
    from app.routes.transport import transport_bp
    
    # Website CMS Blueprints
    from app.routes.website.home_controller import website_home_bp
    from app.routes.website.about_controller import website_about_bp
    from app.routes.website.academics_controller import website_academics_bp
    from app.routes.website.admissions_controller import website_admissions_bp
    from app.routes.website.contact_info_controller import website_contact_info_bp
    from app.routes.website.contact_message_controller import website_contact_message_bp
    from app.routes.website.footer_controller import website_footer_bp
    from app.routes.website.gallery_controller import website_gallery_bp

    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(users_bp, url_prefix='/api/v1/users')
    app.register_blueprint(students_bp, url_prefix='/api/v1/students')
    app.register_blueprint(attendance_bp, url_prefix='/api/v1/attendance')
    app.register_blueprint(marks_bp, url_prefix='/api/v1/marks')
    app.register_blueprint(reports_bp, url_prefix='/api/v1/reports')
    app.register_blueprint(classes_bp, url_prefix='/api/v1/classes')
    app.register_blueprint(communication_bp, url_prefix='/api/v1/communication')
    app.register_blueprint(contact_bp, url_prefix='/api/v1')
    app.register_blueprint(admissions_bp, url_prefix='/api/v1/admissions')
    app.register_blueprint(finance_bp, url_prefix='/api/v1/finance')
    app.register_blueprint(library_bp, url_prefix='/api/v1/library')
    app.register_blueprint(transport_bp, url_prefix='/api/v1/transport')
    
    app.register_blueprint(website_home_bp)
    app.register_blueprint(website_about_bp)
    app.register_blueprint(website_academics_bp)
    app.register_blueprint(website_admissions_bp)
    app.register_blueprint(website_contact_info_bp)
    app.register_blueprint(website_contact_message_bp)
    app.register_blueprint(website_footer_bp)
    app.register_blueprint(website_gallery_bp)

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

    # Create tables and ensure default admin user exists
    with app.app_context():
        db.create_all()
        ensure_default_roles_and_admin()

    return app