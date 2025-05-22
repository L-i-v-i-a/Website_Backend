from flask import Blueprint

news_bp = Blueprint('news', __name__)

@news_bp.route('/')
def news_page():
    return 'This is the News Page'
from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from bson import ObjectId
import os
from datetime import datetime

news_bp = Blueprint('news', __name__)

# MongoDB connection
client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/'))
db = client['Cluster0']
news_collection = db['news']

# Upload folder
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads', 'news_media')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def serialize_news(doc):
    return {
        "_id": str(doc["_id"]),
        "title": doc.get("title", ""),
        "subtitle": doc.get("subtitle", ""),
        "info": doc.get("info", ""),
        "date": doc.get("date", ""),
        "image": doc.get("image"),
        "video": doc.get("video")
    }

# Add news entry: POST /news/add
@news_bp.route('/add', methods=['POST'])
def add_news():
    title = request.form.get('title')
    subtitle = request.form.get('subtitle')
    info = request.form.get('info')
    date = request.form.get('date')  # format: YYYY-MM-DD

    if not all([title, subtitle, info, date]):
        return jsonify({"error": "Missing required fields: title, subtitle, info, date"}), 400

    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Date format must be YYYY-MM-DD"}), 400

    image = request.files.get('image')
    video = request.files.get('video')

    image_path = None
    video_path = None

    if image and image.filename != '':
        filename = secure_filename(image.filename)
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        image.save(image_path)

    if video and video.filename != '':
        filename = secure_filename(video.filename)
        video_path = os.path.join(UPLOAD_FOLDER, filename)
        video.save(video_path)

    news_entry = {
        "title": title,
        "subtitle": subtitle,
        "info": info,
        "date": date,
        "image": image_path,
        "video": video_path
    }

    result = news_collection.insert_one(news_entry)
    return jsonify({"message": "News entry added", "id": str(result.inserted_id)}), 201

# Get all news entries: GET /news/get-news
@news_bp.route('/get-news', methods=['GET'])
def get_news():
    entries = news_collection.find()
    return jsonify([serialize_news(entry) for entry in entries]), 200

# Edit news entry: PUT /news/edit-news/<id>
@news_bp.route('/edit-news/<string:news_id>', methods=['PUT'])
def edit_news(news_id):
    update_data = {}

    title = request.form.get('title')
    subtitle = request.form.get('subtitle')
    info = request.form.get('info')
    date = request.form.get('date')

    if date:
        try:
            datetime.strptime(date, "%Y-%m-%d")
            update_data["date"] = date
        except ValueError:
            return jsonify({"error": "Date format must be YYYY-MM-DD"}), 400

    if title:
        update_data["title"] = title
    if subtitle:
        update_data["subtitle"] = subtitle
    if info:
        update_data["info"] = info

    image = request.files.get('image')
    video = request.files.get('video')

    if image and image.filename != '':
        filename = secure_filename(image.filename)
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        image.save(image_path)
        update_data["image"] = image_path

    if video and video.filename != '':
        filename = secure_filename(video.filename)
        video_path = os.path.join(UPLOAD_FOLDER, filename)
        video.save(video_path)
        update_data["video"] = video_path

    result = news_collection.update_one({"_id": ObjectId(news_id)}, {"$set": update_data})

    if result.matched_count == 0:
        return jsonify({"error": "News entry not found"}), 404

    return jsonify({"message": "News entry updated"}), 200

# Delete news entry: DELETE /news/delete-news/<id>
@news_bp.route('/delete-news/<string:news_id>', methods=['DELETE'])
def delete_news(news_id):
    result = news_collection.delete_one({"_id": ObjectId(news_id)})

    if result.deleted_count == 0:
        return jsonify({"error": "News entry not found"}), 404

    return jsonify({"message": "News entry deleted"}), 200
