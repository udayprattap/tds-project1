# Evaluation Endpoint Notifier
# Handles POST requests to evaluation endpoints with retry logic

import requests
import logging
import time
import json
from typing import Dict, Any
from datetime import datetime

from .config import Config

logger = logging.getLogger(__name__)

class EvaluationNotifier:
    """
    Handles notification of evaluation endpoints with retry logic
    """
    
    def __init__(self):
        self.max_retries = Config.RETRY_ATTEMPTS
        self.timeout = 30  # 30 second timeout for requests
    
    # TODO (Copilot): POST to evaluation_url with:
    # {
    #   email, task, round, nonce,
    #   repo_url, commit_sha, pages_url
    # }
    # Headers: Content-Type: application/json
    # Retry on failure: exponential backoff (1s, 2s, 4s…) up to 5 times
    # Log response and success/failure
    
    def notify_evaluation_endpoint(self, evaluation_url: str, data: Dict[str, Any]) -> bool:
        """
        Send evaluation data to the endpoint with retry logic
        
        Args:
            evaluation_url: URL to POST the evaluation data to
            data: Dictionary containing evaluation results
            
        Returns:
            True if notification was successful, False otherwise
        """
        if not evaluation_url:
            logger.warning("No evaluation URL provided")
            return False
        
        # Add timestamp to data
        data['timestamp'] = datetime.utcnow().isoformat()
        
        logger.info(f"Notifying evaluation endpoint: {evaluation_url}")
        logger.debug(f"Evaluation data: {json.dumps(data, indent=2)}")
        
        for attempt in range(self.max_retries):
            try:
                # Calculate backoff delay: 1s, 2s, 4s, 8s, 16s
                if attempt > 0:
                    delay = 2 ** (attempt - 1)
                    logger.info(f"Retrying in {delay} seconds (attempt {attempt + 1}/{self.max_retries})")
                    time.sleep(delay)
                
                # Make the POST request
                response = requests.post(
                    evaluation_url,
                    json=data,
                    headers={
                        'Content-Type': 'application/json',
                        'User-Agent': 'LLM-Code-Deployment/1.0'
                    },
                    timeout=self.timeout
                )
                
                # Log the response
                logger.info(f"Evaluation endpoint response: {response.status_code}")
                logger.debug(f"Response body: {response.text}")
                
                # Check if successful
                if response.status_code in [200, 201, 202]:
                    logger.info("Successfully notified evaluation endpoint")
                    return True
                elif response.status_code in [400, 401, 403, 404]:
                    # Client errors - don't retry
                    logger.error(f"Client error {response.status_code}, not retrying: {response.text}")
                    return False
                else:
                    # Server errors - retry
                    logger.warning(f"Server error {response.status_code}, will retry: {response.text}")
                    continue
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout on attempt {attempt + 1}")
                continue
                
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"Connection error on attempt {attempt + 1}: {str(e)}")
                continue
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error on attempt {attempt + 1}: {str(e)}")
                continue
                
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {str(e)}")
                continue
        
        logger.error(f"Failed to notify evaluation endpoint after {self.max_retries} attempts")
        return False
    
    def notify_success(
        self,
        evaluation_url: str,
        email: str,
        task: str,
        round_num: int,
        nonce: str,
        repo_url: str,
        commit_sha: str,
        pages_url: str
    ) -> bool:
        """
        Notify evaluation endpoint of successful deployment
        
        Args:
            evaluation_url: URL to POST to
            email: Student email
            task: Task identifier
            round_num: Round number (1 or 2)
            nonce: Request nonce
            repo_url: GitHub repository URL
            commit_sha: Git commit SHA
            pages_url: GitHub Pages URL
            
        Returns:
            True if notification was successful
        """
        data = {
            'email': email,
            'task': task,
            'round': round_num,
            'nonce': nonce,
            'repo_url': repo_url,
            'commit_sha': commit_sha,
            'pages_url': pages_url,
            'status': 'success'
        }
        
        return self.notify_evaluation_endpoint(evaluation_url, data)
    
    def notify_failure(
        self,
        evaluation_url: str,
        email: str,
        task: str,
        round_num: int,
        nonce: str,
        error: str
    ) -> bool:
        """
        Notify evaluation endpoint of failed deployment
        
        Args:
            evaluation_url: URL to POST to
            email: Student email
            task: Task identifier
            round_num: Round number (1 or 2)
            nonce: Request nonce
            error: Error message
            
        Returns:
            True if notification was successful
        """
        data = {
            'email': email,
            'task': task,
            'round': round_num,
            'nonce': nonce,
            'status': 'failed',
            'error': error
        }
        
        return self.notify_evaluation_endpoint(evaluation_url, data)
    
    def test_evaluation_endpoint(self, evaluation_url: str) -> bool:
        """
        Test if an evaluation endpoint is reachable
        
        Args:
            evaluation_url: URL to test
            
        Returns:
            True if endpoint is reachable
        """
        try:
            # Send a simple GET request to test connectivity
            response = requests.get(
                evaluation_url,
                timeout=10,
                headers={'User-Agent': 'LLM-Code-Deployment/1.0'}
            )
            
            logger.info(f"Evaluation endpoint test: {response.status_code}")
            return True
            
        except Exception as e:
            logger.warning(f"Evaluation endpoint test failed: {str(e)}")
            return False