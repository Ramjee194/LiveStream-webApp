from flask import Flask, request, jsonify
from flask_cors import CORS
from routes.overlays import overlays_bp
from services.rtsp_stream import convert_rtsp_to_hls
import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Register blueprint
app.register_blueprint(overlays_bp, url_prefix="/api/overlays")

# Create folders
os.makedirs("static/streams", exist_ok=True)

@app.route("/")
def home():
    return {"message": "RTSP Overlay Backend is running!", "status": "healthy"}

@app.route("/api/start-stream", methods=["POST"])
def start_stream():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        rtsp_url = data.get("rtsp_url")
        if not rtsp_url:
            return jsonify({"error": "RTSP URL is required"}), 400

        # Validate RTSP URL format
        if not rtsp_url.startswith(('rtsp://', 'rtsps://')):
            return jsonify({"error": "Invalid RTSP URL format"}), 400

        # Convert RTSP to HLS with unique stream ID
        stream_id = convert_rtsp_to_hls(rtsp_url)
        if not stream_id:
            return jsonify({"error": "Failed to start stream conversion"}), 500

        return jsonify({
            "message": "Stream started successfully", 
            "hls_url": f"/static/streams/{stream_id}/stream.m3u8",
            "stream_id": stream_id
        }), 200

    except Exception as e:
        app.logger.error(f"Stream start error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/stream-health")
def stream_health():
    return jsonify({"status": "running", "timestamp": "2024-01-01T00:00:00Z"})

if __name__ == "__main__":
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(
        host=os.getenv('FLASK_HOST', '0.0.0.0'),
        port=int(os.getenv('FLASK_PORT', 5000)),
        debug=debug_mode
    )