# LLM Code Deployment API
# Main Flask application that handles build and revise requests

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
import threading
from datetime import datetime, timezone
from src.api_handler import process_deployment_request
from src.config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# TODO (Copilot): Implement /api POST handler.
# It should:
# - Accept JSON with fields: email, secret, task, round, nonce, brief, checks, attachments, evaluation_url
# - Validate the secret
# - Respond 200 JSON {"status": "ok"} on success, 400 on error
# - Save the request to disk or database (optional)
# - Call generate_and_deploy_app(...) with parsed brief, attachments, task ID
# - After deployment, POST to evaluation_url within 10 minutes with:
#   { email, task, round, nonce, repo_url, commit_sha, pages_url }
# - Retry POST to evaluation_url on failure using backoff (1s, 2s, 4s…)

@app.route('/api', methods=['POST'])
def handle_deployment_request():
    """
    Main API endpoint for handling build and revise requests.
    Accepts JSON with deployment parameters and processes asynchronously.
    """
    try:
        # Validate Content-Type
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'secret', 'task', 'round', 'nonce', 'brief', 'evaluation_url']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        # Validate secret
        if not Config.validate_secret(data['secret']):
            logger.warning(f"Invalid secret attempted from {data.get('email', 'unknown')}")
            return jsonify({"error": "Invalid secret"}), 401
        
        # Validate round number
        if data['round'] not in [1, 2]:
            return jsonify({"error": "Round must be 1 or 2"}), 400
        
        # Log the request
        logger.info(f"Received {data['round']} request for {data['email']} - Task: {data['task']}")
        
        # Process deployment in background thread to avoid timeout
        thread = threading.Thread(
            target=process_deployment_request,
            args=(data,),
            daemon=True
        )
        thread.start()
        
        # Return immediate success response
        return jsonify({
            "status": "ok",
            "message": f"Round {data['round']} deployment started",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "LLM Code Deployment API",
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API info"""
    return jsonify({
        "service": "LLM Code Deployment API",
        "version": "1.0.0",
        "endpoints": {
            "/api": "POST - Submit deployment request",
            "/health": "GET - Health check"
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting LLM Code Deployment API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)