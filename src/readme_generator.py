# README Generator for deployed projects

from datetime import datetime
from typing import Optional

def generate_readme(brief: str, task_id: str, repo_url: Optional[str] = None) -> str:
    """
    Generate a professional README.md file for a deployed project
    
    Args:
        brief: Project brief/description
        task_id: Task identifier
        repo_url: Optional repository URL
        
    Returns:
        README.md content as string
    """
    
    # TODO (Copilot): Auto-generate a professional README.md file.
    # Should include:
    # - Project title (based on task)
    # - Short description from the brief
    # - Setup steps (if any)
    # - Deployment / GitHub Pages link
    # - Sample usage or screenshot (if available)
    # - License section (MIT)
    
    current_date = datetime.utcnow().strftime("%Y-%m-%d")
    
    # Extract a title from the brief or use task ID
    title = _extract_title_from_brief(brief, task_id)
    
    # Generate deployment section
    deployment_section = ""
    if repo_url:
        pages_url = repo_url.replace('github.com', 'github.io').replace('.git', '')
        deployment_section = f"""
## 🚀 Live Demo
This project is deployed and available at: [**{pages_url}**]({pages_url})
## 📦 Repository
Source code: [{repo_url}]({repo_url})
"""
    
    readme_content = f"""# {title}
> Task ID: `{task_id}` | Generated: {current_date}
## 📝 Description
{brief}
{deployment_section}
## 🛠️ Setup
This project is a static web application that runs in any modern web browser.
### Local Development
1. Clone the repository:
   ```bash
   git clone {repo_url or '[REPOSITORY_URL]'}
   cd {task_id}
   ```
2. Open `index.html` in your web browser or serve with a local server:
   ```bash
   # Using Python
   python -m http.server 8000
   
   # Using Node.js
   npx serve .
   
   # Using PHP
   php -S localhost:8000
   ```
3. Navigate to `http://localhost:8000` in your browser
## 🏗️ Project Structure
```
.
├── index.html          # Main HTML file
├── styles.css          # Stylesheet
├── main.js            # JavaScript functionality
├── README.md          # This file
├── LICENSE            # MIT License
└── [attachments]      # Any included data files
```
## ✨ Features
- Responsive design using Bootstrap 5
- Modern JavaScript (ES6+)
- Clean, accessible HTML
- Professional styling
- Cross-browser compatibility
## 🧪 Testing
Open the project in a web browser and verify:
- All elements display correctly
- Interactive features work as expected
- Responsive design adapts to different screen sizes
- No console errors
## 🤝 Contributing
This project was generated as part of an automated deployment system. 
If you need to make changes:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request
## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
## 🔧 Technical Details
- **Framework**: Vanilla HTML/CSS/JavaScript
- **Styling**: Bootstrap 5
- **Deployment**: GitHub Pages
- **Generated**: {current_date}
---
*This project was automatically generated and deployed using an LLM-powered deployment system.*
"""
    
    return readme_content.strip()

def _extract_title_from_brief(brief: str, task_id: str) -> str:
    """Extract a suitable title from the project brief"""
    
    # Try to find a title-like sentence in the brief
    sentences = brief.split('.')
    first_sentence = sentences[0].strip()
    
    # If the first sentence is short and descriptive, use it
    if len(first_sentence) < 100 and len(first_sentence) > 10:
        # Clean up common prefixes
        title = first_sentence
        prefixes_to_remove = [
            "create a", "build a", "develop a", "make a",
            "create an", "build an", "develop an", "make an",
            "create", "build", "develop", "make"
        ]
        
        title_lower = title.lower()
        for prefix in prefixes_to_remove:
            if title_lower.startswith(prefix + " "):
                title = title[len(prefix):].strip()
                break
        
        # Capitalize first letter
        if title:
            title = title[0].upper() + title[1:]
            return title
    
    # Fallback to a generic title
    return f"Task {task_id} - Web Application"


