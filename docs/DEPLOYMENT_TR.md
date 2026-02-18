# UnrealMate Sunucu Kurulum Rehberi

**`collab dashboard`** ve **`report dashboard`** web arayüzlerini sanal sunucuya kurarak tüm ekibin erişimine açın.

---

## Gereksinimler

- VPS (Ubuntu 22.04+ önerilir) veya Docker sunucusu
- Python 3.10+
- Alan adı (isteğe bağlı ama önerilir)

---

## Hızlı Kurulum (Docker)

```bash
# Klonla ve derle
git clone https://github.com/gktrk363/unrealmate.git
cd unrealmate
docker build -t unrealmate .

# Dashboard'u başlat
docker run -d -p 8080:8080 --name unrealmate-dashboard unrealmate \
    python -m unrealmate report dashboard --host 0.0.0.0 --port 8080
```

Erişim: `http://sunucu-ip-adresiniz:8080`

---

## Manuel Kurulum (VPS)

### 1. Sunucu Hazırlığı

```bash
# Sistemi güncelle
sudo apt update && sudo apt upgrade -y

# Python kur
sudo apt install -y python3 python3-pip python3-venv git

# Servis kullanıcısı oluştur
sudo useradd -m -s /bin/bash unrealmate
sudo su - unrealmate
```

### 2. UnrealMate Kurulumu

```bash
# Klonla ve kur
git clone https://github.com/gktrk363/unrealmate.git
cd unrealmate
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### 3. Systemd Servisi

`/etc/systemd/system/unrealmate-dashboard.service` dosyasını oluşturun:

```ini
[Unit]
Description=UnrealMate Ekip Dashboard'u
After=network.target

[Service]
Type=simple
User=unrealmate
WorkingDirectory=/home/unrealmate/unrealmate
ExecStart=/home/unrealmate/unrealmate/venv/bin/python -m unrealmate report dashboard --host 0.0.0.0 --port 8080
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable unrealmate-dashboard
sudo systemctl start unrealmate-dashboard
```

### 4. Ters Proxy (Nginx)

```bash
sudo apt install -y nginx certbot python3-certbot-nginx
```

`/etc/nginx/sites-available/unrealmate` dosyasını oluşturun:

```nginx
server {
    listen 80;
    server_name dashboard.siteadiniz.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/unrealmate /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# SSL sertifikası (isteğe bağlı)
sudo certbot --nginx -d dashboard.siteadiniz.com
```

---

## İzleme ve Yönetim

```bash
# Logları görüntüle
sudo journalctl -u unrealmate-dashboard -f

# Durum kontrolü
sudo systemctl status unrealmate-dashboard

# Yeniden başlat
sudo systemctl restart unrealmate-dashboard
```

---

## Güvenlik Duvarı

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

---

© 2026 gktrk363
