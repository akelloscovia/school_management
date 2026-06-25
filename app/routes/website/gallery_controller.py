from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
import os
from app import db
from app.models.website import Gallery

website_gallery_bp = Blueprint('website_gallery', __name__)


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi', 'mkv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Get all gallery items

@website_gallery_bp.route('/', methods=['GET'], strict_slashes=False)
def get_gallery():
   items = Gallery.query.all()
   return jsonify([item.to_dict() for item in items])

# Upload a new image/video
@website_gallery_bp.route('/', methods=['POST'], strict_slashes=False)
def upload_media():
    files = request.files.getlist('images') or request.files.getlist('file')
    if not files:
        return jsonify({'error': 'No files provided'}), 400

    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    created_items = []

    for file in files:
        if file.filename == '':
            continue
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)

            media_type = 'video' if filename.rsplit('.', 1)[1].lower() in {'mp4', 'mov', 'avi', 'mkv'} else 'image'
            new_item = Gallery(filename=filename, media_type=media_type)
            db.session.add(new_item)
            db.session.commit()
            created_items.append(new_item.to_dict())

    if not created_items:
        return jsonify({'error': 'No valid files uploaded'}), 400

    return jsonify(created_items), 201

# Get a single image/video by id

@website_gallery_bp.route('/<int:item_id>', methods=['GET'], strict_slashes=False)
def get_media(item_id):
    item = Gallery.query.get_or_404(item_id)
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    return send_from_directory(upload_folder, item.filename)

# Delete an image/video
@website_gallery_bp.route('/<int:item_id>', methods=['DELETE'])
def delete_media(item_id):
    item = Gallery.query.get_or_404(item_id)
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    
    try:
        os.remove(os.path.join(upload_folder, item.filename))
    except FileNotFoundError:
        pass

    db.session.delete(item)
    db.session.commit()
    
    return jsonify({'message': 'Item deleted'}), 200
