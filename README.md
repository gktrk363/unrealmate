# 🎮 UnrealMate

> All-in-one CLI toolkit for Unreal Engine developers
> 
> Unreal Engine geliştiricileri için hepsi bir arada CLI araç kiti

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub](https://img.shields.io/github/stars/gktrk363/unrealmate?style=social)](https://github.com/gktrk363/unrealmate)

🇬🇧 [English](#-features) | 🇹🇷 [Türkçe](#-özellikler)

---

## ✨ Features

**UnrealMate** is a powerful command-line tool that helps Unreal Engine developers manage their projects more efficiently. From Git configuration to asset management and Blueprint analysis - all in one place!

### 🔧 Git Tools
- **`unrealmate git init`** - Generate optimized `.gitignore` for UE projects
- **`unrealmate git lfs`** - Setup Git LFS for large binary files
- **`unrealmate git clean`** - Clean up unnecessary files (Saved, Intermediate, etc.)

### 📦 Asset Management
- **`unrealmate asset scan`** - Scan and report all assets in your project
- **`unrealmate asset organize`** - Auto-organize assets into proper folders
- **`unrealmate asset duplicates`** - Find duplicate assets wasting space

### 📊 Blueprint Analysis
- **`unrealmate blueprint analyze`** - Analyze Blueprint files and show statistics
- **`unrealmate blueprint report`** - Generate detailed complexity reports (JSON/HTML)

### 🩺 Project Health
- **`unrealmate doctor`** - Check your UE project health and configuration
- **`unrealmate version`** - Show UnrealMate version

---

## ✨ Özellikler

**UnrealMate**, Unreal Engine geliştiricilerinin projelerini daha verimli yönetmelerine yardımcı olan güçlü bir komut satırı aracıdır. Git yapılandırmasından asset yönetimine ve Blueprint analizine kadar - hepsi tek bir yerde!

### 🔧 Git Araçları
- **`unrealmate git init`** - UE projeleri için optimize edilmiş `.gitignore` oluştur
- **`unrealmate git lfs`** - Büyük dosyalar için Git LFS kurulumu yap
- **`unrealmate git clean`** - Gereksiz dosyaları temizle (Saved, Intermediate, vb.)

### 📦 Asset Yönetimi
- **`unrealmate asset scan`** - Projedeki tüm asset'leri tara ve raporla
- **`unrealmate asset organize`** - Asset'leri otomatik olarak klasörlere düzenle
- **`unrealmate asset duplicates`** - Yer kaplayan tekrarlayan asset'leri bul

### 📊 Blueprint Analizi
- **`unrealmate blueprint analyze`** - Blueprint dosyalarını analiz et ve istatistikleri göster
- **`unrealmate blueprint report`** - Detaylı karmaşıklık raporları oluştur (JSON/HTML)

### 🩺 Proje Sağlığı
- **`unrealmate doctor`** - UE proje sağlığını ve yapılandırmasını kontrol et
- **`unrealmate version`** - UnrealMate versiyonunu göster

---

## 🚀 Installation / Kurulum

### Prerequisites / Gereksinimler
- Python 3.8+
- pip
- Git
- Git LFS (opsiyonel)

### Install from source / Kaynaktan kurulum

```bash
# Clone the repository / Repoyu klonla
git clone https://github.com/gktrk363/unrealmate.git
cd unrealmate

# Create virtual environment / Sanal ortam oluştur
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install / Kur
pip install -e . 
```

---

## 📖 Usage / Kullanım

### Check Project Health / Proje Sağlığını Kontrol Et

```bash
unrealmate doctor
```

Output / Çıktı:
```
🔍 Running UnrealMate Doctor... 

┏━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Status ┃ Check       ┃ Details                             ┃
┡━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ ✅     │ . gitignore  │ Found                               │
│ ✅     │ UE Project  │ Found:  MyGame.uproject              │
│ ✅     │ Git LFS     │ Configured                          │
│ ✅     │ Large Files │ No large binary files in root       │
└────────┴─────────────┴─────────────────────────────────────┘

🎉 Health Score: 100/100
```

### Setup Git for UE Project / UE Projesi için Git Kurulumu

```bash
# Generate .gitignore / .gitignore oluştur
unrealmate git init

# Setup Git LFS / Git LFS kur
unrealmate git lfs

# Clean unnecessary files / Gereksiz dosyaları temizle
unrealmate git clean --dry-run  # Önizleme / Preview
unrealmate git clean            # Gerçek silme / Actually delete
```

### Manage Assets / Asset Yönetimi

```bash
# Scan all assets / Tüm asset'leri tara
unrealmate asset scan

# Show all assets / Tüm asset'leri göster
unrealmate asset scan --all

# Auto-organize assets / Asset'leri otomatik düzenle
unrealmate asset organize --dry-run  # Önizleme
unrealmate asset organize            # Gerçek taşıma

# Find duplicate assets / Tekrarlayan asset'leri bul
unrealmate asset duplicates
unrealmate asset duplicates --content  # İçeriğe göre karşılaştır
```

### Analyze Blueprints / Blueprint Analizi

```bash
# Analyze all blueprints / Tüm blueprint'leri analiz et
unrealmate blueprint analyze

# Show all blueprints / Tüm blueprint'leri göster
unrealmate blueprint analyze --all

# Generate complexity report / Karmaşıklık raporu oluştur
unrealmate blueprint report

# Export to HTML / HTML'e aktar
unrealmate blueprint report --output report.html

# Export to JSON / JSON'a aktar
unrealmate blueprint report --output report.json
```

---

## 🎯 Commands Reference / Komut Referansı

| Command / Komut | Description / Açıklama |
|-----------------|------------------------|
| `unrealmate version` | Versiyon göster |
| `unrealmate doctor` | Proje sağlığını kontrol et |
| `unrealmate git init` | .gitignore oluştur |
| `unrealmate git lfs` | Git LFS kur |
| `unrealmate git clean` | Geçici dosyaları temizle |
| `unrealmate asset scan` | Asset'leri tara |
| `unrealmate asset organize` | Asset'leri düzenle |
| `unrealmate asset duplicates` | Tekrarları bul |
| `unrealmate blueprint analyze` | Blueprint analiz et |
| `unrealmate blueprint report` | Karmaşıklık raporu |

### Common Options / Genel Seçenekler

| Option / Seçenek | Description / Açıklama |
|------------------|------------------------|
| `--help` | Yardım göster |
| `--dry-run, -d` | Değişiklik yapmadan önizle |
| `--yes, -y` | Onay istemeden devam et |
| `--force, -f` | Mevcut dosyaların üzerine yaz |
| `--all, -a` | Tüm öğeleri göster |
| `--output, -o` | Çıktıyı dosyaya kaydet |

---

## 📁 Project Structure / Proje Yapısı

```
unrealmate/
├── unrealmate/
│   ├── __init__.py
│   ├── cli.py              # Ana CLI uygulaması
│   └── templates/
│       ├── gitignore.template
│       └── gitattributes. template
├── tests/
├── pyproject.toml
├── setup.py
└── README.md
```

---

## 🤝 Contributing / Katkıda Bulunma

Katkılarınızı bekliyoruz! / Contributions are welcome! 

1. Fork'layın / Fork the repository
2. Feature branch oluşturun / Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit'leyin / Commit your changes (`git commit -m '✨ Add amazing feature'`)
4. Push'layın / Push to the branch (`git push origin feature/amazing-feature`)
5. Pull Request açın / Open a Pull Request

---

## 📝 License / Lisans

Bu proje MIT Lisansı ile lisanslanmıştır.  / This project is licensed under the MIT License. 

---

## 👤 Author / Geliştirici

**gktrk363**

- GitHub:  [@gktrk363](https://github.com/gktrk363)

---

## ⭐ Destek / Support

Eğer bu proje işinize yaradıysa yıldız vermeyi unutmayın! ⭐

Give a ⭐ if this project helped you! 

---

<p align="center">
  Made with ❤️ for Unreal Engine developers
  <br>
  Unreal Engine geliştiricileri için ❤️ ile yapıldı
</p>
