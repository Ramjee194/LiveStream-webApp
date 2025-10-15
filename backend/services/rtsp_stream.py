import os
import subprocess

def convert_rtsp_to_hls(rtsp_url):
    """
    Converts an RTSP stream to HLS format (.m3u8) for browser playback.
    """
    os.makedirs("static", exist_ok=True)

    command = [
        "ffmpeg",
        "-i", rtsp_url,             # Input RTSP stream
        "-c:v", "copy",             # Copy video codec
        "-c:a", "aac",              # Convert audio codec to AAC
        "-f", "hls",                # Output format HLS
        "-hls_time", "2",           # Split into 2-sec segments
        "-hls_list_size", "3",      # Only keep latest 3 segments
        "-hls_flags", "delete_segments",
        "static/stream.m3u8"
    ]

    try:
        subprocess.Popen(command)
        print(" FFmpeg started converting RTSP to HLS")
    except Exception as e:
        print(" Error starting stream:", e)
