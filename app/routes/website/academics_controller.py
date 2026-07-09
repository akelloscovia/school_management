# app/controllers/academics_controller.py
from flask import Blueprint, jsonify, request, current_app
import json
import os

# Blueprint without url_prefix
website_academics_bp = Blueprint("academics", __name__)

DEFAULT_ACADEMICS_CONTENT = {
    "title": "Programs and Highlights",
    "subtitle": "Key programs offered at Hilltop Junior School",
    "description": "We provide a balanced curriculum aligned with the Uganda Primary syllabus, focusing on literacy, numeracy, critical thinking and character formation.",
    "excellence": "A strong academic culture built on excellence, discipline, continuous assessment and support for every learner.",
    "approach": "A child-centered approach that blends academic rigor, creativity, values formation and practical life skills.",
    "cards": [
        {
            "title": "Early Childhood & Daycare",
            "content": "Caring early years provision that supports social, emotional and foundational learning for pre-school children. Play-based activities prepare children for formal schooling."
        },
        {
            "title": "Kindergarten/Foundation",
            "content": "Structured kindergarten that introduces literacy, numeracy and basic life skills. Focus on readiness for Primary 1 and building confidence."
        },
        {
            "title": "Primary Curriculum & PLE Preparation",
            "content": "A curriculum aligned with the Uganda Ministry of Education focusing on English, Mathematics, Science, Social Studies and Religious Education. Pupils are prepared for the Primary Leaving Examinations (PLE) through continuous assessment and targeted revision."
        },
        {
            "title": "Co-curricular Activities",
            "content": "Sports (football, netball), music, drama, and school clubs (STEM, reading, environment) that build teamwork, leadership and practical skills."
        },
        {
            "title": "Pastoral Care & Character Formation",
            "content": "A strong pastoral program promoting discipline, good behavior, moral values and child protection. Emphasis on positive habits and community responsibility."
        },
        {
            "title": "ICT & Life Skills",
            "content": "Introduction to basic ICT, practical subjects and vocational-minded activities to equip learners with modern skills and problem-solving ability."
        }
    ],
    "highlights": [
        "Strong PLE preparation with a history of good results and continuous assessment.",
        "Low teacher-to-pupil ratio enabling individual attention and mentoring.",
        "Active sports and arts programs including football, netball, music and drama.",
        "Regular community engagement and parental involvement in school activities.",
        "Emphasis on values: discipline, respect, responsibility and kindness.",
        "Practical ICT exposure and life skills to prepare pupils for modern learning."
    ],
    "additional": {
        "title": "",
        "content": ""
    }
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
    if "cards" in data:
        content["cards"] = data.get("cards")
    if "highlights" in data:
        content["highlights"] = data.get("highlights")
    if "additional" in data:
        content["additional"] = data.get("additional")
    save_academics_content(content)
    return jsonify(content), 200
