from flask import Blueprint, request, jsonify
from pymongo import MongoClient
import os
from bson import json_util
import json
from flask_cors import CORS  # ✅ Add this import

overlays_bp = Blueprint("overlays", __name__)

# Enable CORS for this blueprint
CORS(overlays_bp, origins=["https://livestream-webapp.onrender.com"])  # ✅ Only this line added

# Temporary: Hardcode MongoDB URI (remove this in production)
MONGO_URI = "mongodb+srv://yadavramjeekumar04_db_user:taCac7SpISZHrPIG@cluster0.rlke4mk.mongodb.net/rtsp_overlay_app?retryWrites=true&w=majority"

# Or use environment variable with fallback
# MONGO_URI = os.getenv('MONGODB_URI', "mongodb+srv://yadavramjeekumar04_db_user:taCac7SpISZHrPIG@cluster0.rlke4mk.mongodb.net/rtsp_overlay_app?retryWrites=true&w=majority")

try:
    client = MongoClient(MONGO_URI)
    # Test connection
    client.admin.command('ping')
    print(" MongoDB connected successfully!")
except Exception as e:
    print(f" MongoDB connection failed: {e}")
    raise

db = client["rtsp_overlay_app"]
overlays_collection = db["overlays"]

def serialize_doc(doc):
    """Convert MongoDB document to JSON serializable format"""
    return json.loads(json_util.dumps(doc))

# CREATE overlay
@overlays_bp.route("/", methods=["POST"])
def create_overlay():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        name = data.get("name")
        if not name:
            return jsonify({"error": "Overlay name is required"}), 400
        
        # Check if overlay already exists
        if overlays_collection.find_one({"name": name}):
            return jsonify({"error": "Overlay with this name already exists"}), 409
        
        # Validate required fields
        required_fields = ["type", "content", "x", "y", "width", "height"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Field '{field}' is required"}), 400
        
        # Insert new overlay
        result = overlays_collection.insert_one(data)
        return jsonify({
            "message": "Overlay created successfully",
            "id": str(result.inserted_id)
        }), 201
        
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

# READ all overlays
@overlays_bp.route("/", methods=["GET"])
def get_overlays():
    try:
        overlays = list(overlays_collection.find({}))
        serialized_overlays = [serialize_doc(ov) for ov in overlays]
        return jsonify(serialized_overlays), 200
    except Exception as e:
        return jsonify({"error": "Failed to fetch overlays"}), 500

# UPDATE overlay by name
@overlays_bp.route("/<string:name>", methods=["PUT"])
def update_overlay(name):
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Remove _id from update data to avoid modification
        data.pop('_id', None)
        
        result = overlays_collection.update_one(
            {"name": name}, 
            {"$set": data}
        )
        
        if result.matched_count == 0:
            return jsonify({"error": "Overlay not found"}), 404
            
        return jsonify({"message": "Overlay updated successfully"}), 200
        
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

# DELETE overlay by name
@overlays_bp.route("/<string:name>", methods=["DELETE"])
def delete_overlay(name):
    try:
        result = overlays_collection.delete_one({"name": name})
        if result.deleted_count == 0:
            return jsonify({"error": "Overlay not found"}), 404
        return jsonify({"message": "Overlay deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

# GET single overlay by name
@overlays_bp.route("/<string:name>", methods=["GET"])
def get_overlay(name):
    try:
        overlay = overlays_collection.find_one({"name": name})
        if not overlay:
            return jsonify({"error": "Overlay not found"}), 404
        return jsonify(serialize_doc(overlay)), 200
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500
