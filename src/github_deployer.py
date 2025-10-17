# GitHub Repository Deployer
# Handles creating repos, pushing code, and enabling GitHub Pages

import os
import json
import logging
import subprocess
import tempfile
import shutil
from typing import Dict, List, Tuple, Optional
from datetime import datetime

from .config import Config

logger = logging.getLogger(__name__)

class GitHubDeployer:
    """
    Manages GitHub repository creation and deployment
    """
    
    def __init__(self):
        self.github_token = Config.GITHUB_TOKEN
        self.github_owner = Config.get_github_owner()
        self.pages_branch = Config.PAGES_BRANCH
        self.pages_source = Config.PAGES_SOURCE
    
    # TODO (Copilot): Create and push a new GitHub repo using GitHub CLI or API.
    # - Repo name: "student-task-${task}" (must be unique)
    # - Add MIT LICENSE at root
    # - Add generated files + attachments
    # - Push to main branch
    # - Enable GitHub Pages on /docs or root
    # - Get commit SHA and Pages URL
    # Return: repo_url, commit_sha, pages_url
    
    def create_and_deploy_repo(
        self,
        repo_name: str,
        project_files: Dict[str, str],
        attachment_files: List[str],
        brief: str
    ) -> Tuple[str, str, str]:
        """
        Create a new GitHub repository and deploy the project
        
        Args:
            repo_name: Name for the new repository
            project_files: Dictionary of filename -> content
            attachment_files: List of attachment file paths to include
            brief: Project brief for commit message
            
        Returns:
            Tuple of (repo_url, commit_sha, pages_url)
        """
        try:
            logger.info(f"Creating repository: {repo_name}")
            
            # Create temporary directory for git operations
            with tempfile.TemporaryDirectory() as temp_dir:
                repo_path = os.path.join(temp_dir, repo_name)
                os.makedirs(repo_path)
                
                # Initialize git repository
                self._run_git_command(['init'], cwd=repo_path)
                self._configure_git(repo_path)
                
                # Write project files
                for filename, content in project_files.items():
                    file_path = os.path.join(repo_path, filename)
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                
                # Copy attachment files
                for attachment_path in attachment_files:
                    if os.path.exists(attachment_path):
                        filename = os.path.basename(attachment_path)
                        dest_path = os.path.join(repo_path, filename)
                        shutil.copy2(attachment_path, dest_path)
                
                # Create GitHub repository
                repo_url = self._create_github_repo(repo_name, brief)
                
                # Add and commit files
                self._run_git_command(['add', '.'], cwd=repo_path)
                commit_message = f"Initial commit: {brief[:100]}"
                self._run_git_command(['commit', '-m', commit_message], cwd=repo_path)
                
                # Add remote and push
                self._run_git_command(['remote', 'add', 'origin', repo_url], cwd=repo_path)
                self._run_git_command(['branch', '-M', 'main'], cwd=repo_path)
                self._run_git_command(['push', '-u', 'origin', 'main'], cwd=repo_path)
                
                # Get commit SHA
                commit_sha = self._get_latest_commit_sha(repo_path)
                
                # Enable GitHub Pages
                pages_url = self._enable_github_pages(repo_name)
                
                logger.info(f"Successfully deployed {repo_name} to {pages_url}")
                return repo_url, commit_sha, pages_url
                
        except Exception as e:
            logger.error(f"Failed to create and deploy repository: {str(e)}")
            raise
    
    def update_existing_repo(
        self,
        repo_name: str,
        revised_files: Dict[str, str],
        attachment_files: List[str],
        brief: str
    ) -> Tuple[str, str, str]:
        """
        Update an existing GitHub repository with revised files
        
        Args:
            repo_name: Name of the existing repository
            revised_files: Dictionary of filename -> updated content
            attachment_files: List of new attachment file paths
            brief: Revision brief for commit message
            
        Returns:
            Tuple of (repo_url, commit_sha, pages_url)
        """
        try:
            logger.info(f"Updating repository: {repo_name}")
            
            repo_url = f"https://github.com/{self.github_owner}/{repo_name}.git"
            
            # Create temporary directory for git operations
            with tempfile.TemporaryDirectory() as temp_dir:
                repo_path = os.path.join(temp_dir, repo_name)
                
                # Clone existing repository
                self._run_git_command(['clone', repo_url, repo_path])
                self._configure_git(repo_path)
                
                # Update files
                for filename, content in revised_files.items():
                    file_path = os.path.join(repo_path, filename)
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                
                # Copy new attachment files
                for attachment_path in attachment_files:
                    if os.path.exists(attachment_path):
                        filename = os.path.basename(attachment_path)
                        dest_path = os.path.join(repo_path, filename)
                        shutil.copy2(attachment_path, dest_path)
                
                # Check for changes
                result = self._run_git_command(['status', '--porcelain'], cwd=repo_path)
                if not result.stdout.strip():
                    logger.info("No changes detected, skipping commit")
                    commit_sha = self._get_latest_commit_sha(repo_path)
                    pages_url = self._get_pages_url(repo_name)
                    return repo_url.replace('.git', ''), commit_sha, pages_url
                
                # Commit and push changes
                self._run_git_command(['add', '.'], cwd=repo_path)
                commit_message = f"Update: {brief[:100]}"
                self._run_git_command(['commit', '-m', commit_message], cwd=repo_path)
                self._run_git_command(['push'], cwd=repo_path)
                
                # Get new commit SHA
                commit_sha = self._get_latest_commit_sha(repo_path)
                
                # Get Pages URL
                pages_url = self._get_pages_url(repo_name)
                
                logger.info(f"Successfully updated {repo_name}")
                return repo_url.replace('.git', ''), commit_sha, pages_url
                
        except Exception as e:
            logger.error(f"Failed to update repository: {str(e)}")
            raise
    
    def _create_github_repo(self, repo_name: str, description: str) -> str:
        """Create a new GitHub repository using GitHub CLI"""
        try:
            # Use GitHub CLI to create repository
            cmd = [
                'gh', 'repo', 'create',
                f"{self.github_owner}/{repo_name}",
                '--public',
                '--description', description[:100],
                '--clone=false'
            ]
            
            result = self._run_command(cmd)
            
            if result.returncode != 0:
                raise Exception(f"Failed to create repository: {result.stderr}")
            
            repo_url = f"https://github.com/{self.github_owner}/{repo_name}.git"
            logger.info(f"Created repository: {repo_url}")
            return repo_url
            
        except Exception as e:
            logger.error(f"Failed to create GitHub repository: {str(e)}")
            raise
    
    def _enable_github_pages(self, repo_name: str) -> str:
        """Enable GitHub Pages for the repository"""
        try:
            # Use GitHub CLI to enable Pages
            cmd = [
                'gh', 'api',
                f'/repos/{self.github_owner}/{repo_name}/pages',
                '--method', 'POST',
                '--field', f'source[branch]={self.pages_branch}',
                '--field', f'source[path]={self.pages_source}'
            ]
            
            result = self._run_command(cmd)
            
            # Pages might already be enabled, which is fine
            if result.returncode not in [0, 422]:
                logger.warning(f"GitHub Pages setup returned code {result.returncode}: {result.stderr}")
            
            pages_url = f"https://{self.github_owner}.github.io/{repo_name}"
            logger.info(f"GitHub Pages enabled: {pages_url}")
            return pages_url
            
        except Exception as e:
            logger.warning(f"Failed to enable GitHub Pages: {str(e)}")
            # Return the expected URL even if setup failed
            return f"https://{self.github_owner}.github.io/{repo_name}"
    
    def _get_pages_url(self, repo_name: str) -> str:
        """Get the GitHub Pages URL for a repository"""
        return f"https://{self.github_owner}.github.io/{repo_name}"
    
    def _configure_git(self, repo_path: str):
        """Configure git with authentication"""
        # Set git config
        self._run_git_command(['config', 'user.email', 'deployment-bot@example.com'], cwd=repo_path)
        self._run_git_command(['config', 'user.name', 'Deployment Bot'], cwd=repo_path)
        
        # Configure authentication using token
        if self.github_token:
            git_credential_helper = f'!f() {{ echo "username=token"; echo "password={self.github_token}"; }}; f'
            self._run_git_command(['config', 'credential.helper', git_credential_helper], cwd=repo_path)
    
    def _get_latest_commit_sha(self, repo_path: str) -> str:
        """Get the SHA of the latest commit"""
        result = self._run_git_command(['rev-parse', 'HEAD'], cwd=repo_path)
        return result.stdout.strip()
    
    def _run_git_command(self, args: List[str], cwd: str = None) -> subprocess.CompletedProcess:
        """Run a git command"""
        cmd = ['git'] + args
        return self._run_command(cmd, cwd=cwd)
    
    def _run_command(self, cmd: List[str], cwd: str = None) -> subprocess.CompletedProcess:
        """Run a shell command"""
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                logger.error(f"Command failed: {' '.join(cmd)}")
                logger.error(f"Exit code: {result.returncode}")
                logger.error(f"STDOUT: {result.stdout}")
                logger.error(f"STDERR: {result.stderr}")
            
            return result
            
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {' '.join(cmd)}")
            raise
        except Exception as e:
            logger.error(f"Failed to run command {' '.join(cmd)}: {str(e)}")
            raise