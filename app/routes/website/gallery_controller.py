from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
import os
from app import db
from app.models.website import Gallery

website_gallery_bp = Blueprint('website_gallery', __name__)


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi', 'mkv'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_upload_folder():
    return current_app.config.get('UPLOAD_FOLDER') or os.path.join(current_app.static_folder, 'uploads', 'gallery')


def get_upload_url(filename):
    return f'/api/v1/gallery/files/{filename}'

# Get all gallery items

@website_gallery_bp.route('/', methods=['GET'], strict_slashes=False)
def get_gallery():
   items = Gallery.query.all()
   return jsonify([item.to_dict() for item in items])

# Upload a new image/video
@website_gallery_bp.route('/', methods=['POST'], strict_slashes=False)
def upload_media():
    files = (
        request.files.getlist('images')
        or request.files.getlist('images[]')
        or request.files.getlist('gallery_images')
        or request.files.getlist('gallery_images[]')
        or request.files.getlist('file')
        or request.files.getlist('files')
        or request.files.getlist('image')
    )
    if not files:
        return jsonify({'error': 'No files provided'}), 400

    upload_folder = get_upload_folder()
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

@website_gallery_bp.route('/files/<path:filename>', methods=['GET'], strict_slashes=False)
def serve_gallery_file(filename):
    upload_folder = get_upload_folder()
    return send_from_directory(upload_folder, filename)


@website_gallery_bp.route('/<int:item_id>', methods=['GET'], strict_slashes=False)
def get_media(item_id):
    item = Gallery.query.get_or_404(item_id)
    upload_folder = get_upload_folder()
    return send_from_directory(upload_folder, item.filename)

# Delete an image/video
@website_gallery_bp.route('/<int:item_id>', methods=['DELETE'])
def delete_media(item_id):
    item = Gallery.query.get_or_404(item_id)
    upload_folder = get_upload_folder()
    
    try:
        os.remove(os.path.join(upload_folder, item.filename))
    except FileNotFoundError:
        pass

    db.session.delete(item)
    db.session.commit()
    
    return jsonify({'message': 'Item deleted'}), 200
