# API Handler for processing deployment requests

import logging
import json
import base64
import os
import tempfile
from datetime import datetime
from typing import Dict, List, Any

from .llm_generator import LLMCodeGenerator
from .github_deployer import GitHubDeployer
from .evaluation_notifier import EvaluationNotifier
from .utils import save_request_log, decode_attachments
from .config import Config

logger = logging.getLogger(__name__)

def process_deployment_request(request_data: Dict[str, Any]):
    """
    Process a deployment request (build or revise round)
    Runs in background thread to avoid API timeout
    """
    try:
        # Extract request data
        email = request_data['email']
        task_id = request_data['task']
        round_num = request_data['round']
        nonce = request_data['nonce']
        brief = request_data['brief']
        evaluation_url = request_data['evaluation_url']
        attachments = request_data.get('attachments', [])
        checks = request_data.get('checks', [])
        
        logger.info(f"Processing round {round_num} for {email}, task {task_id}")
        
        # Save request log
        log_file = save_request_log(request_data)
        logger.info(f"Request logged to {log_file}")
        
        # Generate repository name
        repo_name = Config.get_repo_name(task_id, email)
        
        # Initialize components
        llm_generator = LLMCodeGenerator()
        github_deployer = GitHubDeployer()
        evaluator = EvaluationNotifier()
        
        # Decode and save attachments
        attachment_files = []
        if attachments:
            attachment_files = decode_attachments(attachments, task_id)
            logger.info(f"Decoded {len(attachment_files)} attachments")
        
        if round_num == 1:
            # Build Phase: Generate new project
            logger.info(f"Generating new project for task {task_id}")
            
            project_files = llm_generator.generate_project_from_brief(
                brief=brief,
                attachments=attachment_files,
                task_id=task_id,
                checks=checks
            )
            
            # Create new repository
            repo_url, commit_sha, pages_url = github_deployer.create_and_deploy_repo(
                repo_name=repo_name,
                project_files=project_files,
                attachment_files=attachment_files,
                brief=brief
            )
            
        else:
            # Revise Phase: Update existing project
            logger.info(f"Revising existing project for task {task_id}")
            
            # Generate revised code
            revised_files = llm_generator.revise_project_from_brief(
                brief=brief,
                repo_name=repo_name,
                attachments=attachment_files,
                checks=checks
            )
            
            # Update existing repository
            repo_url, commit_sha, pages_url = github_deployer.update_existing_repo(
                repo_name=repo_name,
                revised_files=revised_files,
                attachment_files=attachment_files,
                brief=brief
            )
        
        logger.info(f"Deployment successful - Repo: {repo_url}, Pages: {pages_url}")
        
        # Notify evaluation endpoint
        evaluation_data = {
            'email': email,
            'task': task_id,
            'round': round_num,
            'nonce': nonce,
            'repo_url': repo_url,
            'commit_sha': commit_sha,
            'pages_url': pages_url
        }
        
        success = evaluator.notify_evaluation_endpoint(evaluation_url, evaluation_data)
        
        if success:
            logger.info(f"Successfully notified evaluation endpoint for {email}")
        else:
            logger.error(f"Failed to notify evaluation endpoint for {email}")
        
        # Clean up temporary files
        for attachment_file in attachment_files:
            try:
                if os.path.exists(attachment_file):
                    os.remove(attachment_file)
            except Exception as e:
                logger.warning(f"Failed to clean up {attachment_file}: {e}")
        
    except Exception as e:
        logger.error(f"Deployment failed for {request_data.get('email', 'unknown')}: {str(e)}")
        
        # Still try to notify evaluation endpoint about the failure
        try:
            evaluator = EvaluationNotifier()
            evaluation_data = {
                'email': request_data.get('email', ''),
                'task': request_data.get('task', ''),
                'round': request_data.get('round', 0),
                'nonce': request_data.get('nonce', ''),
                'error': str(e),
                'status': 'failed'
            }
            evaluator.notify_evaluation_endpoint(
                request_data.get('evaluation_url', ''),
                evaluation_data
            )
        except Exception as notify_error:
            logger.error(f"Failed to notify evaluation endpoint about error: {notify_error}")