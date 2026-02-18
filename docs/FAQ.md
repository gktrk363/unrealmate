<!--
╔══════════════════════════════════════════════════════════════════════════════╗
║                          UnrealMate - FAQ                                    ║
║                                                                              ║
║  Author: gktrk363                                                            ║
║  Purpose: Frequently Asked Questions                                         ║
║  Created: 2026-02-06                                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

© 2026 gktrk363 - Crafted with passion for Unreal Engine developers
-->

# ❓ Frequently Asked Questions (FAQ)

## 1. Which Unreal Engine versions are supported?
UnrealMate fully supports Unreal Engine 4.26, 4.27, and 5.0 through 5.4.

## 2. Does it backup my project before making changes?
Yes, destructive commands like `unrealmate minimize` or `unrealmate git clean` often have a `--dry-run` flag to preview changes. For safety, it is highly recommended to use `unrealmate backup create` before performing bulk operations.

## 3. Can I use this in CI/CD pipelines?
Absolutely! UnrealMate is designed to run in Docker containers and is compatible with Jenkins, GitLab CI, and GitHub Actions. Use `unrealmate build ci-init` to generate a starting pipeline configuration.

## 4. Does it work on Mac or Linux?
Yes, UnrealMate is cross-platform and works on Windows, macOS, and Linux.

## 5. Do AI commands require an internet connection?
No. The AI features (NLP, Bug Detection, Code Review) run locally on your machine using lightweight static analysis and pattern matching engines. Your code never leaves your computer.

## 6. Why does `unrealmate doctor` fail?
If `unrealmate doctor` returns an error (Exit Code 1), it usually means you are not running it inside a valid Unreal Engine project folder (a folder containing a `.uproject` file).

## 7. How do I access the Web Dashboard?
Run `unrealmate report dashboard` and open `http://localhost:8080` in your web browser. Make sure you have `flask` installed (`pip install flask`).

---
*Created by [gktrk363](https://github.com/gktrk363)*
