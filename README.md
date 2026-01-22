<div align="center">

# 🎮 UnrealMate

### Professional CLI Toolkit for Unreal Engine Developers
### Unreal Engine geliştiricileri için profesyonel CLI araç kiti

[![PyPI](https://img.shields.io/pypi/v/unrealmate?style=for-the-badge&logo=pypi&logoColor=white)](https://pypi.org/project/unrealmate/)
[![Version](https://img.shields.io/badge/Version-1.0.0-00D9FF?style=for-the-badge&logo=semver)](https://github.com/gktrk363/unrealmate/releases)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Mac%20%7C%20Linux-blue?style=for-the-badge)](https://github.com/gktrk363/unrealmate)
[![Unreal Engine](https://img.shields.io/badge/Unreal%20Engine-4%20%7C%205-black?style=for-the-badge&logo=unrealengine)](https://unrealengine.com)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success?style=for-the-badge)](https://github.com/gktrk363/unrealmate)

<br>

**⚡ Crafted by gktrk363 ⚡**

*Speed up your Unreal Engine workflow with 30+ powerful CLI commands*

[🚀 Quick Start](#-installation) • [📖 Documentation](#-commands) • [🎯 Features](#-features) • [🇹🇷 Türkçe](#-türkçe)

</div>

---

## 🎉 What's New in v1.0.0

**Production/Stable Release** - Complete feature set with personal branding!

- ✨ **Personal Signature System** - Beautiful cyan/magenta themed interface
- ⚡ **Performance Profiler** - Analyze CPU/GPU/Memory bottlenecks
- 🔍 **Shader Analyzer** - Detect shader complexity issues
- 💾 **Memory Auditor** - Track asset memory usage
- 🔌 **Plugin Manager** - Install/manage UE plugins via CLI
- 🏗️ **CI/CD Generator** - GitHub Actions, GitLab CI, Jenkins
- ⚙️ **Configuration System** - `.unrealmate.toml` support
- 📝 **Comprehensive Logging** - Debug mode with file logging

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🔧 Git Tools
Manage your Git workflow efficiently

- ✅ Generate optimized `.gitignore`
- ✅ Setup Git LFS automatically
- ✅ Clean temporary files (save GBs!)
- ✅ Pre-commit hooks

</td>
<td width="50%">

### 📦 Asset Management
Keep your assets organized

- ✅ Scan & report all assets
- ✅ Auto-organize into folders
- ✅ Find duplicate files
- ✅ Dependency tracking

</td>
</tr>
<tr>
<td width="50%">

### 📊 Blueprint Analysis
Understand your Blueprint complexity

- ✅ Analyze BP statistics
- ✅ Complexity scoring
- ✅ Export HTML/JSON reports
- ✅ Visual graph generation

</td>
<td width="50%">

### ⚡ Performance Tools
Optimize your project

- ✅ Performance profiling
- ✅ Shader complexity analysis
- ✅ Memory auditing
- ✅ Bottleneck detection

</td>
</tr>
<tr>
<td width="50%">

### 🔌 Plugin Management
Manage plugins easily

- ✅ Install from Git/local
- ✅ Enable/disable plugins
- ✅ List installed plugins
- ✅ Remove plugins

</td>
<td width="50%">

### 🏗️ Build & CI/CD
Automate your builds

- ✅ GitHub Actions generator
- ✅ GitLab CI generator
- ✅ Jenkins pipelines
- ✅ Build optimization

</td>
</tr>
</table>

---

## 🚀 Installation

### Via pip (Recommended)

```bash
pip install unrealmate
```

### From source

```bash
git clone https://github.com/gktrk363/unrealmate.git
cd unrealmate
pip install -e .
```

### Verification

```bash
unrealmate version
```

You should see the beautiful UnrealMate banner! 🎨

---

## 📖 Commands

### Core Commands

```bash
unrealmate version          # Show version and signature banner
unrealmate doctor           # Health check with recommendations
unrealmate --help           # Show all available commands
```

### Git Commands

```bash
unrealmate git init         # Generate .gitignore for UE projects
unrealmate git lfs          # Setup Git LFS for large files
unrealmate git clean        # Clean temporary files (Saved, Intermediate, etc.)
```

### Asset Commands

```bash
unrealmate asset scan                    # Scan all assets in project
unrealmate asset scan --all              # Show detailed asset list
unrealmate asset organize                # Auto-organize assets by type
unrealmate asset organize --dry-run      # Preview organization
unrealmate asset duplicates              # Find duplicate files
unrealmate asset duplicates --content    # Compare by content (slower but accurate)
```

### Blueprint Commands

```bash
unrealmate blueprint analyze             # Analyze all blueprints
unrealmate blueprint analyze --all       # Show all blueprints
unrealmate blueprint report              # Generate complexity report
unrealmate blueprint report -o report.html  # Export to HTML
```

### Performance Commands ⚡ NEW!

```bash
unrealmate performance profile           # Analyze performance bottlenecks
unrealmate performance shaders           # Analyze shader complexity
unrealmate performance shaders --all     # Show all shaders
unrealmate performance memory            # Audit memory usage
```

### Plugin Commands 🔌 NEW!

```bash
unrealmate plugin list                   # List installed plugins
unrealmate plugin install <git-url>      # Install from Git
unrealmate plugin install <local-path>   # Install from local directory
unrealmate plugin enable <name>          # Enable a plugin
unrealmate plugin disable <name>         # Disable a plugin
unrealmate plugin remove <name>          # Remove a plugin
```

### Build Commands 🏗️ NEW!

```bash
unrealmate build ci-init --platform github   # Generate GitHub Actions
unrealmate build ci-init --platform gitlab   # Generate GitLab CI
unrealmate build ci-init --platform jenkins  # Generate Jenkinsfile
unrealmate build info                        # Show build information
```

### Config Commands ⚙️ NEW!

```bash
unrealmate config init                   # Create .unrealmate.toml
unrealmate config show                   # Show all settings
unrealmate config set <key> <value>      # Set a configuration value
unrealmate config get <key>              # Get a configuration value
```

---

## 💡 Examples

### Complete Workflow

```bash
# 1. Initialize your project
unrealmate config init
unrealmate git init
unrealmate git lfs

# 2. Check project health
unrealmate doctor

# 3. Analyze performance
unrealmate performance profile
unrealmate performance shaders
unrealmate performance memory

# 4. Manage plugins
unrealmate plugin list
unrealmate plugin install https://github.com/example/ue-plugin.git

# 5. Generate CI/CD
unrealmate build ci-init --platform github

# 6. Organize assets
unrealmate asset scan
unrealmate asset organize

# 7. Analyze blueprints
unrealmate blueprint analyze
unrealmate blueprint report -o report.html
```

### Clean Up Project

```bash
# Preview what will be deleted
unrealmate git clean --dry-run

# Clean temporary files (saves GBs!)
unrealmate git clean
```

### Find Issues

```bash
# Find duplicate assets
unrealmate asset duplicates --content

# Find complex blueprints
unrealmate blueprint analyze --all

# Find shader issues
unrealmate performance shaders
```

---

## 🎨 Personal Signature

Every command features beautiful branding by **gktrk363**:

- 🎨 Cyan (#00D9FF) and Magenta (#FF006E) color theme
- ⚡ Signature banner on version command
- 🎯 Branded panels in all commands
- ✨ Signature footer: "Powered by UnrealMate | Crafted by gktrk363"

---

## 📊 Project Statistics

- **30+ Commands** across 7 command groups
- **8 New Modules** in v1.0.0
- **2000+ Lines** of code added
- **Production/Stable** status
- **Personal Signature** throughout

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with [Typer](https://typer.tiangolo.com/) and [Rich](https://rich.readthedocs.io/)
- Inspired by the Unreal Engine developer community
- Special thanks to all contributors

---

## 📧 Contact

**Developer:** gktrk363  
**GitHub:** [@gktrk363](https://github.com/gktrk363)  
**Project:** [UnrealMate](https://github.com/gktrk363/unrealmate)

---

<div align="center">

## ⭐ Star this repository if you find it helpful!

**© 2026 gktrk363 - Crafted with passion for Unreal Engine developers**

✨ **Powered by UnrealMate** ✨

</div>

---
---

# 🇹🇷 Türkçe

## 📋 İçindekiler

- [Özellikler](#-özellikler-1)
- [Kurulum](#-kurulum-1)
- [Hızlı Başlangıç](#-hızlı-başlangıç)
- [Komutlar](#-komutlar-1)
- [Örnekler](#-örnekler-1)

## ✨ Özellikler

### 🔧 Git Araçları
- ✅ Optimize edilmiş `.gitignore` oluşturma
- ✅ Git LFS otomatik kurulum
- ✅ Geçici dosyaları temizleme (GB'larca yer kazanın!)

### 📦 Asset Yönetimi
- ✅ Tüm assetleri tarama ve raporlama
- ✅ Otomatik klasörlere organize etme
- ✅ Duplicate dosyaları bulma

### 📊 Blueprint Analizi
- ✅ Blueprint istatistikleri
- ✅ Karmaşıklık skorlama
- ✅ HTML/JSON rapor çıktısı

### ⚡ Performans Araçları (YENİ!)
- ✅ Performans profilleme
- ✅ Shader karmaşıklık analizi
- ✅ Bellek denetimi

### 🔌 Plugin Yönetimi (YENİ!)
- ✅ Git'ten plugin kurma
- ✅ Plugin aktif/pasif etme
- ✅ Plugin listesi

### 🏗️ Build & CI/CD (YENİ!)
- ✅ GitHub Actions oluşturma
- ✅ GitLab CI oluşturma
- ✅ Jenkins pipeline

## 🚀 Kurulum

```bash
pip install unrealmate
```

## 🎯 Hızlı Başlangıç

```bash
# Versiyon kontrolü
unrealmate version

# Proje sağlık kontrolü
unrealmate doctor

# Git kurulumu
unrealmate git init
unrealmate git lfs

# Asset tarama
unrealmate asset scan

# Blueprint analizi
unrealmate blueprint analyze
```

## 📖 Komutlar

Tüm komutlar için:
```bash
unrealmate --help
```

Her komut grubu için yardım:
```bash
unrealmate git --help
unrealmate asset --help
unrealmate blueprint --help
unrealmate performance --help
unrealmate plugin --help
unrealmate build --help
unrealmate config --help
```

## 💡 Örnekler

### Proje Temizleme

```bash
# Önizleme
unrealmate git clean --dry-run

# Temizle
unrealmate git clean
```

### Performans Analizi

```bash
# Performans profili
unrealmate performance profile

# Shader analizi
unrealmate performance shaders

# Bellek denetimi
unrealmate performance memory
```

### Plugin Yönetimi

```bash
# Kurulu pluginleri listele
unrealmate plugin list

# Git'ten plugin kur
unrealmate plugin install https://github.com/example/plugin.git

# Plugin aktif et
unrealmate plugin enable MyPlugin
```

---

<div align="center">

**⚡ gktrk363 tarafından Unreal Engine geliştiricileri için özenle hazırlanmıştır ⚡**

[⬆ Başa Dön](#-unrealmate)

</div>
