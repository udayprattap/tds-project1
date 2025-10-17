# LLM Code Deployment API

🚀 **An automated system that builds, deploys, and revises web applications based on JSON task requests using AI.**

This API accepts JSON briefs with attachments, uses Large Language Models to generate project code, deploys to GitHub repositories with Pages enabled, and notifies evaluation endpoints.

## 🎯 Features

- **Build Phase**: Generate complete web projects from text briefs
- **Revise Phase**: Update existing projects with new requirements  
- **GitHub Integration**: Automatic repo creation and GitHub Pages deployment
- **LLM-Powered**: Uses OpenAI API for intelligent code generation
- **Retry Logic**: Robust evaluation endpoint notification with exponential backoff
- **Attachment Support**: Handles base64-encoded file attachments
- **Professional Output**: Generates README, LICENSE, and clean project structure

## 📁 Project Structure

```
tdssep/
├── app.py                 # Main Flask application
├── src/
│   ├── __init__.py
│   ├── api_handler.py     # Request processing logic
│   ├── config.py          # Configuration management
│   ├── llm_generator.py   # AI code generation
│   ├── github_deployer.py # GitHub integration
│   ├── evaluation_notifier.py # Endpoint notification
│   ├── readme_generator.py # README creation
│   └── utils.py           # Utility functions
├── tests/                 # Test files
├── logs/                  # Request logs
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
└── README.md             # This file
└── LICENSE               # Hold a sample Licence 

```

## 🛠️ Setup

### Prerequisites

- Python 3.8+
- Git
- GitHub CLI (`gh`) installed and authenticated
- OpenAI API access

### Installation

1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd tdssep
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

3. **Setup GitHub CLI:**
   ```bash
   gh auth login
   gh auth status
   ```

### Required Environment Variables

```env
# GitHub Integration
GITHUB_TOKEN=ghp_your_token_here
GITHUB_USERNAME=your-username

# OpenAI API
OPENAI_API_KEY=sk_your_key_here

# API Security
VALID_SECRETS=secret1,secret2,secret3
```

## 🚀 Usage

### Start the API

```bash
python app.py
```

The API will be available at `http://localhost:5000`

### API Endpoints

- `POST /api` - Submit deployment request
- `GET /health` - Health check
- `GET /` - API information

### Request Format

```json
{
  "email": "student@example.com",
  "secret": "your-valid-secret",
  "task": "task-123",
  "round": 1,
  "nonce": "unique-request-id",
  "brief": "Create a responsive todo list application with Bootstrap",
  "evaluation_url": "https://evaluator.example.com/results",
  "checks": ["Must have #add-task button", "Must display task count"],
  "attachments": [
    {
      "filename": "data.csv",
      "content": "base64-encoded-content"
    }
  ]
}
```

### Example cURL Request

```bash
curl -X POST http://localhost:5000/api \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "secret": "dev-secret-123",
    "task": "todo-app",
    "round": 1,
    "nonce": "req-001",
    "brief": "Create a todo list with add/remove functionality",
    "evaluation_url": "https://webhook.site/your-unique-url"
  }'
```

## 🔄 Workflow

### Round 1 (Build Phase)
1. Receive JSON request with brief and attachments
2. Validate secret and required fields
3. Use LLM to generate project files (HTML, CSS, JS)
4. Create new GitHub repository
5. Push generated code and enable GitHub Pages
6. Notify evaluation endpoint with deployment URLs

### Round 2 (Revise Phase)
1. Receive revision request with new requirements
2. Use LLM to modify existing project
3. Update GitHub repository with changes
4. Notify evaluation endpoint with updated URLs

## 🧪 Testing

### Run Tests
```bash
python -m pytest tests/ -v
```

### Manual Testing
```bash
# Test the health endpoint
curl http://localhost:5000/health

# Test with sample data
python tests/test_manual.py
```

### Example Test Request
```python
import requests

response = requests.post('http://localhost:5000/api', json={
    "email": "test@example.com",
    "secret": "dev-secret-123", 
    "task": "test-123",
    "round": 1,
    "nonce": "test-nonce",
    "brief": "Create a simple calculator app",
    "evaluation_url": "https://httpbin.org/post"
})

print(response.json())
```

## 📝 Generated Project Features

Each deployed project includes:

- **Responsive Design**: Bootstrap 5 integration
- **Clean Structure**: Organized HTML, CSS, and JavaScript files
- **Professional Documentation**: Auto-generated README and LICENSE
- **GitHub Pages Ready**: Immediate deployment and hosting
- **Error Handling**: Robust client-side error management
- **Accessibility**: Semantic HTML and ARIA attributes

## 🔧 Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `MAX_DEPLOYMENT_TIME` | Max deployment time (seconds) | 600 |
| `RETRY_ATTEMPTS` | Evaluation endpoint retries | 5 |
| `LLM_MODEL` | OpenAI model to use | gpt-4o-mini |
| `PAGES_BRANCH` | GitHub Pages branch | main |
| `PAGES_SOURCE` | GitHub Pages source | / |

## 🐛 Troubleshooting

### Common Issues

1. **GitHub CLI not authenticated**:
   ```bash
   gh auth login
   gh auth status
   ```

2. **OpenAI API errors**:
   - Check API key validity
   - Verify API credit/usage limits
   - Ensure base URL is correct

3. **Repository creation fails**:
   - Verify GitHub token permissions
   - Check if repository name already exists
   - Ensure GitHub username/org is correct

4. **Pages deployment issues**:
   - GitHub Pages may take a few minutes to activate
   - Check repository settings for Pages configuration
   - Verify branch and source path settings

### Logs

Check the `logs/` directory for detailed request logs and error information.

## 🔒 Security

- API secrets are validated before processing
- GitHub tokens use minimal required permissions  
- Request data is logged with sensitive fields redacted
- Input validation prevents malicious payloads
- Temporary files are cleaned up after use

## 🚀 Deployment

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

### Railway/Heroku
1. Set environment variables in platform dashboard
2. Ensure `PORT` variable is respected (already handled in app.py)
3. Install GitHub CLI in deployment environment

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## 📞 Support

For issues and questions:
- Check the troubleshooting section
- Review logs in the `logs/` directory  
- Open an issue on GitHub

---

*This project provides automated code deployment capabilities using AI for educational and development purposes.*