# TODO (Copilot): Entry point CLI for the LLM Deployment Agent.
# Supports:
# - python cli.py build-request.json → reads task JSON, builds & deploys app
# - python cli.py revise-request.json → updates existing repo based on round 2 brief
# Loads JSON, calls main flow, prints success or error

import sys
import json
import logging
from datetime import datetime
from src.api_handler import process_deployment_request
from src.config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_request_file(file_path):
    """Load and validate request JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Add timestamp if not present
        if 'timestamp' not in data:
            data['timestamp'] = datetime.utcnow().isoformat()
        
        return data
    except FileNotFoundError:
        logger.error(f"Request file not found: {file_path}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {file_path}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error loading {file_path}: {str(e)}")
        return None

def validate_config():
    """Validate that required configuration is present"""
    errors = Config.validate_config()
    if errors:
        logger.error("Configuration errors:")
        for error in errors:
            logger.error(f"  - {error}")
        return False
    return True

def main():
    """Main CLI entry point"""
    if len(sys.argv) != 2:
        print("Usage: python cli.py <request.json>")
        print("Example: python cli.py build-request.json")
        sys.exit(1)
    
    request_file = sys.argv[1]
    
    logger.info(f"LLM Code Deployment CLI - Processing {request_file}")
    
    # Validate configuration
    if not validate_config():
        logger.error("Configuration validation failed. Check your .env file.")
        sys.exit(1)
    
    # Load request data
    request_data = load_request_file(request_file)
    if not request_data:
        sys.exit(1)
    
    # Validate request structure
    from src.utils import validate_json_structure
    validation_errors = validate_json_structure(request_data)
    if validation_errors:
        logger.error("Request validation errors:")
        for error in validation_errors:
            logger.error(f"  - {error}")
        sys.exit(1)
    
    # Validate secret
    if not Config.validate_secret(request_data.get('secret', '')):
        logger.error("Invalid secret in request")
        sys.exit(1)
    
    # Process the deployment
    try:
        logger.info(f"Starting deployment for task {request_data['task']}")
        process_deployment_request(request_data)
        logger.info("Deployment completed successfully")
        print(f"✅ Successfully processed {request_file}")
        
    except Exception as e:
        logger.error(f"Deployment failed: {str(e)}")
        print(f"❌ Failed to process {request_file}: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()