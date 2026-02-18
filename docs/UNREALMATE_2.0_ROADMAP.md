# 🚀 UnrealMate v2.0: The Next Level Roadmap

This document outlines the strategic vision to evolve UnrealMate from a **Developer CLI** into a **Holistic Production Ecosystem**.

[Türkçe Versiyonu İçin Aşağı Kaydırın 👇](#-unrealmate-v20-yol-haritası-türkçe)

---

## 🗺️ Strategic Vision: The "Mate" Ecosystem (English)

Currently, UnrealMate is a powerful *sidekick* (CLI). The next level is to make it the *command center* of the studio.

### Phase 1: Deep Editor Integration (Inside the Engine)
**Goal:** Developers shouldn't have to leave Unreal Editor to use UnrealMate.

- [ ] **UnrealMate Editor Plugin (C++/Python)**
    - Add an **UnrealMate Toolbar** inside UE5.
    - **Context Menu Integration**: Right-click an asset in Content Browser -> `UnrealMate > Analyze Complexity`.
    - **Output Log Hook**: Catch errors in real-time inside the Output Log and offer "Auto-Fix" buttons.
    - **Startup Guard**: Prevent Editor launch if project health is below a threshold (optional).

### Phase 2: The Desktop Experience (GUI)
**Goal:** Empower Artists, Level Designers, and Producers who fear the Command Line.

- [ ] **UnrealMate Desktop App (Electron/Tauri or PyQt)**
    - **Visual Asset Graph**: 3D interactive node graph showing references between Blueprints and Assets.
    - **One-Click Build**: A simple "Build & Deploy" button that handles all flags/Docker stuff in the background.
    - **Drag & Drop Optimization**: Drop a folder of 4K textures, auto-convert to optimal settings.
    - **Live Dashboard**: Real-time CPU/GPU memory monitoring separate from the Editor.

### Phase 3: "True" AI Agents (Beyond Regex)
**Goal:** Move from heuristic pattern matching to Semantic Understanding.

- [ ] **Local LLM Integration (Ollama/Llama 3)**
    - **"Chat with Project"**: "Where is the logic for the double-jump?" -> AI scans Blueprints and points you to the file.
    - **Semantic Code Search**: "Find all weapons that deal fire damage" (understands logic, not just text).
    - **Auto-Refactor Agent**: Not just *detecting* bugs, but generating a patch file to fix C++ header errors automatically.
    - **Texture Hallucination**: "Generate a roughness map for this texture" using Stable Diffusion capabilities.

### Phase 4: Cloud & Team SaaS (The Enterprise Tier)
**Goal:** Centralized management for distributed teams.

- [ ] **UnrealMate Cloud Dashboard**
    - **Remote Build Farm**: Orchestrate builds across multiple cheap VPS nodes.
    - **Asset Locking Map**: Visual map of who is working on what (integrating with Perforce/Git).
    - **Global Telemetry**: Compare your project's performance metrics against "Anonymous Global Averages".
    - **Team Health**: "Developer Burnout Prediction" based on commit times and frequency.

---

## 🛠️ Technical Foundation Updates Needed

To support this v2.0 vision, the core needs to evolve:

1.  **API-First Architecture**: Refactor `cli.py` so the CLI is just *one* client. The core logic should be a fast API server (FastAPI) that the CLI, Editor Plugin, and Desktop App all talk to.
2.  **Rust Core (Optional)**: Rewrite the heavy file-scanning parts (Asset Scan) in Rust for 100x speed on massive projects (100GB+).
3.  **Database Layer**: Move from JSON files (`analytics.json`) to a local SQLite database to handle complex relationships for the "Chat with Project" feature.

---

## 📅 Timeline Estimation

| Phase | Duration | Key Deliverable |
|-------|----------|-----------------|
| **Review**| 2 Weeks | API Refactoring |
| **Ph 1** | 1 Month  | UE5 Editor Plugin (Toolbar) |
| **Ph 2** | 2 Months | Desktop App (Alpha) |
| **Ph 3** | 3 Months | LLM Integration (Beta) |
| **Ph 4** | 6 Months+| SaaS Dashboard |

---
---

# 🚀 UnrealMate v2.0: Yol Haritası (Türkçe)

Bu belge, UnrealMate'i basit bir **Geliştirici CLI Aracı** olmaktan çıkarıp, bütüncül bir **Prodüksiyon Ekosistemi** haline getirecek stratejik vizyonu çizer.

---

## 🗺️ Stratejik Vizyon: "Mate" Ekosistemi

Şu anda UnrealMate güçlü bir yardımcı (sidekick). Bir sonraki adımda stüdyonun **komuta merkezi** olması hedefleniyor.

### Evre 1: Derin Editör Entegrasyonu (Motorun İçinde) 🔌
**Hedef:** Geliştiriciler UnrealMate kullanmak için Unreal Editor'den çıkmak zorunda kalmamalı.

- [ ] **UnrealMate Editor Plugin (C++/Python)**
    - UE5 içine bir **UnrealMate Araç Çubuğu** ekle.
    - **Sağ Tık Menüsü**: Content Browser'da bir asset'e sağ tıkla -> `UnrealMate > Analiz Et`.
    - **Output Log Kancası**: Hataları anlık yakala ve Log penceresinde "Otomatik Düzelt" butonu sun.
    - **Başlangıç Koruması**: Proje sağlığı belirli bir seviyenin altındaysa editörün açılmasını engelle (opsiyonel).

### Evre 2: Masaüstü Deneyimi (GUI) 🖥️
**Hedef:** Terminalden korkan Artistler, Level Designer'lar ve Yapımcılar için kullanım kolaylığı.

- [ ] **UnrealMate Masaüstü Uygulaması**
    - **Görsel Asset Grafiği**: Blueprint ve Assetler arasındaki referansları 3 boyutlu ağ grafiği olarak göster.
    - **Tek Tıkla Build**: Arka plandaki tüm karmaşık Docker/Flag işlerini gizleyen basit bir "Derle ve Dağıt" butonu.
    - **Sürükle & Bırak Optimizasyon**: Bir klasör dolusu 4K texture'ı bırak, otomatik olarak en uygun ayarlara dönüştürsün.
    - **Canlı Dashboard**: Editörden bağımsız, gerçek zamanlı CPU/GPU bellek izleme paneli.

### Evre 3: Gerçek Yapay Zeka Ajanları 🧠
**Hedef:** Basit kalıp eşleştirme (Regex) yerine Anlamsal Kavrayışa geçiş.

- [ ] **Yerel LLM Entegrasyonu (Ollama/Llama 3)**
    - **"Projeyle Sohbet Et"**: "Çift zıplama mekaniği nerede?" -> AI Blueprintleri tarar ve dosyayı gösterir.
    - **Anlamsal Kod Arama**: "Ateş hasarı veren tüm silahları bul" (sadece metni değil, mantığı anlar).
    - **Otomatik Refactor Ajanı**: Sadece hatayı tespit etmekle kalmaz, C++ header hatalarını düzelten bir yama dosyası oluşturur.
    - **Texture Halüsinasyonu**: Stable Diffusion yeteneklerini kullanarak, bir texture için roughness haritası üretir.

### Evre 4: Bulut & Takım SaaS (Enterprise) ☁️
**Hedef:** Dağınık ekipler için merkezi yönetim.

- [ ] **UnrealMate Bulut Paneli**
    - **Uzaktan Build Çiftliği**: Build işlemlerini birden fazla ucuz VPS sunucusuna dağıtarak yönet.
    - **Asset Kilit Haritası**: Kimin hangi dosya üzerinde çalıştığını gösteren görsel harita (Perforce/Git ile entegre).
    - **Küresel Telemetri**: Projenizin performans verilerini "Anonim Küresel Ortalamalar" ile kıyasla.
    - **Takım Sağlığı**: Commit sıklığına ve saatlerine bakarak "Geliştirici Tükenmişliği (Burnout)" tahmini yap.

---

## 🛠️ Teknik Altyapı Güncellemeleri

Bu v2.0 vizyonunu desteklemek için çekirdeğin evrimleşmesi gerekiyor:

1.  **API-Öncelikli Mimari**: `cli.py` yeniden düzenlenmeli. Çekirdek mantık hızlı bir API sunucusu (FastAPI) olmalı; CLI, Editör Eklentisi ve Masaüstü Uygulaması bu API ile konuşmalı.
2.  **Rust Çekirdek (Opsiyonel)**: Devasa projelerde (100GB+) dosya tarama işlemlerini 100 kat hızlandırmak için kritik kısımları Rust ile yeniden yaz.
3.  **Veri Tabanı Katmanı**: Karmaşık ilişkileri (Sohbet özelliği için graph verisi) yönetmek için JSON dosyalarından (`analytics.json`) yerel SQLite veri tabanına geçiş.

---

## 📅 Tahmini Zaman Çizelgesi

| Evre | Süre | Ana Teslimat |
|------|------|--------------|
| **Review**| 2 Hafta | API Yeniden Düzenleme |
| **Evre 1** | 1 Ay   | UE5 Editör Eklentisi (Toolbar) |
| **Evre 2** | 2 Ay   | Masaüstü Uygulaması (Alpha) |
| **Evre 3** | 3 Ay   | LLM Entegrasyonu (Beta) |
| **Evre 4** | 6 Ay+  | SaaS Paneli |

---

> **Hazırlayan**: gktrk363 (Mevcut) UnrealMate v1.1.1
> **Hedef**: UnrealMate v2.0 (Ekosistem)
