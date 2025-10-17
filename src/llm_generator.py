# LLM Code Generator
# Uses OpenAI API to generate project code from briefs and attachments

import os
import json
import logging
import tempfile
from typing import Dict, List, Any, Optional
from openai import OpenAI

from .config import Config
from .readme_generator import generate_readme
from .utils import create_license_file

logger = logging.getLogger(__name__)

class LLMCodeGenerator:
    """
    Generates project code using LLM based on brief and attachments
    """
    
    def __init__(self):
        self.client = OpenAI(
            api_key=Config.OPENAI_API_KEY,
            base_url=Config.OPENAI_BASE_URL
        )
        self.model = Config.LLM_MODEL
    
    # TODO (Copilot): Use OpenAI (or other) LLM to generate project code from the brief.
    # Inputs:
    # - brief (string)
    # - attachments (list of files, base64 or URLs)
    # - task ID for unique repo naming
    # Output:
    # - Generated source files: index.html, main.js, styles.css, etc.
    # Notes:
    # - For captcha or data tasks, generate minimal working frontend with Bootstrap 5
    # - If input file like data.csv or input.md is included, wire it into the generated code
    # - Ensure it displays required UI elements like #total-sales, #github-created-at, etc.
    
    def generate_project_from_brief(
        self, 
        brief: str, 
        attachments: List[str], 
        task_id: str,
        checks: List[str] = None
    ) -> Dict[str, str]:
        """
        Generate a complete project from brief and attachments
        
        Args:
            brief: Project description and requirements
            attachments: List of attachment file paths
            task_id: Unique identifier for the task
            checks: List of validation checks to ensure compliance
            
        Returns:
            Dictionary mapping filenames to file contents
        """
        try:
            logger.info(f"Generating project for task {task_id}")
            
            # Analyze attachments to understand data structure
            attachment_analysis = self._analyze_attachments(attachments)
            
            # Create the main prompt
            prompt = self._create_generation_prompt(brief, attachment_analysis, checks)
            
            # Generate project structure and code
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=4000
            )
            
            # Parse the generated code
            generated_content = response.choices[0].message.content.strip()
            project_files = self._parse_generated_files(generated_content)
            
            # Add standard files
            project_files['README.md'] = generate_readme(brief, task_id)
            project_files['LICENSE'] = create_license_file()
            
            # Add basic .gitignore
            project_files['.gitignore'] = self._create_gitignore()
            
            logger.info(f"Generated {len(project_files)} files for task {task_id}")
            return project_files
            
        except Exception as e:
            logger.error(f"Failed to generate project: {str(e)}")
            # Return minimal fallback project
            return self._create_fallback_project(brief, task_id)
    
    def revise_project_from_brief(
        self,
        brief: str,
        repo_name: str,
        attachments: List[str],
        checks: List[str] = None
    ) -> Dict[str, str]:
        """
        Revise an existing project based on new brief
        
        Args:
            brief: New requirements and modifications
            repo_name: Name of the existing repository
            attachments: List of new attachment file paths
            checks: List of validation checks
            
        Returns:
            Dictionary mapping filenames to updated file contents
        """
        try:
            logger.info(f"Revising project {repo_name}")
            
            # Analyze new attachments
            attachment_analysis = self._analyze_attachments(attachments)
            
            # Create revision prompt
            prompt = self._create_revision_prompt(brief, attachment_analysis, checks)
            
            # Generate revised code
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_revision_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=4000
            )
            
            # Parse the revised files
            generated_content = response.choices[0].message.content.strip()
            revised_files = self._parse_generated_files(generated_content)
            
            logger.info(f"Revised {len(revised_files)} files for {repo_name}")
            return revised_files
            
        except Exception as e:
            logger.error(f"Failed to revise project: {str(e)}")
            return {}
    
    def _analyze_attachments(self, attachments: List[str]) -> str:
        """Analyze attachment files and return summary"""
        if not attachments:
            return "No attachments provided."
        
        analysis = []
        for attachment_path in attachments:
            try:
                filename = os.path.basename(attachment_path)
                file_size = os.path.getsize(attachment_path)
                
                # Read file content (limit to avoid large files)
                with open(attachment_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(2000)  # First 2KB
                
                analysis.append(f"File: {filename} ({file_size} bytes)\nContent preview:\n{content}\n---")
                
            except Exception as e:
                analysis.append(f"File: {os.path.basename(attachment_path)} - Error reading: {str(e)}")
        
        return "\n".join(analysis)
    
    def _create_generation_prompt(self, brief: str, attachment_analysis: str, checks: List[str]) -> str:
        """Create the main generation prompt"""
        checks_text = ""
        if checks:
            checks_text = f"\nValidation requirements:\n" + "\n".join(f"- {check}" for check in checks)
        
        return f"""Generate a complete web project based on this brief:
{brief}
Attachments analysis:
{attachment_analysis}
{checks_text}
Requirements:
1. Create a responsive web application using HTML, CSS, and JavaScript
2. Use Bootstrap 5 for styling
3. If data files are provided, integrate them into the application
4. Ensure all required UI elements are present with correct IDs
5. Make the application functional and visually appealing
6. Include proper error handling
7. Add comments explaining key functionality
Please provide the complete code for each file, clearly separated with file headers."""
    
    def _create_revision_prompt(self, brief: str, attachment_analysis: str, checks: List[str]) -> str:
        """Create prompt for revising existing project"""
        checks_text = ""
        if checks:
            checks_text = f"\nValidation requirements:\n" + "\n".join(f"- {check}" for check in checks)
        
        return f"""Revise the existing project based on these new requirements:
{brief}
New attachments:
{attachment_analysis}
{checks_text}
Please provide only the files that need to be updated or added. Do not include unchanged files.
Maintain the existing project structure where possible."""
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for code generation"""
        return """You are an expert web developer who creates complete, functional web applications.
Generate clean, well-structured code that follows best practices:
- Use semantic HTML5
- Write clean, readable CSS
- Include proper JavaScript functionality
- Ensure accessibility
- Make responsive designs
- Add proper error handling
Always format your response with clear file separators like:
```html
<!-- index.html -->
<!DOCTYPE html>
...
```
```css
/* styles.css */
body {
...
```
```javascript
// main.js
function init() {
...
```
Create a complete, working application that fulfills all requirements."""
    
    def _get_revision_system_prompt(self) -> str:
        """Get the system prompt for code revision"""
        return """You are an expert web developer updating an existing project.
Provide only the files that need changes. Keep the existing structure and functionality where possible.
Focus on implementing the new requirements while maintaining code quality.
Format your response with clear file separators for each updated file."""
    
    def _parse_generated_files(self, content: str) -> Dict[str, str]:
        """Parse the LLM response into separate files"""
        files = {}
        
        # Split by common code block patterns
        lines = content.split('\n')
        current_file = None
        current_content = []
        in_code_block = False
        
        for line in lines:
            # Check for file headers
            if line.strip().startswith('<!--') and '.html' in line:
                # HTML file
                if current_file:
                    files[current_file] = '\n'.join(current_content).strip()
                current_file = line.strip().replace('<!--', '').replace('-->', '').strip()
                current_content = []
                in_code_block = False
                
            elif line.strip().startswith('/*') and '.css' in line:
                # CSS file
                if current_file:
                    files[current_file] = '\n'.join(current_content).strip()
                current_file = line.strip().replace('/*', '').replace('*/', '').strip()
                current_content = []
                in_code_block = False
                
            elif line.strip().startswith('//') and '.js' in line:
                # JavaScript file
                if current_file:
                    files[current_file] = '\n'.join(current_content).strip()
                current_file = line.strip().replace('//', '').strip()
                current_content = []
                in_code_block = False
                
            elif line.strip().startswith('```'):
                # Code block markers
                if 'html' in line.lower() or 'css' in line.lower() or 'javascript' in line.lower():
                    in_code_block = True
                elif line.strip() == '```':
                    in_code_block = False
                continue
                
            elif current_file and (in_code_block or not line.strip().startswith('```')):
                current_content.append(line)
        
        # Add the last file
        if current_file:
            files[current_file] = '\n'.join(current_content).strip()
        
        # If no files were parsed, create default structure
        if not files:
            files = self._create_fallback_project(content, "default")
        
        return files
    
    def _create_fallback_project(self, brief: str, task_id: str) -> Dict[str, str]:
        """Create a minimal fallback project if generation fails"""
        return {
            'index.html': f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Task {task_id}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container mt-5">
        <h1>Task {task_id}</h1>
        <p class="lead">{brief[:200]}...</p>
        <div id="content">
            <p>Project generated for: {task_id}</p>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="main.js"></script>
</body>
</html>''',
            'styles.css': '''body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.container {
    max-width: 1200px;
}
#content {
    margin-top: 2rem;
    padding: 2rem;
    border: 1px solid #dee2e6;
    border-radius: 0.375rem;
    background-color: #f8f9fa;
}''',
            'main.js': '''document.addEventListener('DOMContentLoaded', function() {
    console.log('Project loaded successfully');
    
    // Add any required functionality here
    const content = document.getElementById('content');
    if (content) {
        content.innerHTML += '<p>JavaScript is working!</p>';
    }
});'''
        }
    
    def _create_gitignore(self) -> str:
        """Create a basic .gitignore file"""
        return '''.DS_Store
.env
.env.local
.env.development.local
.env.test.local
.env.production.local
npm-debug.log*
yarn-debug.log*
yarn-error.log*
node_modules/
*.log
temp/
.vscode/
.idea/'''