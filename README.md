<h1 align="center">
  <br>
  🥶 UnrealMate
  <br>
</h1>

<h4 align="center">CLI-first Unreal Engine workflow tooling.</h4>

<p align="center">
  <a href="#-current-surface">Current Surface</a> •
  <a href="#-installation">Installation</a> •
  <a href="#-documentation">Documentation</a> •
  <a href="#-contributing">Contributing</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-1.1.4-blue.svg?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/python-3.10+-yellow.svg?style=flat-square" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-green.svg?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/downloads-1k%2B%2Fmonth-brightgreen.svg?style=flat-square" alt="Downloads">
  <img src="https://img.shields.io/badge/platform-windows%20%7C%20linux-lightgrey.svg?style=flat-square" alt="Platform">
</p>

<div align="center">
  <sub>Built with ❤︎ by <a href="https://github.com/gktrk363">G & E ZYNTH</a></sub>
</div>

<br>

**UnrealMate** is a CLI-first toolkit for Unreal Engine projects. The strongest current surface is the stable/default CLI: `doctor`, `config`, `git`, `asset`, `performance`, `plugin`, and local report export flows. `report dashboard` exists as an experimental secondary surface launched from the CLI.

---

## ✨ Current Surface

*   **Project checks**: `doctor`, `config validate`, `build info`
*   **Project state management**: `git init`, `git lfs`, `git clean`, `plugin` commands
*   **Project analysis**: `asset scan`, `asset duplicates`, `asset organize`, `performance profile`, `performance memory`, `performance shaders`
*   **Local reporting**: `report html`, `report json`, and experimental `report dashboard`

---

## 🚀 Installation

```bash
pip install unrealmate
python -m unrealmate version
```

After installation, you can run UnrealMate as either `python -m unrealmate` or the installed `unrealmate` command.

### Requirements
*   Python 3.10 or higher
*   Git installed and in PATH
*   (Optional) Unreal Engine 5.0+ installed

---

## 📖 Documentation

Detailed documentation is available in the project root:

*   **Canonical project status**: `docs/PROJECT_STATUS.md`
*   **Product / UX reality snapshot**: `docs/PRODUCT_AND_UX_STATUS.md`
*   **Generated command truth surfaces**: `docs/COMMAND_SURFACES.md`

---

## 🎮 First Run

Most users should start with the stable/default CLI surface and inspection commands like these.

Run these from your Unreal project root:

```bash
# 1. Check local readiness
unrealmate doctor

# 2. Review local config safely
unrealmate config show

# 3. Scan project assets without changing files
unrealmate asset scan Content

# 4. Review local project metadata
unrealmate build info .
```

Start with inspection commands like the examples above. Treat config setup, git setup or cleanup, plugin mutations, and local report exports as later steps once you are ready to change local state.

Use `python -m unrealmate --help` for the stable/default CLI surface. Use `python -m unrealmate --help-all` when you want to review opt-in, experimental, mock, or secondary surfaces.

---

## 🧭 Use It On Your Project

Run UnrealMate from your Unreal project root, or pass `<project-root>` to commands that accept a project path.

```bash
python -m unrealmate build info <project-root>
python -m unrealmate plugin list <project-root>
```

---

## 🤝 Contributing

Please read `docs/PROJECT_STATUS.md` first, then submit a Pull Request with tests.

---

## 📄 License

MIT License. See `LICENSE` for details.

**Crafted with ❤ by G & E ZYNTH**

