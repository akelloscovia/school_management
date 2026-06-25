from flask import Blueprint, jsonify, request
from app import db
from app.models.website import HomePage, WebsiteAnnouncement as Announcement
from app.models.website import AboutPage
from app.models.website import WebsiteContactInfo as Contact_Info

website_home_bp = Blueprint('website_home', __name__, url_prefix='/home')

# Home page route
@website_home_bp.route('/', methods=['GET'], strict_slashes=False)
def home():
    home_page = HomePage.query.first()

    if not home_page:
        return jsonify({'message': 'Home page not set up'}), 404

    return jsonify(home_page.to_dict()), 200

# About page route
@website_home_bp.route('/about', methods=['GET'], strict_slashes=False)
def about():
    return jsonify({
        'school_name': 'Hilltop Junior School Kasangati',
        'established': 2010,
        'motto': 'Knowledge, Discipline, Excellence',
        'location': 'Kasangati, Wakiso, Uganda'
    }), 200

# Announcements route
@website_home_bp.route('/announcements', methods=['GET'], strict_slashes=False)
def announcements():
    all_announcements = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return jsonify([a.to_dict() for a in all_announcements]), 200

# Contact route
@website_home_bp.route('/contact', methods=['GET']
)
def contact():
    contact_info = Contact_Info.query.first()
    if contact_info:
        return jsonify(contact_info.to_dict()), 200
    else:
        return jsonify({'message': 'Contact info not set'}), 404

# Update home page content (admin)
@website_home_bp.route('/', methods=['PUT'], strict_slashes=False)
def update_home():
    import json
    data = request.get_json() or {}
    home_page = HomePage.query.first()
    if not home_page:
        home_page = HomePage()
        db.session.add(home_page)

    if 'hero_title' in data:
        home_page.hero_title = data.get('hero_title')
    if 'hero_subtitle' in data:
        home_page.hero_subtitle = data.get('hero_subtitle')
    if 'hero_image' in data:
        home_page.hero_image = data.get('hero_image')
    if 'about_title' in data:
        home_page.about_title = data.get('about_title')
    if 'about_text' in data:
        home_page.about_text = data.get('about_text')
    if 'about_link' in data:
        home_page.about_link = data.get('about_link')
    if 'core_values' in data:
        # Store core_values as JSON string
        home_page.core_values = json.dumps(data.get('core_values', []))

    db.session.commit()
    return jsonify(home_page.to_dict()), 200
