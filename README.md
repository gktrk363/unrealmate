# 🦁 UnrealMate

> **The Ultimate CLI Companion for Unreal Engine Developers.**

![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-yellow.svg)
![Downloads](https://img.shields.io/badge/downloads-1k%2B%2Fmonth-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20linux-lightgrey.svg)

**UnrealMate** is a feature-rich command-line interface (CLI) designed to streamline your Unreal Engine workflow. From optimizing projects and managing plugins to tracking team performance and deploying CI/CD pipelines, UnrealMate handles the heavy lifting so you can focus on creating.

---

## ✨ Key Features

*   **🔧 Git Automation**: Auto-configure `.gitignore` and `.gitattributes` (LFS) for UE projects.
*   **📦 Asset Organization**: Scan and auto-organize your `Content` folder. Detect duplicates.
*   **⚡ Optimization**: Analyze Blueprints, check Shader complexity, and audit memory usage.
*   **👥 Collaboration**: View team activity dashboards (CLI & Web). Share templates.
*   **🛒 Marketplace**: Search and manage assets directly from terminal.
*   **🏗️ CI/CD Ready**: Generate Dockerfiles and CI pipelines for Jenkins/GitHub/GitLab.
*   **🛡️ Secure**: Built-in project health checks (`doctor`) and security scans.
*   **🤖 AI POWERED**: NLP commands (`ai nlp`), Bug Detection (`ai detect-bugs`), and Code Review.

---

## 🚀 Installation

```bash
pip install unrealmate
```

### Requirements
*   Python 3.10 or higher
*   Git installed and in PATH
*   (Optional) Unreal Engine 5.0+ installed

---

## 📖 Documentation

Detailed documentation is available in the project root:

*   **[Kullanıcı Rehberi (Türkçe)](USER_GUIDE_TR.md)**: **Kapsamlı ve Detaylı Kullanım Kılavuzu.** (Önerilen)
*   **[User Guide (English)](USER_GUIDE.md)**: Command reference.
*   **[Deployment Guide](docs/DEPLOYMENT.md)**: For server hosting and CI/CD integration.

---

## 🎮 Quick Start

```bash
# 1. Check system health
unrealmate doctor

# 2. Initialize project config
unrealmate config init

# 3. Analyze performance
unrealmate performance profile

# 4. Launch the visual dashboard
unrealmate report dashboard
```

---

## 🤝 Contributing

We welcome contributions! Please see `docs/CONTRIBUTING.md` (if available) or submit a Pull Request.

---

## 📄 License

MIT License. See `LICENSE` for details.

**Crafted with ❤ by gktrk363**
