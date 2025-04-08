from flask import Flask, jsonify, request, render_template, send_file, send_from_directory
from services.video_generator import VideoGenerator
from services.analyzer import Analyzer
from api.quotes import QuoteAPI
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize services
generator = VideoGenerator()
analyzer = Analyzer()
quotes_api = QuoteAPI()

# Define the output directory path
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download/<path:filename>')
def download_file(filename):
    try:
        # Check if the filename is already an absolute path
        if not os.path.isabs(filename):
            # If it's not absolute, assume it's relative to the output directory
            filename = os.path.join(OUTPUT_DIR, filename)
        
        # Handle the case where only the filename is passed (without the path)
        if os.path.basename(filename) == filename:
            filename = os.path.join(OUTPUT_DIR, filename)
            
        if not os.path.exists(filename):
            logger.error(f"File not found: {filename}")
            return jsonify({"error": "File not found"}), 404
            
        return send_file(filename, as_attachment=True)
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        return jsonify({"error": "File not found"}), 404

@app.route('/video/<path:filename>')
def serve_video(filename):
    """Serve the video file for preview"""
    try:
        return send_from_directory(OUTPUT_DIR, filename, mimetype='video/mp4')
    except Exception as e:
        logger.error(f"Error serving video file: {e}")
        return jsonify({"success": False, "error": "Video file not found"}), 404

@app.route('/get-random-quote', methods=['GET'])
def get_random_quote():
    """Get a random quote without generating video"""
    try:
        quote_data = quotes_api.get_random_quote()
        if not quote_data:
            return jsonify({"error": "Failed to fetch quote", "success": False}), 500
            
        return jsonify({
            "success": True,
            "quote": quote_data["quote"],
            "author": quote_data["author"],
            "category": quote_data["type"]
        }), 200
    except Exception as e:
        logger.error(f"Error fetching quote: {e}")
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/generate-video', methods=['POST'])
def generate_video():
    """
    Generate a video with a random quote and matching background
    Expects: {
        "quote": "quote text", 
        "author": "author name"
    }
    """
    try:
        data = request.get_json()
        if not data or "quote" not in data or "author" not in data:
            return jsonify({"error": "Missing quote or author", "success": False}), 400
            
        quote = data["quote"]
        author = data["author"]

        # Get matching video URL
        video_urls = analyzer.get_video_url(quote)
        if not video_urls or not video_urls.get("high_quality"):
            return jsonify({"error": "Failed to find matching video", "success": False}), 500

        # Generate video
        output_path = generator.generate_video(quote, author, video_urls["high_quality"])
        
        if not output_path:
            return jsonify({"success": False, "error": "Failed to generate video"}), 500

        # Extract just the filename for client use
        video_filename = os.path.basename(output_path)
        
        return jsonify({
            "success": True,
            "video_path": video_filename,
            "quote": quote,
            "author": author
        }), 200

    except Exception as e:
        logger.error(f"Error generating video: {e}")
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/generate-video-custom', methods=['POST'])
def generate_video_custom():
    """
    Generate a video with a custom quote
    Expects JSON body with: {
        "quote": "your quote",
        "author": "quote author"
    }
    """
    try:
        data = request.get_json()
        if not data or "quote" not in data or "author" not in data:
            return jsonify({"error": "Missing quote or author", "success": False}), 400

        # Get matching video URL
        video_urls = analyzer.get_video_url(data["quote"])
        if not video_urls or not video_urls.get("high_quality"):
            return jsonify({"error": "Failed to find matching video", "success": False}), 500

        # Generate video
        output_path = generator.generate_video(
            quote=data["quote"],
            author=data["author"],
            video_url=video_urls["high_quality"]
        )

        if not output_path:
            return jsonify({"error": "Failed to generate video", "success": False}), 500

        # Return just the filename, not the full path
        video_filename = os.path.basename(output_path)
        
        return jsonify({
            "success": True,
            "video_path": video_filename,
            "quote": data["quote"],
            "author": data["author"]
        }), 200

    except Exception as e:
        logger.error(f"Error generating custom video: {e}")
        return jsonify({"error": str(e), "success": False}), 500

# Route to list available videos
@app.route('/api/videos', methods=['GET'])
def list_videos():
    try:
        videos = []
        for file in os.listdir(OUTPUT_DIR):
            if file.endswith('.mp4'):
                file_path = os.path.join(OUTPUT_DIR, file)
                file_size = os.path.getsize(file_path)
                videos.append({
                    'filename': file,
                    'size': file_size,
                    'created': os.path.getctime(file_path)
                })
        return jsonify({"success": True, "videos": videos})
    except Exception as e:
        logger.error(f"Error listing videos: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# Route to download video files
@app.route('/api/download/<filename>')
def api_download_video(filename):
    """API endpoint to download a video file"""
    try:
        file_path = os.path.join(OUTPUT_DIR, filename)
        if not os.path.exists(file_path):
            app.logger.error(f"File not found: {file_path}")
            return jsonify({"error": "File not found"}), 404
            
        # Send the file as an attachment (triggers download)
        return send_from_directory(
            OUTPUT_DIR, 
            filename, 
            as_attachment=True,
            download_name=filename  # For Flask >= 2.0
        )
    except Exception as e:
        app.logger.error(f"Error downloading file: {e}")
        return jsonify({"error": "Unable to download file"}), 500

@app.route('/api/videos/<filename>')
def api_serve_video(filename):
    try:
        return send_from_directory(OUTPUT_DIR, filename, mimetype='video/mp4')
    except Exception as e:
        app.logger.error(f"Error serving video: {e}")
        return jsonify({"error": "Video not found"}), 404

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)