<!--
╔══════════════════════════════════════════════════════════════════════════════╗
║                    UnrealMate - Plugin Development                           ║
║                                                                              ║
║  Author: gktrk363                                                            ║
║  Purpose: Guide for creating UnrealMate plugins                              ║
║  Created: 2026-02-06                                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

© 2026 gktrk363 - Crafted with passion for Unreal Engine developers
-->

# 🔌 Plugin Geliştirme Rehberi

UnrealMate, plugin mimarisi sayesinde genişletilebilir. Kendi plugininizi yazmak için bu rehberi takip edin.

## Temel Yapı

Bir plugin, `unrealmate/plugins/` altında bir klasör ve `plugin.py` dosyasından oluşur.

```python
from unrealmate.core.plugin_system import Plugin

class MyAwesomePlugin(Plugin):
    name = "MyAwesomePlugin"
    version = "1.0.0"
    
    def on_load(self):
        print("Plugin loaded!")
```

## Hook Noktaları
Pluginler, sistemin çeşitli noktalarına "hook" atabilir:
- `on_command_execute`
- `on_analysis_start`
- `on_build_complete`

---
*Created by [gktrk363](https://github.com/gktrk363)*
