# app/controllers/academics_controller.py
from flask import Blueprint, jsonify, request, current_app
import json
import os

# Blueprint without url_prefix
website_academics_bp = Blueprint("academics", __name__, 
url_prefix="/api/v1/academics"
)

DEFAULT_ACADEMICS_CONTENT = {
    "title": "Academic Excellence",
    "subtitle": "Nurturing Bright Minds",
    "description": "Our curriculum is designed to challenge and inspire students.",
    "excellence": "100% pass rate in national exams.",
    "approach": "Holistic education with focus on STEM and arts."
}

CONTENT_FILE_NAME = 'academics_page.json'


def get_content_file_path():
    instance_path = current_app.instance_path
    os.makedirs(instance_path, exist_ok=True)
    return os.path.join(instance_path, CONTENT_FILE_NAME)


def load_academics_content():
    content_file = get_content_file_path()
    if os.path.exists(content_file):
        try:
            with open(content_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_ACADEMICS_CONTENT.copy()


def save_academics_content(content):
    content_file = get_content_file_path()
    with open(content_file, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=2)


# GET /api/v1/academics/
@website_academics_bp.route("/", methods=["GET"], strict_slashes=False)
def get_academics():
    return jsonify(load_academics_content()), 200


# UPDATE /api/v1/academics/
@website_academics_bp.route("/", methods=["PUT"], strict_slashes=False)
def update_academics():
    data = request.get_json(silent=True) or {}
    content = load_academics_content()
    content["title"] = data.get("title", content["title"])
    content["subtitle"] = data.get("subtitle", content["subtitle"])
    content["description"] = data.get("description", content["description"])
    content["excellence"] = data.get("excellence", content["excellence"])
    content["approach"] = data.get("approach", content["approach"])
    save_academics_content(content)
    return jsonify(content), 200
