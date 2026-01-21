<div align="center">

# 🎮 UnrealMate

### All-in-one CLI toolkit for Unreal Engine developers
### Unreal Engine geliştiricileri için hepsi bir arada CLI araç kiti

[![Tests](https://img.shields.io/github/actions/workflow/status/gktrk363/unrealmate/tests.yml?branch=main&style=for-the-badge&logo=github&label=Tests)](https://github.com/gktrk363/unrealmate/actions/workflows/tests.yml)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Mac%20%7C%20Linux-blue?style=for-the-badge)]()
[![Unreal Engine](https://img.shields.io/badge/Unreal%20Engine-4%20%7C%205-black?style=for-the-badge&logo=unrealengine)](https://unrealengine.com)

<br>

[🇬🇧 English](#-english) • [🇹🇷 Türkçe](#-türkçe)

<br>

*Speed up your Unreal Engine workflow with powerful CLI commands*

</div>

---

# 🇬🇧 English

## 📋 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Commands](#-commands)
- [Examples](#-examples)
- [Contributing](#-contributing)

## ✨ Features

<table>
<tr>
<td width="50%">

### 🔧 Git Tools
Manage your Git workflow efficiently

- ✅ Generate optimized `.gitignore`
- ✅ Setup Git LFS automatically
- ✅ Clean temporary files (save GBs!)

</td>
<td width="50%">

### 📦 Asset Management
Keep your assets organized

- ✅ Scan & report all assets
- ✅ Auto-organize into folders
- ✅ Find duplicate files

</td>
</tr>
<tr>
<td width="50%">

### 📊 Blueprint Analysis
Understand your Blueprint complexity

- ✅ Analyze BP statistics
- ✅ Complexity scoring
- ✅ Export HTML/JSON reports

</td>
<td width="50%">

### 🩺 Project Health
Keep your project healthy

- ✅ Health score (0-100)
- ✅ Configuration checks
- ✅ Best practice validation

</td>
</tr>
</table>

## 🚀 Installation

### Prerequisites

| Requirement | Version | Required |
|-------------|---------|----------|
| Python | 3.8+ | ✅ Yes |
| Git | Any | ✅ Yes |
| Git LFS | Any | ⚠️ Optional |

### Quick Install

```bash
# Clone the repository
git clone https://github.com/gktrk363/unrealmate.git
cd unrealmate

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows: 
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install UnrealMate
pip install -e . 
```

### Verify Installation

```bash
unrealmate version
```

You should see:
```
UnrealMate v0.1.0 🚀
https://github.com/gktrk363/unrealmate
Created by:  gktrk363
```

## ⚡ Quick Start

```bash
# Navigate to your UE project
cd "C:/Projects/MyGame"

# Check project health
unrealmate doctor

# Setup Git (one-time)
unrealmate git init
unrealmate git lfs

# Clean temporary files
unrealmate git clean

# Scan assets
unrealmate asset scan

# Analyze blueprints
unrealmate blueprint analyze
```

## 📖 Commands

### 🔧 Git Commands

| Command | Description |
|---------|-------------|
| `unrealmate git init` | Generate `.gitignore` for UE projects |
| `unrealmate git lfs` | Setup Git LFS for large files |
| `unrealmate git clean` | Remove temporary/cache files |

```bash
# Examples
unrealmate git init              # Create . gitignore
unrealmate git init --force      # Overwrite existing
unrealmate git clean --dry-run   # Preview what will be deleted
unrealmate git clean --yes       # Delete without confirmation
```

### 📦 Asset Commands

| Command | Description |
|---------|-------------|
| `unrealmate asset scan` | Scan and report all assets |
| `unrealmate asset organize` | Auto-organize assets into folders |
| `unrealmate asset duplicates` | Find duplicate assets |

```bash
# Examples
unrealmate asset scan                    # Summary view
unrealmate asset scan --all              # Show all files
unrealmate asset organize --dry-run      # Preview organization
unrealmate asset duplicates --content    # Compare by content (accurate)
```

### 📊 Blueprint Commands

| Command | Description |
|---------|-------------|
| `unrealmate blueprint analyze` | Analyze Blueprint statistics |
| `unrealmate blueprint report` | Generate complexity report |

```bash
# Examples
unrealmate blueprint analyze              # Quick analysis
unrealmate blueprint analyze --all        # Show all BPs
unrealmate blueprint report               # Console report
unrealmate blueprint report -o report.html   # HTML report
unrealmate blueprint report -o report.json   # JSON report
```

### 🩺 Health Commands

| Command | Description |
|---------|-------------|
| `unrealmate doctor` | Check project health & configuration |
| `unrealmate version` | Show version info |

## 📊 Examples

### Doctor Output

```
🔍 Running UnrealMate Doctor... 

┏━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Status ┃ Check       ┃ Details                   ┃
┡━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ ✅     │ . gitignore  │ Found                     │
│ ✅     │ UE Project  │ Found:  MyGame.uproject    │
│ ✅     │ Git LFS     │ Configured                │
│ ⚠️     │ Large Files │ 5 binary files found      │
└────────┴─────────────┴───────────────────────────┘

🎉 Health Score: 90/100
```

### Asset Scan Output

```
📦 Scanning for assets... 

┏━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━┓
┃ Category    ┃ Count ┃ Size     ┃
┡━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━┩
│ Blueprints  │ 45    │ 12.5 MB  │
│ Textures    │ 128   │ 856. 2 MB │
│ Audio       │ 32    │ 125.8 MB │
│ 3D Models   │ 18    │ 234.1 MB │
├─────────────┼───────┼──────────┤
│ Total       │ 223   │ 1. 23 GB  │
└─────────────┴───────┴──────────┘
```

### Blueprint Complexity Report

```
📊 Blueprint Complexity Report

🔴 Critical (300+):   2
🟡 High (100+):       8
🟢 Medium (50+):      15
⚪ Low (<50):         45

⚠️ Blueprints That Need Attention: 

┏━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━���━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Blueprint       ┃ Nodes ┃ Recommendation                      ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ BP_GameMode     │ 456   │ Refactor immediately                │
│ BP_PlayerCtrl   │ 312   │ Refactor immediately                │
│ BP_Enemy        │ 189   │ Consider breaking into functions    │
└─────────────────┴───────┴─────────────────────────────────────┘

🎉 Blueprint Health Score: 72/100
```

## 🤝 Contributing

Contributions are welcome! Here's how: 

1. 🍴 Fork the repository
2. 🌿 Create a feature branch (`git checkout -b feature/amazing-feature`)
3. ✍️ Commit your changes (`git commit -m '✨ Add amazing feature'`)
4. 📤 Push to the branch (`git push origin feature/amazing-feature`)
5. 🔃 Open a Pull Request

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

# 🇹🇷 Türkçe

## 📋 İçindekiler

- [Özellikler](#-özellikler)
- [Kurulum](#-kurulum)
- [Hızlı Başlangıç](#-hızlı-başlangıç)
- [Komutlar](#-komutlar)
- [Örnekler](#-örnekler)
- [Katkıda Bulunma](#-katkıda-bulunma)

## ✨ Özellikler

<table>
<tr>
<td width="50%">

### 🔧 Git Araçları
Git iş akışınızı verimli yönetin

- ✅ Optimize edilmiş `.gitignore` oluştur
- ✅ Git LFS'i otomatik kur
- ✅ Geçici dosyaları temizle (GB'larca yer kazan!)

</td>
<td width="50%">

### 📦 Asset Yönetimi
Asset'lerinizi düzenli tutun

- ✅ Tüm asset'leri tara ve raporla
- ✅ Klasörlere otomatik düzenle
- ✅ Tekrarlayan dosyaları bul

</td>
</tr>
<tr>
<td width="50%">

### 📊 Blueprint Analizi
Blueprint karmaşıklığınızı anlayın

- ✅ BP istatistiklerini analiz et
- ✅ Karmaşıklık puanlaması
- ✅ HTML/JSON rapor çıkart

</td>
<td width="50%">

### 🩺 Proje Sağlığı
Projenizi sağlıklı tutun

- ✅ Sağlık puanı (0-100)
- ✅ Yapılandırma kontrolleri
- ✅ Best practice doğrulama

</td>
</tr>
</table>

## 🚀 Kurulum

### Gereksinimler

| Gereksinim | Versiyon | Zorunlu |
|------------|----------|---------|
| Python | 3.8+ | ✅ Evet |
| Git | Herhangi | ✅ Evet |
| Git LFS | Herhangi | ⚠️ Opsiyonel |

### Hızlı Kurulum

```bash
# Repoyu klonla
git clone https://github.com/gktrk363/unrealmate.git
cd unrealmate

# Sanal ortam oluştur (önerilir)
python -m venv venv

# Sanal ortamı aktifleştir
# Windows:
venv\Scripts\activate
# Mac/Linux: 
source venv/bin/activate

# UnrealMate'i kur
pip install -e . 
```

### Kurulumu Doğrula

```bash
unrealmate version
```

Şunu görmelisin:
```
UnrealMate v0.1.0 🚀
https://github.com/gktrk363/unrealmate
Created by: gktrk363
```

## ⚡ Hızlı Başlangıç

```bash
# UE projenize gidin
cd "C:/Projects/MyGame"

# Proje sağlığını kontrol et
unrealmate doctor

# Git kurulumu (bir kere)
unrealmate git init
unrealmate git lfs

# Geçici dosyaları temizle
unrealmate git clean

# Asset'leri tara
unrealmate asset scan

# Blueprint'leri analiz et
unrealmate blueprint analyze
```

## 📖 Komutlar

### 🔧 Git Komutları

| Komut | Açıklama |
|-------|----------|
| `unrealmate git init` | UE projeleri için `.gitignore` oluştur |
| `unrealmate git lfs` | Büyük dosyalar için Git LFS kur |
| `unrealmate git clean` | Geçici/önbellek dosyalarını sil |

```bash
# Örnekler
unrealmate git init              # . gitignore oluştur
unrealmate git init --force      # Mevcutun üzerine yaz
unrealmate git clean --dry-run   # Silinecekleri önizle
unrealmate git clean --yes       # Onay istemeden sil
```

### 📦 Asset Komutları

| Komut | Açıklama |
|-------|----------|
| `unrealmate asset scan` | Tüm asset'leri tara ve raporla |
| `unrealmate asset organize` | Asset'leri klasörlere otomatik düzenle |
| `unrealmate asset duplicates` | Tekrarlayan asset'leri bul |

```bash
# Örnekler
unrealmate asset scan                    # Özet görünüm
unrealmate asset scan --all              # Tüm dosyaları göster
unrealmate asset organize --dry-run      # Düzenlemeyi önizle
unrealmate asset duplicates --content    # İçeriğe göre karşılaştır (doğru)
```

### 📊 Blueprint Komutları

| Komut | Açıklama |
|-------|----------|
| `unrealmate blueprint analyze` | Blueprint istatistiklerini analiz et |
| `unrealmate blueprint report` | Karmaşıklık raporu oluştur |

```bash
# Örnekler
unrealmate blueprint analyze              # Hızlı analiz
unrealmate blueprint analyze --all        # Tüm BP'leri göster
unrealmate blueprint report               # Konsol raporu
unrealmate blueprint report -o report.html   # HTML rapor
unrealmate blueprint report -o report. json   # JSON rapor
```

### 🩺 Sağlık Komutları

| Komut | Açıklama |
|-------|----------|
| `unrealmate doctor` | Proje sağlığını ve yapılandırmasını kontrol et |
| `unrealmate version` | Versiyon bilgisini göster |

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! İşte nasıl yapılır:

1. 🍴 Repoyu fork'layın
2. 🌿 Feature branch oluşturun (`git checkout -b feature/harika-ozellik`)
3. ✍️ Değişikliklerinizi commit'leyin (`git commit -m '✨ Harika özellik ekle'`)
4. 📤 Branch'e push'layın (`git push origin feature/harika-ozellik`)
5. 🔃 Pull Request açın

## 📄 Lisans

Bu proje **MIT Lisansı** ile lisanslanmıştır - detaylar için [LICENSE](LICENSE) dosyasına bakın.

---

<div align="center">

## 👤 Author / Geliştirici

**gktrk363**

[![GitHub](https://img.shields.io/badge/GitHub-gktrk363-black?style=for-the-badge&logo=github)](https://github.com/gktrk363)

---

### ⭐ Star this repo if it helped you!  / Yardımcı olduysa yıldız ver! 

<br>

Made for Unreal Engine developers <3

Unreal Engine geliştiricileri yapıldı <3

<br>

**🎮 Happy Game Development!  / İyi Oyun Geliştirmeler!  🎮**

</div>
