from flask import Blueprint, request, jsonify
from pymongo import MongoClient

overlays_bp = Blueprint("overlays", __name__)

# MongoDB Atlas connection
MONGO_URI = "mongodb+srv://yadavramjeekumar04_db_user:taCac7SpISZHrPIG@cluster0.rlke4mk.mongodb.net/"
client = MongoClient(MONGO_URI)

db = client["rtsp_overlay_app"]
overlays_collection = db["overlays"]

# CREATE overlay
@overlays_bp.route("/", methods=["POST"])
def create_overlay():
    data = request.json
    if not data.get("name"):
        return jsonify({"error": "Overlay name is required"}), 400
    
    overlays_collection.insert_one(data)
    return jsonify({"message": "Overlay created successfully"}), 201

# READ all overlays
@overlays_bp.route("/", methods=["GET"])
def get_overlays():
    overlays = list(overlays_collection.find({}, {"_id": 0}))
    return jsonify(overlays), 200

# UPDATE overlay by name
@overlays_bp.route("/<string:name>", methods=["PUT"])
def update_overlay(name):
    data = request.json
    result = overlays_collection.update_one({"name": name}, {"$set": data})
    if result.matched_count == 0:
        return jsonify({"error": "Overlay not found"}), 404
    return jsonify({"message": "Overlay updated successfully"}), 200

# DELETE overlay by name
@overlays_bp.route("/<string:name>", methods=["DELETE"])
def delete_overlay(name):
    result = overlays_collection.delete_one({"name": name})
    if result.deleted_count == 0:
        return jsonify({"error": "Overlay not found"}), 404
    return jsonify({"message": "Overlay deleted successfully"}), 200
