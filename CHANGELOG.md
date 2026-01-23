# Changelog

All notable changes to UnrealMate will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).



## [1.0.10] - 2026-01-24

### Fixed
- 🐛 **Fixed:** Removed duplicated text in banner output that occurred when applying mixed colors to the "Crafted by" line.
- 📦 Version bumped to 1.0.10.

## [1.0.9] - 2026-01-24

### Changed
- 🎨 **UI Polish:** Refined banner aesthetics - "Crafted by" text is now Gray, while developer name remains Green for better contrast and elegance.
- 📦 Version bumped to 1.0.9.

## [1.0.8] - 2026-01-24

### Fixed
- 🐛 **Fixed:** Updated banner to Lime Green/Dark Gray theme as per user request.
- 🎨 Synchronized version number to 1.0.8.

## [1.0.7] - 2026-01-24

### Fixed
- 🐛 **Fixed:** Updated default banner ASCII art to ensures correct Green Blocky design is shown for all users, regardless of config settings.
- 🎨 Synchronized version number across all files to 1.0.7.

## [1.0.6] - 2026-01-24

### Fixed
- 🐛 **Fixed:** Corrected version display in CLI to show v1.0.5 (was showing outdated v1.0.1)

## [1.0.5] - 2026-01-24

### Changed
- 🎨 Updated version number in signature.py to 1.0.4

## [1.0.4] - 2026-01-24

### Changed
- 🎨 Improved banner color compatibility using standard terminal color names

## [1.0.3] - 2026-01-24

### Fixed
- 🐛 **Fixed:** Corrected banner colors in PyPI package (lime green theme now works correctly)

## [1.0.2] - 2026-01-24

### Changed
- 🎨 Updated banner color scheme to lime green and dark gray theme
- ✨ Improved visual aesthetics for better terminal display

## [1.0.1] - 2026-01-23

### Fixed
- **Critical:** Fixed package configuration to include all submodules (`unrealmate.core.*`)
- Package now correctly installs all modules when installed from PyPI

## [1.0.0] - 2026-01-23

### 🎉 Production/Stable Release

**Major milestone:** Complete feature set with personal branding throughout!

### Added

#### Personal Branding & Signature System
- ✨ Personal signature system with ASCII art banner
- ✨ Custom cyan (#00D9FF) and magenta (#FF006E) color theme
- ✨ Signature headers in all code files
- ✨ Branded panels in all commands
- ✨ Signature footer in command outputs
- ✨ Responsive banner that adapts to terminal width

#### Performance Tools
- ⚡ **Performance Profiler** - Analyze CPU/GPU/Memory bottlenecks
  - CSV profiling report parsing
  - Automatic severity assessment (OK/Warning/Critical)
  - Bottleneck detection with optimization suggestions
- ⚡ **Shader Analyzer** - Detect shader complexity issues
  - Instruction count estimation
  - Complexity scoring (0-100)
  - Detection of expensive operations (loops, texture samples, math)
  - Optimization suggestions
- ⚡ **Memory Auditor** - Track asset memory usage
  - Runtime memory estimation
  - Asset categorization and priority assessment
  - Optimization recommendations by category

#### Plugin Management
- 🔌 **Plugin Manager** - Complete plugin lifecycle management
  - Install plugins from Git repositories
  - Install plugins from local directories
  - Enable/disable plugins in .uproject
  - List all installed plugins with status
  - Remove plugins safely

#### Build & CI/CD Tools
- 🏗️ **CI/CD Generator** - Automated pipeline generation
  - GitHub Actions workflow generation
  - GitLab CI configuration generation
  - Jenkinsfile generation
  - Customizable templates with best practices
- 🏗️ **Build Info** - Project information and recommendations

#### Configuration System
- ⚙️ **Configuration Management** - `.unrealmate.toml` support
  - TOML-based configuration files
  - User preferences management
  - Easy get/set interface
  - Default values with validation
  - Config commands: init, show, set, get

#### Infrastructure
- 📝 **Logging System** - Comprehensive logging
  - Debug mode support
  - File logging with rotation
  - Structured logging with context
- 🎨 **Enhanced CLI** - Improved user experience
  - Branded panels for all commands
  - Progress indicators and status messages
  - Better error handling with helpful messages
  - Responsive design for various terminal widths

### Changed
- 📦 Updated to Production/Stable status (was Beta)
- 📦 Version bumped to 1.0.0
- 📦 Enhanced all existing commands with signature theme
- 📦 Improved error messages and user feedback
- 📦 Better terminal width handling

### Technical Details
- 📊 8 new modules created
- 📊 3 existing modules enhanced
- 📊 30+ total commands available
- 📊 ~2000+ lines of code added
- 📊 Personal signature in every file
- 📊 Comprehensive docstrings and type hints

---

## [0.2.0] - 2026-01-23

### Added
- Initial signature system
- Performance profiler (basic)
- Shader analyzer (basic)
- Configuration management (basic)

### Changed
- Updated to Beta status

---

## [0.1.10] - Previous

### Features
- Git tools (init, lfs, clean)
- Asset management (scan, organize, duplicates)
- Blueprint analysis (analyze, report)
- Doctor command for health checks

---

## Future Plans

### Planned Features
- 📊 Blueprint visual graph generation with graphviz
- 📊 Asset dependency graph visualization
- 🔧 Enhanced doctor command with auto-fix
- 📚 Interactive tutorial mode
- 🌐 Marketplace integration
- 📈 Telemetry (opt-in)

---

**© 2026 gktrk363 - Crafted with passion for Unreal Engine developers**
