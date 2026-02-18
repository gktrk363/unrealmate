# 📘 UnrealMate CLI v1.1.3 — Kullanım Kılavuzu

**Unreal Engine Geliştiricileri İçin Hepsi-Bir-Arada CLI Araç Takımı**

---

## 🚀 Giriş

UnrealMate, Unreal Engine geliştiricilerinin iş akışlarını hızlandırmak, projelerini optimize etmek ve ekip işbirliğini güçlendirmek için tasarlanmış modern bir komut satırı aracıdır.

**Öne Çıkan Özellikler:**
- **Proje Kurulumu:** 3 saniyede standartlara uygun proje yapısı oluşturma
- **Performans Analizi:** Tek komutla darboğazları, hatalı assetleri ve bellek kaçaklarını tespit etme
- **Otomasyon:** Git LFS, CI/CD pipeline ve Docker yapılandırmalarını otomatik oluşturma
- **Asset Yönetimi:** Dağınık dosyaları otomatik organize etme ve kopya dosyaları bulma
- **Yapay Zeka:** Doğal dil ile komut çalıştırma ve kod inceleme

---

## 📦 Kurulum

```bash
# Gereksinimler: Python 3.10+, Unreal Engine 5.0+

# 1. Sanal ortam oluşturun (Önerilen)
python -m venv venv
.\venv\Scripts\activate

# 2. UnrealMate'i yükleyin
pip install -e .

# 3. Kurulumu doğrulayın
unrealmate version
```

---

## 💡 Temel Komutlar

Her zaman yardım almak için herhangi bir komutun sonuna `--help` ekleyebilirsiniz.

```bash
unrealmate --help
unrealmate git --help
unrealmate asset scan --help
```

### Sistem Kontrolü
Projeye başlamadan önce sisteminizin ve projenizin durumunu kontrol edin:

```bash
# Proje sağlık kontrolü ( .uproject dizininde çalıştırın)
unrealmate doctor

# Güvenlik taraması
unrealmate security-scan

# Kullanım istatistikleri
unrealmate analytics
```

---

## 🛠️ Komut Grupları ve Detaylı Kullanım

### 1. 🏗️ Proje ve Yapılandırma (`project` & `config`)

Projenizi standartlara uygun başlatın ve yönetin.

- **Yeni Proje Başlatma:**
  ```bash
  # Standart şablonları listele
  unrealmate template list
  
  # "Mobile" şablonundan yeni proje oluştur
  unrealmate template create MyGame --template mobile
  ```

- **Proje Yapılandırması:**
  ```bash
  # .unrealmate.toml oluştur
  unrealmate config init
  
  # Ayarları düzenle (GUI açılır)
  unrealmate config edit
  ```

### 2. 🔧 Git ve Yedekleme (`git` & `backup`)

Versiyon kontrolü ve veri güvenliği için araçlar.

- **Git Kurulumu (UE5 Optimize):**
  ```bash
  # .gitignore oluştur
  unrealmate git init
  
  # Git LFS (Large File Storage) kur
  unrealmate git lfs
  ```

- **Temizlik ve Yedekleme:**
  ```bash
  # Gereksiz dosyaları (Intermediate, Saved, Binaries) temizle
  unrealmate git clean
  
  # Projenin akıllı yedeğini al (Zip)
  unrealmate backup create D:\Yedekler
  ```

### 3. 📦 Asset Yönetimi (`asset`)

Proje dosyalarınızı düzenli tutun.

- **Asset Analizi:**
  ```bash
  # Tüm assetleri tara ve raporla
  unrealmate asset scan .
  ```

- **Otomatik Düzenleme:**
  ```bash
  # Dosyaları türlerine göre klasörlere taşı (Textures, Audio, Models vb.)
  unrealmate asset organize .
  ```

- **Kopya Dosya Kontrolü:**
  ```bash
  # İçerik hash'ine göre kopya dosyaları bul
  unrealmate asset duplicates . --content
  ```

