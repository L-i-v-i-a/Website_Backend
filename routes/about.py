from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
import os
from werkzeug.utils import secure_filename

about_bp = Blueprint('about', __name__)

# MongoDB connection
client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/'))
db = client['Cluster0']
about_collection = db['about']
gallery_collection = db['about_gallery']

UPLOAD_FOLDER = 'uploads/about_images'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def serialize_about(doc):
    return {
        "_id": str(doc["_id"]),
        "title": doc.get("title", ""),
        "subtitle": doc.get("subtitle", ""),
        "info": doc.get("info", ""),
        "image": doc.get("image", None)
    }

# Add about entry
@about_bp.route('/add', methods=['POST'])
def add_about():
    title = request.form.get('title')
    subtitle = request.form.get('subtitle')
    info = request.form.get('info')

    if not title or not subtitle or not info:
        return jsonify({"error": "Missing required fields: title, subtitle, info"}), 400

    image = None
    if 'image' in request.files:
        image_file = request.files['image']
        if image_file.filename != '':
            filename = secure_filename(image_file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            image_file.save(filepath)
            image = filepath

    new_entry = {
        "title": title,
        "subtitle": subtitle,
        "info": info,
        "image": image
    }

    result = about_collection.insert_one(new_entry)
    return jsonify({"message": "About entry added", "id": str(result.inserted_id)}), 201

# Get all entries
@about_bp.route('/get-about', methods=['GET'])
def get_about():
    entries = about_collection.find()
    return jsonify([serialize_about(entry) for entry in entries]), 200

# Edit entry
@about_bp.route('/edit-about/<string:about_id>', methods=['PUT'])
def edit_about(about_id):
    title = request.form.get('title')
    subtitle = request.form.get('subtitle')
    info = request.form.get('info')

    update_data = {}
    if title: update_data['title'] = title
    if subtitle: update_data['subtitle'] = subtitle
    if info: update_data['info'] = info

    if 'image' in request.files:
        image_file = request.files['image']
        if image_file.filename != '':
            filename = secure_filename(image_file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            image_file.save(filepath)
            update_data['image'] = filepath

    if not update_data:
        return jsonify({"error": "No data provided for update"}), 400

    result = about_collection.update_one(
        {"_id": ObjectId(about_id)},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Entry not found"}), 404

    return jsonify({"message": "About entry updated"}), 200

# Delete entry
@about_bp.route('/delete-about/<string:about_id>', methods=['DELETE'])
def delete_about(about_id):
    result = about_collection.delete_one({"_id": ObjectId(about_id)})

    if result.deleted_count == 0:
        return jsonify({"error": "Entry not found"}), 404

    return jsonify({"message": "About entry deleted"}), 200


# Add gallery
@about_bp.route('/add-gallery', methods=['POST'])
def add_gallery():
    if 'images' not in request.files:
        return jsonify({"error": "No images provided"}), 400

    image_files = request.files.getlist('images')
    image_paths = []

    for image_file in image_files:
        if image_file.filename != '':
            filename = secure_filename(image_file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            image_file.save(filepath)
            image_paths.append(filepath)

    if not image_paths:
        return jsonify({"error": "No valid images uploaded"}), 400

    result = gallery_collection.insert_one({"images": image_paths})
    return jsonify({"message": "Gallery added", "id": str(result.inserted_id)}), 201

# View galleries
@about_bp.route('/get-gallery', methods=['GET'])
def get_gallery():
    galleries = gallery_collection.find()
    return jsonify([
        {"_id": str(g["_id"]), "images": g.get("images", [])}
        for g in galleries
    ]), 200

# Edit gallery
@about_bp.route('/edit-gallery/<string:gallery_id>', methods=['PUT'])
def edit_gallery(gallery_id):
    if 'images' not in request.files:
        return jsonify({"error": "No images provided"}), 400

    image_files = request.files.getlist('images')
    image_paths = []

    for image_file in image_files:
        if image_file.filename != '':
            filename = secure_filename(image_file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            image_file.save(filepath)
            image_paths.append(filepath)

    if not image_paths:
        return jsonify({"error": "No valid images uploaded"}), 400

    result = gallery_collection.update_one(
        {"_id": ObjectId(gallery_id)},
        {"$set": {"images": image_paths}}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Gallery not found"}), 404

    return jsonify({"message": "Gallery updated"}), 200

# Delete gallery
@about_bp.route('/delete-gallery/<string:gallery_id>', methods=['DELETE'])
def delete_gallery(gallery_id):
    result = gallery_collection.delete_one({"_id": ObjectId(gallery_id)})
    if result.deleted_count == 0:
        return jsonify({"error": "Gallery not found"}), 404
    return jsonify({"message": "Gallery deleted"}), 200