import os
import subprocess
import uuid
from datetime import datetime
import threading
import time

# Store active streams
active_streams = {}

def convert_rtsp_to_hls(rtsp_url):
    """
    Convert RTSP stream to HLS format using FFmpeg
    Returns stream_id if successful, None if failed
    """
    try:
        # Generate unique stream ID
        stream_id = str(uuid.uuid4())[:8]
        stream_dir = f"static/streams/{stream_id}"
        os.makedirs(stream_dir, exist_ok=True)
        
        # HLS output path
        output_pattern = f"{stream_dir}/stream_%03d.ts"
        playlist_path = f"{stream_dir}/stream.m3u8"
        
        # FFmpeg command for RTSP to HLS conversion
        ffmpeg_cmd = [
            'ffmpeg',
            '-i', rtsp_url,           # Input RTSP URL
            '-c:v', 'libx264',        # Video codec
            '-c:a', 'aac',            # Audio codec
            '-f', 'hls',              # Output format HLS
            '-hls_time', '4',         # Segment length in seconds
            '-hls_list_size', '6',    # Number of segments in playlist
            '-hls_segment_filename', output_pattern,
            '-hls_flags', 'delete_segments',  # Delete old segments
            playlist_path
        ]
        
        # Start FFmpeg process
        process = subprocess.Popen(
            ffmpeg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE
        )
        
        # Store stream info
        active_streams[stream_id] = {
            'process': process,
            'rtsp_url': rtsp_url,
            'started_at': datetime.now(),
            'stream_dir': stream_dir,
            'playlist_path': playlist_path
        }
        
        # Start monitoring thread
        monitor_thread = threading.Thread(
            target=monitor_stream_process,
            args=(stream_id, process),
            daemon=True
        )
        monitor_thread.start()
        
        print(f"Started stream conversion: {stream_id} for {rtsp_url}")
        return stream_id
        
    except Exception as e:
        print(f"Error starting stream conversion: {str(e)}")
        return None

def monitor_stream_process(stream_id, process):
    """
    Monitor FFmpeg process and clean up if it stops
    """
    try:
        # Wait for process to complete
        process.wait()
        
        # Clean up if process ended
        if stream_id in active_streams:
            cleanup_stream(stream_id)
            print(f"Stream {stream_id} stopped and cleaned up")
            
    except Exception as e:
        print(f"Error monitoring stream {stream_id}: {str(e)}")

def stop_stream(stream_id):
    """
    Stop a specific stream by ID
    """
    if stream_id in active_streams:
        stream_info = active_streams[stream_id]
        process = stream_info['process']
        
        # Terminate FFmpeg process
        try:
            process.terminate()
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
        
        cleanup_stream(stream_id)
        return True
    return False

def cleanup_stream(stream_id):
    """
    Clean up stream resources
    """
    if stream_id in active_streams:
        stream_info = active_streams.pop(stream_id)
        
        # Optional: Delete stream files
        try:
            import shutil
            if os.path.exists(stream_info['stream_dir']):
                shutil.rmtree(stream_info['stream_dir'])
        except Exception as e:
            print(f"Error cleaning up stream files: {str(e)}")

def get_active_streams():
    """
    Get list of active streams
    """
    return list(active_streams.keys())

def get_stream_info(stream_id):
    """
    Get information about a specific stream
    """
    return active_streams.get(stream_id)