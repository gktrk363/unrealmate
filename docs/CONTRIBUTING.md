<!--
╔══════════════════════════════════════════════════════════════════════════════╗
║                        UnrealMate - Contributing                             ║
║                                                                              ║
║  Author: gktrk363                                                            ║
║  Purpose: Guidelines for contributors                                        ║
║  Created: 2026-02-06                                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

© 2026 gktrk363 - Crafted with passion for Unreal Engine developers
-->

# 🤝 Katkıda Bulunma Rehberi (Contributing)

UnrealMate projesine katkıda bulunmak istediğiniz için teşekkürler! İşte nasıl başlayacağınız:

## Geliştirme Ortamı Kurulumu

1. Projeyi fork'layın ve klonlayın.
2. Bağımlılıkları yükleyin:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```
3. Pre-commit hooklarını kurun:
   ```bash
   pre-commit install
   ```

## Pull Request Süreci

1. Yeni bir feature branch açın: `feature/my-awesome-feature`
2. Değişikliklerinizi yapın ve testleri çalıştırın:
   ```bash
   pytest
   ```
3. Kodunuzu formatlayın:
   ```bash
   ruff format .
   ```
4. PR açın ve detaylı bir açıklama yazın.

## Kod Standartları

- **Type Hints:** Tüm fonksiyonlar type hint içermelidir.
- **Docstrings:** Google style docstrings kullanıyoruz.
- **Tests:** Yeni özellikler için test yazılması zorunludur.

---
*Created by [gktrk363](https://github.com/gktrk363)*
