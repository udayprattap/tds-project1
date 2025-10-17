# Test cases for LLM Code Deployment API

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch
from flask import Flask

# Import the app
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from src.config import Config
from src.utils import validate_json_structure, decode_attachments
from src.readme_generator import generate_readme

@pytest.fixture
def client():
    """Flask test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def sample_request_data():
    """Sample valid request data"""
    return {
        "email": "test@example.com",
        "secret": "test-secret",
        "task": "test-task-123",
        "round": 1,
        "nonce": "test-nonce-456",
        "brief": "Create a simple todo list application with Bootstrap styling",
        "evaluation_url": "https://httpbin.org/post",
        "checks": ["Must have #add-task button", "Must display task count"],
        "attachments": []
    }

class TestAPI:
    """Test API endpoints"""
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get('/')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'service' in data
        assert 'endpoints' in data
    
    def test_api_endpoint_missing_json(self, client):
        """Test API endpoint with missing JSON"""
        response = client.post('/api')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_api_endpoint_missing_fields(self, client):
        """Test API endpoint with missing required fields"""
        response = client.post('/api', json={})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Missing required fields' in data['error']
    
    @patch('src.config.Config.validate_secret')
    def test_api_endpoint_invalid_secret(self, mock_validate_secret, client, sample_request_data):
        """Test API endpoint with invalid secret"""
        mock_validate_secret.return_value = False
        
        response = client.post('/api', json=sample_request_data)
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['error'] == 'Invalid secret'
    
    @patch('src.config.Config.validate_secret')
    def test_api_endpoint_invalid_round(self, mock_validate_secret, client, sample_request_data):
        """Test API endpoint with invalid round number"""
        mock_validate_secret.return_value = True  # Make secret validation pass
        sample_request_data['round'] = 3
        
        response = client.post('/api', json=sample_request_data)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Round must be 1 or 2' in data['error']

class TestValidation:
    """Test validation functions"""
    
    def test_validate_json_structure_valid(self, sample_request_data):
        """Test validation with valid data"""
        errors = validate_json_structure(sample_request_data)
        assert len(errors) == 0
    
    def test_validate_json_structure_missing_fields(self):
        """Test validation with missing fields"""
        data = {"email": "test@example.com"}
        errors = validate_json_structure(data)
        assert len(errors) > 0
        assert any("Missing required field" in error for error in errors)
    
    def test_validate_json_structure_invalid_email(self):
        """Test validation with invalid email"""
        data = {
            "email": "invalid-email",
            "secret": "test",
            "task": "test",
            "round": 1,
            "nonce": "test",
            "brief": "test",
            "evaluation_url": "https://example.com"
        }
        errors = validate_json_structure(data)
        assert any("Invalid email format" in error for error in errors)
    
    def test_validate_json_structure_invalid_url(self):
        """Test validation with invalid URL"""
        data = {
            "email": "test@example.com",
            "secret": "test",
            "task": "test",
            "round": 1,
            "nonce": "test",
            "brief": "test",
            "evaluation_url": "not-a-url"
        }
        errors = validate_json_structure(data)
        assert any("Evaluation URL must start with" in error for error in errors)

class TestUtilities:
    """Test utility functions"""
    
    def test_decode_attachments_empty(self):
        """Test decoding empty attachments"""
        result = decode_attachments([], "test-task")
        assert result == []
    
    def test_decode_attachments_valid(self):
        """Test decoding valid base64 attachments"""
        import base64
        
        test_content = "Hello, world!"
        encoded_content = base64.b64encode(test_content.encode()).decode()
        
        attachments = [{
            "filename": "test.txt",
            "content": encoded_content
        }]
        
        result = decode_attachments(attachments, "test-task")
        assert len(result) == 1
        
        # Read the file and verify content
        with open(result[0], 'r') as f:
            content = f.read()
        assert content == test_content
        
        # Cleanup
        os.unlink(result[0])
    
    def test_generate_readme(self):
        """Test README generation"""
        brief = "Create a todo list application"
        task_id = "test-123"
        
        readme = generate_readme(brief, task_id)
        
        assert task_id in readme
        assert brief in readme
        assert "# " in readme  # Has heading
        assert "## " in readme  # Has subheadings
        assert "MIT License" in readme

class TestConfig:
    """Test configuration"""
    
    def test_validate_secret_empty_list(self):
        """Test secret validation with empty valid secrets"""
        with patch.object(Config, 'VALID_SECRETS', ['']):
            assert Config.validate_secret("any-secret") == True
    
    def test_validate_secret_valid(self):
        """Test secret validation with valid secret"""
        with patch.object(Config, 'VALID_SECRETS', ['secret1', 'secret2']):
            assert Config.validate_secret("secret1") == True
            assert Config.validate_secret("secret2") == True
    
    def test_validate_secret_invalid(self):
        """Test secret validation with invalid secret"""
        with patch.object(Config, 'VALID_SECRETS', ['secret1', 'secret2']):
            assert Config.validate_secret("invalid") == False
            assert Config.validate_secret("") == False
    
    def test_get_repo_name(self):
        """Test repository name generation"""
        task_id = "test-123"
        email = "student@example.com"
        
        repo_name = Config.get_repo_name(task_id, email)
        
        assert task_id in repo_name
        assert "student-task-" in repo_name
        assert len(repo_name) > len(task_id)

# Integration test data
def create_test_request_file():
    """Create a test request file for CLI testing"""
    test_data = {
        "email": "test@example.com",
        "secret": "test-secret",
        "task": "cli-test-123",
        "round": 1,
        "nonce": "cli-test-nonce",
        "brief": "Create a simple calculator application with basic arithmetic operations",
        "evaluation_url": "https://httpbin.org/post",
        "checks": [
            "Must have calculator buttons for digits 0-9",
            "Must have operation buttons (+, -, *, /)",
            "Must have equals button",
            "Must display calculation result"
        ],
        "attachments": []
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f, indent=2)
        return f.name

if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v'])
    
    # Create test request file
    test_file = create_test_request_file()
    print(f"\nTest request file created: {test_file}")
    print(f"To test CLI: python cli.py {test_file}")