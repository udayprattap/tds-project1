# Utility functions for LLM Code Deployment API

import os
import json
import base64
import logging
import tempfile
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def save_request_log(request_data: Dict[str, Any]) -> str:
    """
    Save request data to a log file for debugging and audit purposes
    
    Args:
        request_data: The complete request data
        
    Returns:
        Path to the saved log file
    """
    try:
        # Create logs directory if it doesn't exist
        logs_dir = os.path.join(os.getcwd(), 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        email_safe = request_data.get('email', 'unknown').replace('@', '_at_').replace('.', '_')
        task_id = request_data.get('task', 'unknown')
        round_num = request_data.get('round', 0)
        
        filename = f"{timestamp}_{email_safe}_{task_id}_round{round_num}.json"
        log_path = os.path.join(logs_dir, filename)
        
        # Create a copy without sensitive data for logging
        log_data = dict(request_data)
        if 'secret' in log_data:
            log_data['secret'] = '[REDACTED]'
        
        # Add metadata
        log_data['_metadata'] = {
            'logged_at': datetime.utcnow().isoformat(),
            'log_file': filename
        }
        
        # Save to file
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Request logged to {log_path}")
        return log_path
        
    except Exception as e:
        logger.error(f"Failed to save request log: {str(e)}")
        return ""

def decode_attachments(attachments: List[Dict[str, Any]], task_id: str) -> List[str]:
    """
    Decode base64 attachments and save to temporary files
    
    Args:
        attachments: List of attachment objects with 'filename' and 'content' (base64)
        task_id: Task identifier for unique naming
        
    Returns:
        List of file paths to decoded attachments
    """
    attachment_files = []
    
    try:
        # Create temp directory for this task
        temp_dir = os.path.join(tempfile.gettempdir(), f"task_{task_id}")
        os.makedirs(temp_dir, exist_ok=True)
        
        for i, attachment in enumerate(attachments):
            try:
                # Get filename and content
                filename = attachment.get('filename', f'attachment_{i}')
                content_b64 = attachment.get('content', '')
                
                if not content_b64:
                    logger.warning(f"Empty content for attachment {filename}")
                    continue
                
                # Decode base64 content
                try:
                    content_bytes = base64.b64decode(content_b64)
                except Exception as e:
                    logger.error(f"Failed to decode base64 for {filename}: {str(e)}")
                    continue
                
                # Save to temporary file
                file_path = os.path.join(temp_dir, filename)
                
                # Determine if content is text or binary
                try:
                    # Try to decode as text first
                    content_text = content_bytes.decode('utf-8')
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content_text)
                except UnicodeDecodeError:
                    # Save as binary
                    with open(file_path, 'wb') as f:
                        f.write(content_bytes)
                
                attachment_files.append(file_path)
                logger.info(f"Decoded attachment: {filename} -> {file_path}")
                
            except Exception as e:
                logger.error(f"Failed to process attachment {i}: {str(e)}")
                continue
        
        return attachment_files
        
    except Exception as e:
        logger.error(f"Failed to decode attachments: {str(e)}")
        return []

def create_license_file() -> str:
    """
    Create MIT license content
    
    Returns:
        MIT license text
    """
    current_year = datetime.utcnow().year
    
    return f"""MIT License
Copyright (c) {current_year} Student Project
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

def validate_json_structure(data: Dict[str, Any]) -> List[str]:
    """
    Validate the structure of incoming JSON requests
    
    Args:
        data: Request data to validate
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    # Required fields
    required_fields = {
        'email': str,
        'secret': str,
        'task': str,
        'round': int,
        'nonce': str,
        'brief': str,
        'evaluation_url': str
    }
    
    for field, expected_type in required_fields.items():
        if field not in data:
            errors.append(f"Missing required field: {field}")
        elif not isinstance(data[field], expected_type):
            errors.append(f"Field {field} must be of type {expected_type.__name__}")
    
    # Validate round number
    if 'round' in data and data['round'] not in [1, 2]:
        errors.append("Round must be 1 or 2")
    
    # Validate email format (basic)
    if 'email' in data:
        email = data['email']
        if '@' not in email or '.' not in email.split('@')[-1]:
            errors.append("Invalid email format")
    
    # Validate URL format (basic)
    if 'evaluation_url' in data:
        url = data['evaluation_url']
        if not url.startswith(('http://', 'https://')):
            errors.append("Evaluation URL must start with http:// or https://")
    
    # Validate attachments structure if present
    if 'attachments' in data:
        attachments = data['attachments']
        if not isinstance(attachments, list):
            errors.append("Attachments must be a list")
        else:
            for i, attachment in enumerate(attachments):
                if not isinstance(attachment, dict):
                    errors.append(f"Attachment {i} must be an object")
                elif 'filename' not in attachment or 'content' not in attachment:
                    errors.append(f"Attachment {i} must have filename and content fields")
    
    return errors

def cleanup_temp_files(task_id: str):
    """
    Clean up temporary files for a task
    
    Args:
        task_id: Task identifier
    """
    try:
        temp_dir = os.path.join(tempfile.gettempdir(), f"task_{task_id}")
        if os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)
            logger.info(f"Cleaned up temp directory: {temp_dir}")
    except Exception as e:
        logger.warning(f"Failed to cleanup temp files for {task_id}: {str(e)}")

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to be safe for filesystem use
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    import re
    
    # Replace unsafe characters with underscores
    safe_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove or replace other problematic characters
    safe_filename = safe_filename.replace(' ', '_')
    safe_filename = re.sub(r'_{2,}', '_', safe_filename)  # Multiple underscores to single
    safe_filename = safe_filename.strip('_')  # Remove leading/trailing underscores
    
    # Ensure it's not empty
    if not safe_filename:
        safe_filename = 'unnamed_file'
    
    return safe_filename