### 4. ⚡ Performans ve Optimizasyon (`performance` & `optimize`)

Oyununuzun performansını artırın.

- **Performans Profili:**
  ```bash
  # Genel performans taraması
  unrealmate performance profile .
  
  # Shader karmaşıklığı analizi
  unrealmate performance shaders .
  ```

- **Otomatik Optimizasyon:**
  ```bash
  # Texture boyutlarını kontrol et ve optimize et (Power of Two)
  unrealmate optimize textures --fix
  ```

### 5. 🔮 Blueprint Analizi (`blueprint`)

Blueprint spagettisini önleyin.

- **Karmaşıklık Raporu:**
  ```bash
  # En karmaşık Blueprint'leri listele
  unrealmate blueprint analyze .
  
  # Detaylı HTML raporu oluştur
  unrealmate blueprint report --output bp_report.html
  ```

### 6. 👥 İşbirliği ve Raporlama (`collab` & `report`)

Ekip içi iletişimi ve proje takibini kolaylaştırır.

- **Proje Panosu:**
  ```bash
  # Web tabanlı proje panosunu başlat (localhost:8080)
  unrealmate report dashboard
  ```

- **Raporlama:**
  ```bash
  # HTML durum raporu oluştur
  unrealmate report html
  
  # Slack/Discord bildirimi gönder
  unrealmate report notify "Build v1.2 hazır!"
  ```

### 7. 🤖 Yapay Zeka Asistanı (`ai` & `automate`)

AI gücüyle geliştirme sürecini hızlandırın.

- **Doğal Dil Komutları:**
  ```bash
  unrealmate ai nlp "scan assets and clean project"
  ```

- **Hata Tespiti:**
  ```bash
  # Kod ve Blueprint hatalarını AI ile tara
  unrealmate ai detect-bugs .
  ```

- **Otomatik Düzeltme:**
  ```bash
  # Yaygın sorunları otomatik düzelt
  unrealmate automate fix .
  ```

### 8. 🔌 Plugin ve Marketplace (`plugin` & `marketplace`)

Eklentileri yönetin ve marketten asset kurun.

- **Plugin Yönetimi:**
  ```bash
  # Yüklü pluginleri listele
  unrealmate plugin list
  
  # Git'ten plugin yükle
  unrealmate plugin install https://github.com/user/repo.git
  ```

- **Marketplace Entegrasyonu:**
  ```bash
  # Asset ara
  unrealmate marketplace search "Low Poly"
  
  # Asset yükle
  unrealmate marketplace install "Low Poly Forest"
  ```

### 9. 🏗️ Build ve CI/CD (`build`)

Dağıtım süreçlerini otomatikleştirin.

- **CI/CD Kurulumu:**
  ```bash
  # GitHub Actions workflow oluştur
  unrealmate build ci-init --platform github
  ```

- **Docker:**
  ```bash
  # UE5 uyumlu Dockerfile oluştur
  unrealmate build docker
  ```

---

## ❓ Sıkça Sorulan Sorular

**S: UnrealMate mevcut projeme zarar verir mi?**
C: Hayır, düzenleme yapan komutlar (örn. `asset organize`, `git clean`) her zaman önce onay ister veya `--dry-run` modu sunar. Güvenliğiniz için önce `unrealmate backup create` kullanmanız önerilir.

**S: Hangi Unreal Engine sürümleri destekleniyor?**
C: UE 4.26, 4.27, 5.0, 5.1, 5.2, 5.3 ve 5.4 tam desteklenmektedir.

**S: AI komutları internet gerektirir mi?**
C: Hayır, NLP ve statik analiz motorları tamamen yerel çalışır ve verilerinizi dışarı göndermez.

---

**Geliştirici:** gktrk363  
**Lisans:** MIT  
**Web:** [github.com/gktrk363/unrealmate](https://github.com/gktrk363/unrealmate)
