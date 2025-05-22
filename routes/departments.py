from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
from werkzeug.utils import secure_filename
import os

departments_bp = Blueprint('departments', __name__)

# MongoDB setup
client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/'))
db = client['Cluster0']
department_collection = db['departments']

# Upload folder
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads', 'departments')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def serialize_doc(doc):
    return {
        "_id": str(doc["_id"]),
        "title": doc.get("title", ""),
        "subtitle": doc.get("subtitle", ""),
        "info": doc.get("info", ""),
        "image": doc.get("image", ""),
        "category": doc.get("category", "")
    }

# Add department entry
@departments_bp.route('/add', methods=['POST'])
def add_department():
    title = request.form.get('title')
    subtitle = request.form.get('subtitle')
    info = request.form.get('info')
    category = request.form.get('category')
    image = request.files.get('image')

    image_path = None
    if image and image.filename:
        cat_folder = os.path.join(UPLOAD_FOLDER, category)
        os.makedirs(cat_folder, exist_ok=True)
        filename = secure_filename(image.filename)
        image_path = os.path.join(cat_folder, filename)
        image.save(image_path)

    new_doc = {
        "title": title,
        "subtitle": subtitle,
        "info": info,
        "category": category,
        "image": image_path
    }

    result = department_collection.insert_one(new_doc)
    return jsonify({"message": "Department entry added", "id": str(result.inserted_id)}), 201

# Get department entries by category
@departments_bp.route('/<category>/get', methods=['GET'])
def get_department_by_category(category):
    entries = department_collection.find({"category": category})
    return jsonify([serialize_doc(doc) for doc in entries]), 200

# Edit department entry
@departments_bp.route('/edit/<string:entry_id>', methods=['PUT'])
def edit_department(entry_id):
    update_data = {}
    for field in ['title', 'subtitle', 'info', 'category']:
        val = request.form.get(field)
        if val:
            update_data[field] = val

    image = request.files.get('image')
    if image and image.filename:
        category = update_data.get('category', 'general')
        cat_folder = os.path.join(UPLOAD_FOLDER, category)
        os.makedirs(cat_folder, exist_ok=True)
        filename = secure_filename(image.filename)
        image_path = os.path.join(cat_folder, filename)
        image.save(image_path)
        update_data['image'] = image_path

    result = department_collection.update_one(
        {"_id": ObjectId(entry_id)},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Entry not found"}), 404

    return jsonify({"message": "Department entry updated"}), 200

# Delete department entry
@departments_bp.route('/delete/<string:entry_id>', methods=['DELETE'])
def delete_department(entry_id):
    result = department_collection.delete_one({"_id": ObjectId(entry_id)})
    if result.deleted_count == 0:
        return jsonify({"error": "Entry not found"}), 404

    return jsonify({"message": "Department entry deleted"}), 200
