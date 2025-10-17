FROM python:3.10-slim
WORKDIR /code

# Install system dependencies and GitHub CLI
RUN apt-get update && apt-get install -y curl sudo \
    && curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | \
    sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
    | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && apt-get update \
    && apt-get install -y gh

# Copy and install requirements
COPY requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Clean up any stale cache files
RUN find /code -type d -name _pycache_ -exec rm -r {} \; || true
RUN find /code -name "*.pyc" -delete || true

# Copy application code last (to optimize cache usage)
COPY . /code

EXPOSE 7860
ENV FLASK_APP=app.py

CMD ["flask", "run", "--host=0.0.0.0", "--port=7860"]