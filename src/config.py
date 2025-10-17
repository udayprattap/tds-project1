# Configuration module for LLM Code Deployment API

import os
import hashlib
import secrets
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration settings for the deployment API"""
    
    # API Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_urlsafe(32))
    VALID_SECRETS = os.environ.get('VALID_SECRETS', '').split(',')
    
    # GitHub Configuration
    GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
    GITHUB_USERNAME = os.environ.get('GITHUB_USERNAME')
    GITHUB_ORG = os.environ.get('GITHUB_ORG')  # Optional: use org instead of personal
    
    # LLM Configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_BASE_URL = os.environ.get('OPENAI_BASE_URL', 'https://api.openai.com/v1')
    LLM_MODEL = os.environ.get('LLM_MODEL', 'gpt-4o-mini')
    
    # Deployment Settings
    MAX_DEPLOYMENT_TIME = int(os.environ.get('MAX_DEPLOYMENT_TIME', 600))  # 10 minutes
    RETRY_ATTEMPTS = int(os.environ.get('RETRY_ATTEMPTS', 5))
    TEMP_DIR = os.environ.get('TEMP_DIR', './temp')
    
    # GitHub Pages Settings
    PAGES_BRANCH = os.environ.get('PAGES_BRANCH', 'main')
    PAGES_SOURCE = os.environ.get('PAGES_SOURCE', '/')  # or '/docs'
    
    @classmethod
    def validate_secret(cls, secret):
        """Validate the provided secret against known valid secrets"""
        if not secret:
            return False
        
        # If no valid secrets configured, accept any non-empty secret (dev mode)
        if not cls.VALID_SECRETS or cls.VALID_SECRETS == ['']:
            return True
        
        # Check against configured secrets
        return secret in cls.VALID_SECRETS
    
    @classmethod
    def get_repo_name(cls, task_id, student_email):
        """Generate a unique repository name"""
        # Create a short hash from email for uniqueness
        email_hash = hashlib.md5(student_email.encode()).hexdigest()[:8]
        return f"student-task-{task_id}-{email_hash}"
    
    @classmethod
    def validate_config(cls):
        """Validate that required configuration is present"""
        errors = []
        
        if not cls.GITHUB_TOKEN:
            errors.append("GITHUB_TOKEN is required")
        
        if not cls.GITHUB_USERNAME and not cls.GITHUB_ORG:
            errors.append("Either GITHUB_USERNAME or GITHUB_ORG is required")
        
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is required")
        
        return errors
    
    @classmethod
    def get_github_owner(cls):
        """Get the GitHub owner (org or username)"""
        return cls.GITHUB_ORG if cls.GITHUB_ORG else cls.GITHUB_USERNAME