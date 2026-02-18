<!--
╔══════════════════════════════════════════════════════════════════════════════╗
║                          UnrealMate - Examples                               ║
║                                                                              ║
║  Author: gktrk363                                                            ║
║  Purpose: Example usages and workflows                                       ║
║  Created: 2026-02-06                                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

© 2026 gktrk363 - Crafted with passion for Unreal Engine developers
-->

# 💡 Örnekler ve Worflow'lar (Examples)

## Günlük Geliştirme Workflow'u
1. `unrealmate analyze` ile projeyi kontrol et.
2. Değişiklikleri yap.
3. `unrealmate build` ile derle.

## CI/CD Workflow Örneği (GitHub Actions)
```yaml
name: UnrealMate CI
on: [push]
jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Checks
        run: unrealmate analyze --ci-mode
```

---
*Created by [gktrk363](https://github.com/gktrk363)*
