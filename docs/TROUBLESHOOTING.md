<!--
╔══════════════════════════════════════════════════════════════════════════════╗
║                      UnrealMate - Troubleshooting                            ║
║                                                                              ║
║  Author: gktrk363                                                            ║
║  Purpose: Common issues and solutions                                        ║
║  Created: 2026-02-06                                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

© 2026 gktrk363 - Crafted with passion for Unreal Engine developers
-->

# 🔧 Troubleshooting

## Common Issues

### "Command not found: unrealmate"
- **Solution:** Ensure your Python Scripts folder is in your PATH.
  ```bash
  export PATH="$PATH:/path/to/python/scripts"
  ```

### "Access Denied" errors
- **Solution:** Run the command with Administrator privileges or check file permissions.

### Blueprint Analysis is slow
- **Solution:** For large projects, analysis can take time. Try scanning a specific folder:
  ```bash
  unrealmate blueprint analyze /path/to/project/Content/SpecificFolder
  ```

### "Web Dashboard not opening" / Port in use
- **Solution:** The dashboard uses port **8080** by default. Ensure no other application is using this port. You also need to install flask:
  ```bash
  pip install flask
  ```

### "Asset Scan failed"
- **Solution:** Ensure you are running the command from the root of a valid Unreal Engine project (where `.uproject` is located).

---
*Created by [gktrk363](https://github.com/gktrk363)*
