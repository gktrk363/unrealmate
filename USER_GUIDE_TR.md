# 📘 UnrealMate CLI v1.1.4 — Kullanım Kılavuzu

**Unreal Engine Geliştiricileri İçin CLI Odaklı İş Akışı Araç Takımı**

---

## 🚀 Giriş

UnrealMate, yerel Unreal Engine projelerini denetlemek, analiz etmek ve yönetmek için tasarlanmış modern bir komut satırı aracıdır.

**Mevcut Ürün Odağı:**
- **Stabil Temel Özellikler:** Ürünün asıl gücü, kararlı ve test edilmiş CLI komut yüzeyinde yatar.
- **Yerel-Öncelikli:** Projenin durumu, ayarları, eklentileri (plugins) ve git konfigürasyonlarını yerel diskinizde yönetmek için tasarlanmıştır.
- **Dışa Aktarma:** Proje durumunuzla ilgili anlık analizleri ve profilleri dışa aktarmanızı sağlar.
- **Güvenlik İkazları:** Dosyalarınızı doğrudan değiştiren komutlar (`git clean`, `plugin install`, `asset organize` vb.) çalışmadan önce mutasyonla ilgili uyarı niteliği taşır.

---

## 📦 Kurulum

```bash
# Gereksinimler: Python 3.10+, Git'in yüklü ve PATH'de olması
# (Tam verim alabilmek için Unreal Engine 5.0+ kurulu olması tavsiye edilir)

# 1. Sanal ortam oluşturun (Önerilen)
python -m venv venv
.\venv\Scripts\activate

# 2. UnrealMate'i yükleyin
pip install unrealmate

# 3. Kurulumu doğrulayın
python -m unrealmate version
```

---

## 🎮 İlk Kullanım ve Temel Kavramlar

Çoğu kullanıcı sistem üzerinde değişiklik yapan komutlardan ziyade projeyi analiz eden komutlarla başlamalıdır. Bütün komutları Unreal projenizin bulunduğu kök klasörde (root) çalıştırın:

```bash
# Kararlı yüzey (stable surface) için genel yardım menüsü
python -m unrealmate --help

# 1. Yerel projeyi denetle (Tavsiye niteliğinde analiz)
python -m unrealmate doctor

# 2. Yerel konfigürasyonları güvenli şekilde oku
python -m unrealmate config show

# 3. Projedeki asset dosyalarını içeriğini değiştirmeden tara
python -m unrealmate asset scan Content

# 4. Yerel proje metadatalarını gözden geçir
python -m unrealmate build info .
```

*Not: Varsayılan menüde gizli tutulan deneysel (experimental) ve ikincil araçları görmek için `python -m unrealmate --help-all` kullanabilirsiniz.*

---

## 🛠️ Kararlı (Stable) Komut Grupları

### 1. İnceleme ve Doğrulama
Proje dosyalarınızda değişiklik yapmayan, güvenli inceleme araçları.

- **`doctor`**: Proje sağlığına ve temel eksiğine dair tavsiye analizini çalıştırır.
- **`config show / validate`**: `.unrealmate.toml` ayar dosyanızı hatalara karşı okur.
- **`asset scan / duplicates`**: İçerik klasörlerinde temel istatistikleri çıkarır ve olası kopya (duplicate) dosyaları bulur.
- **`build info`**: `.uproject` dosyası hakkında temel bilgileri verir.
- **`plugin list`**: Projede tanımlı olan tüm kurulu eklentileri listeler.

### 2. Yerel Durumu Değiştirme
Risk barındıran mutasyon akışları. Bu komutlar diske yazma işlemi gerçekleştirir ya da konfigürasyon dosyalarınızı doğrudan editler.

- **`config init / set / edit / template`**: `.unrealmate.toml` ayarlarını yapılandırmak için kullanılır.
- **`git init / lfs / clean`**: UE için optimize edilmiş git repo kurulumunu ve atık build (Intermediate vs.) dosyası temizliğini gerçekleştirir.
- **`asset organize`**: Asset'leri dosya türlerine göre (Materyal, Doku vs.) ideal klasör yapılarına otomatik aktarır.
- **`plugin install / enable / disable / remove`**: `Plugins/` klasörüne dosya kopyalayarak veya doğrudan `.uproject` dosyasını manipüle ederek eklentileri ayarlar.

### 3. Analiz ve Dışa Aktarma
Cihazınızdaki statükoyu temel alan tahmin ve analiz snapshot'ları (anlık çıktılar).

- **`performance profile / memory / shaders`**: Heuristik performans analizi sağlar. (Canlı oyun motoru telemetrisi değildir, diskteki dosyalar üzerinden tahmin yapar).
- **`report json / html`**: O anki proje durumunuzu anlatan detaylı bir html veya json rapor dosyasını doğrudan oluşturup diske kaydeder.

---

## 🧪 İkincil ve Deneysel Özellikler

UnrealMate aynı zamanda **"deneysel, prototip ya da sadece yerelde çalışan kısımlı"** birtakım yüzeyler içerir. Bunlar aktif olarak kullanılabilir ancak ana üründen ziyade yan özellik olarak kabul edilmelidir:

- **`report dashboard`**: İkincil, CLI üzerinden başlatılan bir web rapor tablosudur. Tarayıcıda açılır, hala deneysel durumdadır ve yerel portları kullanır.
- **`report notify`**: Uzak web sunucularına / Discord / Slack gibi yerlere veri YOLLAMAZ. Sadece makine içerisine lokal bildirim logu yazar.
- **`build ci-init / docker`**: Başlangıç seviyesi basit dosya şablonları üretir, kapsamlı/tam otonom CI/CD otomasyonları (üretim ortamı) sağlamaz.
- **AI Komutları (`ai detect-bugs`, `ai nlp`)**: Desen eşleştirme sistemli deneysel özelliklerdir. Basit senaryolara yanıt verse dahi jenerik/tahmini sonuçlar doğurabilir.

---

## ❓ Sıkça Sorulan Sorular

**S: UnrealMate mevcut projeme zarar verir mi?**
C: İnceleme ("Inspect") ve raporlama ("Export") komutları sadece veriyi okur. Ancak "Durum Değiştirme" (Örn: `asset organize` veya `git clean`) kapsamındaki komutlar projenize mutasyon işlemi uygulayacağından, terminal üzerindeki uyarıları dikkatli okumanız ve olası geri almalar (rollback) için Git history kullanmanız beklenir.

**S: UnrealMate otomatik olarak sunuculara veri gönderir mi?**
C: Hayır. `report notify` veya analitik işlemleri ile alakalı akışlar bu üründe %100 yereldir ve cihaz dışına çıkış sağlamaz.

**S: Dashboard neden doğrudan oyun motoruyla iletişime geçmiyor?**
C: Dashboard, oluşturulan CLI sonuçlarını (JSON snapshot'lar) tarayıcıda grafiksel sunabilmek için yaratılmış ikincil bir görüntüleyicidir, Unreal Engine bellek alanına doğrudan bağlanıp canlı telemetri verisi çekmez.

---

**Geliştirici:** G & E ZYNTH  
**Lisans:** MIT  
**Web:** [github.com/gktrk363/unrealmate](https://github.com/gktrk363/unrealmate)
