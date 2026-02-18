# UnrealMate Deployment & CI/CD Guide

This guide explains how to deploy the **UnrealMate Dashboard** to a server and how to integrate **UnrealMate CLI** into your CI/CD pipelines (Jenkins, GitLab CI, GitHub Actions).

---

## 🌐 Deploying the Web Dashboard (VPS)

You can host the collaboration dashboard on a VPS (Virtual Private Server) so your whole team can access it.

### Prerequisites
*   A Linux VPS (Ubuntu 22.04 recommended)
*   Python 3.10+
*   Git

### 1. Installation on Server
SSH into your server and install UnrealMate:

```bash
# Clone your project repo
git clone https://github.com/your-org/your-project.git
cd your-project

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install tools
pip install unrealmate flask gunicorn
```

### 2. Running with Gunicorn (Production)
Do not use the development server (`unrealmate report dashboard`) for production. Use Gunicorn:

```bash
# Start Gunicorn on port 8000
gunicorn -w 4 -b 0.0.0.0:8000 "unrealmate.cli:create_dashboard_app('.')"
```

*(Note: You might need to create a small `wsgi.py` entry point if direct CLI invocation is tricky. See below.)*

**wsgi.py**:
```python
from unrealmate.core.team_dashboard import TeamDashboard
dashboard = TeamDashboard(".")
app = dashboard._create_app()

if __name__ == "__main__":
    app.run()
```

Run with: `gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app`

### 3. Nginx Reverse Proxy (Optional but Recommended)
Set up Nginx to forward port 80 to 8000 for better security and SSL support.

---

## 🤖 CI/CD Integration

UnrealMate is designed to run in automated pipelines.

### GitHub Actions Example
Add this to `.github/workflows/unrealmate.yml`:

```yaml
name: UnrealMate Checks

on: [push, pull_request]

jobs:
  check:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Install UnrealMate
        run: pip install unrealmate
        
      - name: Healthy Check
        run: unrealmate doctor --ci-mode
        
      - name: Check for Duplicate Assets
        run: unrealmate asset duplicates .
```

### GitLab CI Example
Add to `.gitlab-ci.yml`:

```yaml
stages:
  - analyze

unrealmate_scan:
  stage: analyze
  script:
    - pip install unrealmate
    - unrealmate blueprint analyze .
    - unrealmate performance profile .
  artifacts:
    paths:
      - performance_report.html
```

---

## 🐳 Docker Deployment

You can containerize the dashboard.

**Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt unrealmate flask gunicorn

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "wsgi:app"]
```

Build and run:
```bash
docker build -t unrealmate-dash .
docker run -p 8080:8080 unrealmate-dash
```

---

© 2026 gktrk363 - UnrealMate
