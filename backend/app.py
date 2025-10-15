from flask import Flask, request, jsonify
from flask_cors import CORS
from routes.overlays import overlays_bp
from services.rtsp_stream import convert_rtsp_to_hls
import os

app = Flask(__name__)
CORS(app)

# Register blueprint (for overlay CRUD)
app.register_blueprint(overlays_bp, url_prefix="/api/overlays")

# Create folder to store HLS stream
os.makedirs("static", exist_ok=True)

@app.route("/")
def home():
    return {"message": "RTSP Overlay Backend is running!"}

#  Route to start RTSP stream conversion
@app.route("/api/start-stream", methods=["POST"])
def start_stream():
    data = request.json
    rtsp_url = data.get("rtsp_url")

    if not rtsp_url:
        return jsonify({"error": "RTSP URL is required"}), 400

    # Convert RTSP to HLS
    convert_rtsp_to_hls(rtsp_url)
    return jsonify({"message": "Stream started", "hls_url": "/static/stream.m3u8"})

if __name__ == "__main__":
    app.run(debug=True)
