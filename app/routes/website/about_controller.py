from flask import Blueprint, jsonify, request, current_app
from werkzeug.utils import secure_filename
from app.models.website import TeamMember
import json
import os

website_about_bp = Blueprint('aboutus', __name__)

DEFAULT_ABOUT_CONTENT = {
    'vision': 'To nurture confident, creative, and responsible learners.',
    'mission': 'To provide accessible quality education in a safe, supportive environment.',
    'director': 'Mr. John Doe',
    'head_teacher': 'Mrs. Jane Smith',
    'deputy_head_teacher': 'Mr. Alex Johnson',
    'achievements': 'Award-winning school with excellent exam results.',
    'director_image': '',
    'head_teacher_image': '',
    'deputy_head_teacher_image': ''
}

CONTENT_FILE_NAME = 'about_page.json'


def get_content_file_path():
    instance_path = current_app.instance_path
    os.makedirs(instance_path, exist_ok=True)
    return os.path.join(instance_path, CONTENT_FILE_NAME)


def load_about_content():
    content_file = get_content_file_path()
    if os.path.exists(content_file):
        try:
            with open(content_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_ABOUT_CONTENT.copy()


def save_about_content(content):
    content_file = get_content_file_path()
    # Always save the image fields explicitly to test
    content.setdefault('director_image', '')
    content.setdefault('head_teacher_image', '')
    content.setdefault('deputy_head_teacher_image', '')
    with open(content_file, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=2)


# School overview
@website_about_bp.route('/', methods=['GET'], strict_slashes=False)
def about_school():
    return jsonify(load_about_content()), 200


# Update about page content
@website_about_bp.route('/', methods=['PUT'], strict_slashes=False)
def update_about_school():
    from app.utils.helpers import save_file
    import sys
    
    print(f"DEBUG: request.method = {request.method}", file=sys.stderr)
    print(f"DEBUG: request.content_type = {request.content_type}", file=sys.stderr)
    print(f"DEBUG: request.files keys = {list(request.files.keys())}", file=sys.stderr)
    print(f"DEBUG: request.form keys = {list(request.form.keys())}", file=sys.stderr)
    
    if request.content_type and 'multipart/form-data' in request.content_type:
        data = request.form.to_dict()
        print(f"DEBUG: Parsed multipart data: {data}", file=sys.stderr)
    else:
        data = request.get_json(silent=True) or {}
        print(f"DEBUG: Parsed JSON data: {data}", file=sys.stderr)

    content = load_about_content()
    print(f"DEBUG: Loaded content keys: {list(content.keys())}", file=sys.stderr)
    
    content['vision'] = data.get('vision', content['vision'])
    content['mission'] = data.get('mission', content['mission'])
    content['director'] = data.get('director', content['director'])
    content['head_teacher'] = data.get('head_teacher', content['head_teacher'])
    content['deputy_head_teacher'] = data.get('deputy_head_teacher', content['deputy_head_teacher'])
    content['achievements'] = data.get('achievements', content['achievements'])

    # Handle direct leadership image uploads
    if 'director_image' in request.files:
        print(f"DEBUG: director_image found in request.files", file=sys.stderr)
        uploaded_path = save_file(request.files['director_image'], folder='team')
        print(f"DEBUG: save_file returned: {uploaded_path}", file=sys.stderr)
        if uploaded_path:
            content['director_image'] = uploaded_path

    if 'head_teacher_image' in request.files:
        uploaded_path = save_file(request.files['head_teacher_image'], folder='team')
        if uploaded_path:
            content['head_teacher_image'] = uploaded_path

    if 'deputy_head_teacher_image' in request.files:
        uploaded_path = save_file(request.files['deputy_head_teacher_image'], folder='team')
        if uploaded_path:
            content['deputy_head_teacher_image'] = uploaded_path

    print(f"DEBUG: Final content director_image: {content.get('director_image')}", file=sys.stderr)
    save_about_content(content)
    return jsonify(content), 200


# Optional: List team members (founders, principals, or leadership)
@website_about_bp.route('/team', methods=['GET'], strict_slashes=False)
def team_members():
    members = TeamMember.query.all()
    return jsonify([m.to_dict() for m in members]), 200


# Optional: Get a single team member by ID
@website_about_bp.route('/team/<int:member_id>', methods=['GET'], strict_slashes=False)
def get_team_member(member_id):
    member = TeamMember.query.get_or_404(member_id)
    return jsonify(member.to_dict()), 200
