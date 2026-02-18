# 📘 UnrealMate CLI v1.1.1 — User Guide

**The All-in-One CLI Toolkit for Unreal Engine Developers**

---

## 🚀 Introduction

UnrealMate is a modern command-line tool designed to accelerate workflows, optimize projects, and enhance team collaboration for Unreal Engine developers.

**Key Features:**
- **Project Setup:** Create standard-compliant project structures in 3 seconds.
- **Performance Analysis:** Detect bottlenecks, bad assets, and memory leaks with a single command.
- **Automation:** Auto-generate Git LFS, CI/CD pipelines, and Docker configurations.
- **Asset Management:** Automatically organize messy files and find duplicates.
- **Artificial Intelligence:** Run commands with natural language and perform code reviews.

---

## 📦 Installation

```bash
# Requirements: Python 3.10+, Unreal Engine 5.0+

# 1. Create a virtual environment (Recommended)
python -m venv venv
.\venv\Scripts\activate

# 2. Install UnrealMate
pip install -e .

# 3. Verify installation
unrealmate version
```

---

## 💡 Basic Commands

You can always append `--help` to any command for more information.

```bash
unrealmate --help
unrealmate git --help
unrealmate asset scan --help
```

### System Check
Before starting, check the status of your system and project:

```bash
# Project health check (Run inside .uproject directory)
unrealmate doctor

# Security scan
unrealmate security-scan

# Usage statistics
unrealmate analytics
```

---

## 🛠️ Command Groups & Detailed Usage

### 1. 🏗️ Project & Configuration (`project` & `config`)

Start and manage your projects with industry standards.

- **Start New Project:**
  ```bash
  # List standard templates
  unrealmate template list
  
  # Create a new project from "Mobile" template
  unrealmate template create MyGame --template mobile
  ```

- **Project Configuration:**
  ```bash
  # Create .unrealmate.toml
  unrealmate config init
  
  # Edit settings (GUI opens)
  unrealmate config edit
  ```

### 2. 🔧 Git & Backup (`git` & `backup`)

Tools for version control and data safety.

- **Git Setup (UE5 Optimized):**
  ```bash
  # Create .gitignore
  unrealmate git init
  
  # Setup Git LFS (Large File Storage)
  unrealmate git lfs
  ```

- **Cleanup & Backup:**
  ```bash
  # Clean unnecessary files (Intermediate, Saved, Binaries)
  unrealmate git clean
  
  # Create a smart backup of the project (Zip)
  unrealmate backup create D:\Backups
  ```

### 3. 📦 Asset Management (`asset`)

Keep your project folders organized.

- **Asset Analysis:**
  ```bash
  # Scan all assets and report
  unrealmate asset scan .
  ```

- **Auto Organization:**
  ```bash
  # Move files to appropriate folders based on type (Textures, Audio, Models etc.)
  unrealmate asset organize .
  ```

- **Duplicate Check:**
  ```bash
  # Find duplicates based on content hash
  unrealmate asset duplicates . --content
  ```

### 4. ⚡ Performance & Optimization (`performance` & `optimize`)

Boost your game's performance.

- **Performance Profile:**
  ```bash
  # General performance scan
  unrealmate performance profile .
  
  # Shader complexity analysis
  unrealmate performance shaders .
  ```

- **Auto Optimization:**
  ```bash
  # Check and optimize texture sizes (Power of Two)
  unrealmate optimize textures --fix
  ```

### 5. 🔮 Blueprint Analysis (`blueprint`)

Prevent Blueprint spaghetti.

- **Complexity Report:**
  ```bash
  # List the most complex Blueprints
  unrealmate blueprint analyze .
  
  # Generate detailed HTML report
  unrealmate blueprint report --output bp_report.html
  ```

### 6. 👥 Collaboration & Reporting (`collab` & `report`)

Enhance team communication.

- **Project Dashboard:**
  ```bash
  # Launch web-based project dashboard (localhost:8080)
  unrealmate report dashboard
  ```

- **Reporting:**
  ```bash
  # Generate HTML status report
  unrealmate report html
  
  # Send Slack/Discord notification
  unrealmate report notify "Build v1.2 is ready!"
  ```

### 7. 🤖 AI Assistant (`ai` & `automate`)

Accelerate development with AI power.

- **Natural Language Commands:**
  ```bash
  unrealmate ai nlp "scan assets and clean project"
  ```

- **Bug Detection:**
  ```bash
  # Scan code and Blueprints for bugs using AI
  unrealmate ai detect-bugs .
  ```

- **Auto Fix:**
  ```bash
  # Automatically fix common issues
  unrealmate automate fix .
  ```

### 8. 🔌 Plugin & Marketplace (`plugin` & `marketplace`)

Manage plugins and install assets from the market.

- **Plugin Management:**
  ```bash
  # List installed plugins
  unrealmate plugin list
  
  # Install plugin from Git
  unrealmate plugin install https://github.com/user/repo.git
  ```

- **Marketplace Integration:**
  ```bash
  # Search assets
  unrealmate marketplace search "Low Poly"
  
  # Install asset
  unrealmate marketplace install "Low Poly Forest"
  ```

### 9. 🏗️ Build & CI/CD (`build`)

Automate your deployment processes.

- **CI/CD Setup:**
  ```bash
  # Create GitHub Actions workflow
  unrealmate build ci-init --platform github
  ```

- **Docker:**
  ```bash
  # Generate UE5 compatible Dockerfile
  unrealmate build docker
  ```

---

## ❓ FAQ

**Q: Will UnrealMate damage my existing project?**
A: No, commands that modify files (e.g., `asset organize`, `git clean`) always ask for confirmation or offer a `--dry-run` mode. For safety, it is recommended to use `unrealmate backup create` first.

**Q: Which Unreal Engine versions are supported?**
A: UE 4.26, 4.27, 5.0, 5.1, 5.2, 5.3, and 5.4 are fully supported.

**Q: Do AI commands require internet?**
A: No, NLP and static analysis engines run entirely locally and do not send your data externally.

---

**Developer:** gktrk363  
**License:** MIT  
**Web:** [github.com/gktrk363/unrealmate](https://github.com/gktrk363/unrealmate)
