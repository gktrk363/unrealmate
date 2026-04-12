# Command Surfaces

<!-- AUTO-GENERATED FILE. DO NOT EDIT. -->
<!-- Source: unrealmate/registry/command_registry.toml + tests/smoke -->
<!-- Regenerate with: python scripts/sync_docs_from_registry.py -->

Bu dosya command truth surfaces icerigini registry metadata'dan otomatik uretilmis tek kaynakta birlestirir.

## Command Maturity Matrix

# Command Maturity Matrix

<!-- AUTO-GENERATED FILE. DO NOT EDIT. -->
<!-- Source: unrealmate/registry/command_registry.toml -->
<!-- Regenerate with: python scripts/sync_docs_from_registry.py -->

Bu dosya registry metadata'dan otomatik uretilir.

## Matrix

| Command Group | Subcommand | Maturity | Status | Visibility | Evidence | Notes |
|---|---|---|---|---|---|---|
| `ai` | `detect-bugs` | `experimental` | `risky` | `opt-in` | `unrealmate/cli.py:3138-3173`<br>`unrealmate/core/bug_detector.py:103-177`<br>`unrealmate/core/bug_detector.py:405-427` | Pattern tabanli; Blueprint ozel detector bolumu placeholder. |
| `ai` | `nlp` | `experimental` | `risky` | `opt-in` | `unrealmate/cli.py:3110-3134`<br>`unrealmate/core/nlp_commands.py:65`<br>`unrealmate/core/nlp_commands.py:83`<br>`unrealmate/core/nlp_commands.py:100` | Intent mapping komut gercegiyle driftli (or. `build project`, `blueprint list`). |
| `ai` | `review` | `experimental` | `risky` | `opt-in` | `unrealmate/cli.py:3177-3205`<br>`unrealmate/core/code_review.py:236-269`<br>`unrealmate/core/code_review.py:387-399` | GitHub/GitLab entegrasyonu kisitli; bazi provider metodlari placeholder donuyor. |
| `asset` | `duplicates` | `stable` | `risky` | `default` | `unrealmate/cli.py:1186-1268`<br>`unrealmate/cli.py:1206-1208`<br>`unrealmate/cli.py:1238` | Tespit yapar ama extension listesinde bosluklu girdiler (`. tga`, `. flac`) var. |
| `asset` | `organize` | `stable` | `risky` | `default` | `unrealmate/cli.py:1064-1182`<br>`unrealmate/cli.py:1094`<br>`unrealmate/cli.py:1098`<br>`unrealmate/cli.py:1174` | Dosya tasir (destructive). Extension listesinde bosluklu patternler var (`. dae`, `. mkv`). |
| `asset` | `scan` | `stable` | `risky` | `default` | `unrealmate/cli.py:927-1060`<br>`unrealmate/cli.py:976-981`<br>`unrealmate/cli.py:963` | Heuristic siniflama yapar; cp1254 ortaminda gorsel cikti kaynakli risk mevcut. |
| `automate` | `fix` | `experimental` | `risky` | `opt-in` | `unrealmate/cli.py:3213-3242`<br>`unrealmate/core/autofix.py:102-113`<br>`unrealmate/core/autofix.py:324-333` | Gercek dosya degisikligi yapabilir; kapsamli guvenlik siniri/allowlist yok. |
| `automate` | `organize` | `experimental` | `partially-implemented` | `opt-in` | `unrealmate/cli.py:3246-3265`<br>`unrealmate/cli.py:3262`<br>`unrealmate/core/smart_organizer.py:294` | Smart organizer output key fallback applied; still experimental. |
| `backup` | `create` | `experimental` | `risky` | `opt-in` | `unrealmate/cli.py:2317-2388`<br>`unrealmate/cli.py:2355-2381` | Snapshot kopyasi alir; dry-run yok, buyuk projelerde maliyet yuksek. |
| `backup` | `list` | `experimental` | `risky` | `opt-in` | `unrealmate/cli.py:2392-2435`<br>`unrealmate/cli.py:2403-2417` | Basit klasor patterniyle listeler (`_backup_`), metadata modeli sinirli. |
| `backup` | `restore` | `experimental` | `risky` | `opt-in` | `unrealmate/cli.py:2439-2467`<br>`unrealmate/cli.py:2456-2465` | `copytree` ile toplu overwrite yapabilir; rollback yok. |
| `blueprint` | `analyze` | `experimental` | `risky` | `opt-in` | `unrealmate/cli.py:1274-1380`<br>`unrealmate/cli.py:517-540`<br>`unrealmate/cli.py:1309` | .uasset binary icinden UTF-8 heuristic parse ile metrik cikarimi yapiyor. |
| `blueprint` | `report` | `experimental` | `risky` | `opt-in` | `unrealmate/cli.py:1384-1588`<br>`unrealmate/cli.py:517-540`<br>`unrealmate/cli.py:1418-1424` | Raporlama var ama complexity verisi heuristic; HTML cikti path/format kontrolleri kisitli. |
| `build` | `ci-init` | `stable` | `partially-implemented` | `default` | `unrealmate/cli.py:2005-2044`<br>`unrealmate/core/automation/ci_generator.py:63`<br>`unrealmate/core/automation/ci_generator.py:109`<br>`unrealmate/core/automation/ci_generator.py:164` | CI dosyasi uretir; `--dry-run` preview ve `--force` overwrite guard var, ama UE path/version hala hardcoded (`UE_5.3`). |
| `build` | `docker` | `stable` | `partially-implemented` | `default` | `unrealmate/cli.py:2623-2673`<br>`unrealmate/cli.py:2633-2657`<br>`unrealmate/cli.py:2656` | Dockerfile uretir; `--dry-run` preview ve `--force` overwrite guard var, ama `ProjectName` placeholder hala manuel guncelleme istiyor. |
| `build` | `info` | `stable` | `partially-implemented` | `default` | `unrealmate/cli.py:2048-2100`<br>`unrealmate/cli.py:2060-2085` | .uproject metadata okur; build pipeline durumunu dogrudan denetlemez. |
| `collab` | `dashboard` | `experimental` | `risky` | `opt-in` | `unrealmate/cli.py:3273-3318`<br>`unrealmate/core/team_dashboard.py:212`<br>`unrealmate/core/team_dashboard.py:251`<br>`unrealmate/core/team_dashboard.py:307-309` | Takim metrikleri heuristik/default agirlikli; role/platform/config varsayimlari sabit. |
| `collab` | `share` | `experimental` | `risky` | `opt-in` | `unrealmate/cli.py:3321-3349`<br>`unrealmate/cli.py:3337-3344`<br>`unrealmate/core/template_sharing.py:175-183`<br>`unrealmate/core/template_sharing.py:492-505` | CLI lokal zip export yapiyor; gercek remote share akisinda mock implementation mevcut. |
| `config` | `edit` | `stable` | `risky` | `default` | `unrealmate/cli.py:314-345`<br>`unrealmate/cli.py:332-340` | Yerel `.unrealmate.toml` dosyasini varsayilan editor ile acmayi dener; editor launch davranisi platform bagimli kalir. |
| `config` | `get` | `stable` | `risky` | `default` | `unrealmate/cli.py:1820-1829`<br>`unrealmate/core/config.py:183-191` | Basit dot-notation okur; olmayan key icin `None` dondurur. |
| `config` | `init` | `stable` | `risky` | `default` | `unrealmate/cli.py:1756-1769`<br>`unrealmate/core/config.py:150-167`<br>`python -m unrealmate config init --force` | Fonksiyonel olarak config olusturuyor; cp1254 terminalde spinner/emoji ciktilari kiriyor. |
| `config` | `set` | `stable` | `risky` | `default` | `unrealmate/cli.py:1808-1816`<br>`unrealmate/core/config.py:209-220`<br>`python -m unrealmate config set ...` | Yalnizca `section.key` formatini destekliyor; nested key/unknown section desteklenmiyor. |
| `config` | `show` | `stable` | `risky` | `default` | `unrealmate/cli.py:1773-1804`<br>`unrealmate/cli.py:1784-1803`<br>`unrealmate/core/config.py:84-114` | Cikti guvenilir, ancak komut akisinda Unicode gorsel katman riski var. |
| `config` | `template` | `stable` | `risky` | `default` | `unrealmate/cli.py:422-470`<br>`unrealmate/cli.py:431-444` | Hardcoded preset uygular; `--dry-run` preview vardir, [performance] section overwrite eder ve rollback snapshot olusturmaz. |
| `config` | `validate` | `stable` | `risky` | `default` | `unrealmate/cli.py:348-419`<br>`unrealmate/cli.py:379-403` | Temel schema dogrular; kapsamli schema/migration dogrulamasi yok. |
| `git` | `clean` | `stable` | `risky` | `default` | `unrealmate/cli.py:829-923`<br>`unrealmate/cli.py:830-832`<br>`unrealmate/cli.py:904` | Destructive islem; `--dry-run` var ama varsayilan akista klasor siler. |
| `git` | `init` | `stable` | `risky` | `default` | `unrealmate/cli.py:702-749`<br>`unrealmate/templates/gitignore.template:7`<br>`unrealmate/templates/gitignore.template:48` | Template patternlerinde bosluk bozuklugu var (`*. sln`, `*. ini. bak`). |
| `git` | `lfs` | `stable` | `risky` | `default` | `unrealmate/cli.py:753-825`<br>`unrealmate/templates/gitattributes.template:6`<br>`unrealmate/templates/gitattributes.template:42` | LFS template patternlerinde bosluk bozuklugu var (`*. uasset`, `*. exe`). |
| `marketplace` | `check-updates` | `mock` | `placeholder` | `opt-in` | `unrealmate/cli.py:3024-3054`<br>`unrealmate/cli.py:3032`<br>`unrealmate/cli.py:3048` | Guncelleme kontrolu simule edilir; launcher yonlendirmesi informational. |
| `marketplace` | `export-list` | `mock` | `placeholder` | `opt-in` | `unrealmate/cli.py:3057-3091`<br>`unrealmate/cli.py:3069-3079`<br>`unrealmate/cli.py:3083-3087` | Export calisir ama kaynak veri mock DB. |
| `marketplace` | `install` | `mock` | `partially-implemented` | `opt-in` | `unrealmate/cli.py:2964-2988`<br>`unrealmate/cli.py:2986-2987`<br>`unrealmate/cli.py:2985` | Mock browser handoff flow exists; still not a real marketplace integration. |
| `marketplace` | `list` | `mock` | `placeholder` | `opt-in` | `unrealmate/cli.py:2991-3021`<br>`unrealmate/cli.py:3001-3017`<br>`unrealmate/cli.py:3020` | Kurulu/owned listeyi lokal mock DB uzerinden gosterir. |
| `marketplace` | `search` | `mock` | `placeholder` | `opt-in` | `unrealmate/cli.py:2925-2961`<br>`unrealmate/cli.py:2900-2921`<br>`unrealmate/cli.py:2935-2941`<br>`unrealmate/cli.py:2954` | Gercek marketplace API yerine lokal mock DB ile simule eder. |
| `migrate` | `assets` | `experimental` | `risky` | `opt-in` | `unrealmate/cli.py:2253-2310`<br>`unrealmate/cli.py:2293-2307` | Dosya kopyalar ama asset dependency/reference integrity kontrolu yapmaz. |
| `migrate` | `version` | `experimental` | `risky` | `opt-in` | `unrealmate/cli.py:2212-2249`<br>`unrealmate/cli.py:2233-2245` | `EngineAssociation` dogrudan overwrite edilir; compatibility preflight yok. |
| `optimize` | `scan` | `mock` | `placeholder` | `opt-in` | `unrealmate/cli.py:2116-2146`<br>`unrealmate/cli.py:2127-2135` | Acikca simulated work/result kullaniyor. |
| `optimize` | `textures` | `experimental` | `partially-implemented` | `opt-in` | `unrealmate/cli.py:2150-2204`<br>`unrealmate/cli.py:2174-2188`<br>`unrealmate/cli.py:2196-2200` | Heuristic dosya boyutu kontrolu yapar; `--fix` adimi gercek texture pipeline entegrasyonu degil. |
| `performance` | `drawcalls` | `experimental` | `partially-implemented` | `opt-in` | `unrealmate/cli.py:1665-1702`<br>`unrealmate/cli.py:1678-1691` | Gercek draw call olcumu degil, dosya sayisina dayali tahmin tablosu. |
| `performance` | `memory` | `stable` | `risky` | `default` | `unrealmate/cli.py:1837-1864`<br>`unrealmate/core/performance/memory_auditor.py:102-141`<br>`unrealmate/core/performance/memory_auditor.py:159-168` | Disk size * multiplier yaklasimi kullanir; runtime memory tahmini dogal olarak yaklasik. |
| `performance` | `network` | `experimental` | `partially-implemented` | `opt-in` | `unrealmate/cli.py:1705-1749`<br>`unrealmate/cli.py:1725-1729`<br>`unrealmate/cli.py:1733-1739` | Regex benzeri satir tarama ile replication audit; semantic parse yok. |
| `performance` | `profile` | `stable` | `risky` | `default` | `unrealmate/cli.py:1596-1629`<br>`unrealmate/core/performance/profiler.py:72-83`<br>`unrealmate/core/performance/profiler.py:212-231` | CSV profiling verisine dayali; veri yoksa sessizce no-data doner. |
| `performance` | `shaders` | `stable` | `risky` | `default` | `unrealmate/cli.py:1633-1660`<br>`unrealmate/core/performance/shader_analyzer.py:48-68`<br>`unrealmate/core/performance/shader_analyzer.py:161-178` | Kaynak dosya heuristic analizi; shader complexity UE compiler seviyesinde degil. |
| `plugin` | `disable` | `stable` | `risky` | `default` | `unrealmate/cli.py:1950-1968`<br>`unrealmate/core/plugins/manager.py:188-217` | .uproject only mutates locally; no plugin files are copied or deleted, and disable refuses missing entries instead of reporting a false success. |
| `plugin` | `enable` | `stable` | `risky` | `default` | `unrealmate/cli.py:1928-1946`<br>`unrealmate/core/plugins/manager.py:153-185` | .uproject only mutates locally; no plugin files are copied or deleted, and writes use an atomic temp-file replace. |
| `plugin` | `install` | `stable` | `risky` | `default` | `unrealmate/cli.py:1893-1924`<br>`unrealmate/core/plugins/manager.py:88-120`<br>`unrealmate/core/plugins/manager.py:122-151` | Writes local Plugins/ state directly, does not edit .uproject automatically, has no rollback, and failed installs may leave partial local files behind. |
| `plugin` | `list` | `stable` | `risky` | `default` | `unrealmate/cli.py:1872-1889`<br>`unrealmate/core/plugins/manager.py:56-86` | Yerel `Plugins/**/*.uplugin` uzerinden listeler; cp1254 cikti riski mevcut. |
| `plugin` | `remove` | `stable` | `risky` | `default` | `unrealmate/cli.py:1972-1997`<br>`unrealmate/core/plugins/manager.py:220-239`<br>`unrealmate/cli.py:1988-1995` | Deletes only the local plugin directory, never cleans .uproject references automatically, and manual recovery may be required after filesystem failures. |
| `report` | `dashboard` | `experimental` | `risky` | `opt-in` | `unrealmate/cli.py:2595-2645`<br>`unrealmate/core/application/use_cases/start_report_dashboard.py:20-37`<br>`unrealmate/adapters/report/report_dashboard_adapter.py:54-272` | Lifecycle adapter ile startup readiness/structured stop var; long-running runtime edge-case riski suruyor. |
| `report` | `html` | `stable` | `risky` | `default` | `unrealmate/cli.py:2720-2804`<br>`unrealmate/cli.py:2734-2744`<br>`unrealmate/cli.py:2795-2800` | Gercek dosya sayimlariyla rapor yazar; Unicode output/cp1254 riski suruyor. |
| `report` | `json` | `stable` | `risky` | `default` | `unrealmate/cli.py:2807-2856`<br>`unrealmate/cli.py:2821-2841`<br>`unrealmate/cli.py:2846-2853` | JSON export var; panel ciktisi ve emoji kullanimi Windows legacy terminalde riskli. |
| `report` | `notify` | `local-only` | `partially-implemented` | `default` | `unrealmate/cli.py:2698-2727`<br>`unrealmate/cli.py:590-619`<br>`unrealmate/core/config.py:50-52`<br>`unrealmate/core/config.py:115-122`<br>`unrealmate/core/config.py:146-150` | Sadece lokal log yaziyor; `notification.webhook_url` schema ile uyumlu ama webhook gonderimi uygulanmis degil. |
| `root` | `analytics` | `local-only` | `risky` | `default` | `unrealmate/cli.py:3357-3389`<br>`unrealmate/core/analytics.py:49-57`<br>`unrealmate/core/analytics.py:73-76` | Sadece `~/.unrealmate/analytics.json` lokal verisini okur/yazar. |
| `root` | `doctor` | `stable` | `risky` | `default` | `unrealmate/cli.py:592-698`<br>`unrealmate/core/visuals.py:335-337`<br>`python -m unrealmate doctor` | Gercek kontrol yapiyor ama spinner Unicode sebebiyle Windows cp1254 ortaminda calisma riski yuksek. |
| `root` | `health` | `mock` | `placeholder` | `opt-in` | `unrealmate/cli.py:3391-3436`<br>`unrealmate/cli.py:3408`<br>`unrealmate/core/project_health.py:57-62` | Health skoru placeholder metriklerle hesaplanir. |
| `root` | `security-scan` | `mock` | `placeholder` | `opt-in` | `unrealmate/cli.py:3440-3461`<br>`unrealmate/core/security.py:27-33`<br>`unrealmate/core/security.py:52-56` | Dependency taramasi mock; gercek `pip-audit/safety` entegrasyonu yok. |
| `root` | `version` | `stable` | `production-ready` | `default` | `unrealmate/cli.py:560-590`<br>`unrealmate/cli.py:562-579` | Minimal yan etki, dogrudan bilgi komutu. |
| `template` | `create` | `experimental` | `risky` | `opt-in` | `unrealmate/cli.py:2507-2566`<br>`unrealmate/cli.py:2531-2555`<br>`unrealmate/cli.py:2540` | Scaffold uretiyor; engine/module ayarlari template-agnostic degil. |
| `template` | `list` | `experimental` | `risky` | `opt-in` | `unrealmate/cli.py:2486-2503`<br>`unrealmate/cli.py:2474-2502` | Template listesi hardcoded; registry/discovery yok. |
| `template` | `save` | `experimental` | `risky` | `opt-in` | `unrealmate/cli.py:2570-2620`<br>`unrealmate/cli.py:2582-2617`<br>`unrealmate/cli.py:2604` | Yerel template kaydeder; 10MB ustu content dosyalari atlanir. |

## Stable Surface
- `asset`: `duplicates`, `organize`, `scan`
- `build`: `ci-init`, `docker`, `info`
- `config`: `edit`, `get`, `init`, `set`, `show`, `template`, `validate`
- `git`: `clean`, `init`, `lfs`
- `performance`: `memory`, `profile`, `shaders`
- `plugin`: `disable`, `enable`, `install`, `list`, `remove`
- `report`: `html`, `json`
- `root`: `doctor`, `version`

## Experimental Surface
- `ai`: `detect-bugs`, `nlp`, `review`
- `automate`: `fix`, `organize`
- `backup`: `create`, `list`, `restore`
- `blueprint`: `analyze`, `report`
- `collab`: `dashboard`, `share`
- `migrate`: `assets`, `version`
- `optimize`: `textures`
- `performance`: `drawcalls`, `network`
- `report`: `dashboard`
- `template`: `create`, `list`, `save`

## Mock Surface
- `marketplace`: `check-updates`, `export-list`, `install`, `list`, `search`
- `optimize`: `scan`
- `root`: `health`, `security-scan`

## Local-only Surface
- `report`: `notify`
- `root`: `analytics`

## Deprecated Surface
- None.

## Immediate Hide/Label Recommendations
- Policy check: no `mock` command is exposed in default help.
- Policy check: no `experimental` command is exposed in default help.
- Keep explicit `[local-only]` labels on default-visible local commands: `report notify`, `root analytics`.
- Stable but risky/partially-implemented commands should keep caution notes: `asset duplicates`, `asset organize`, `asset scan`, `build ci-init`, `build docker`, `build info`, `config edit`, `config get`, `config init`, `config set`, `config show`, `config template`, `config validate`, `git clean`, `git init`, `git lfs`, `performance memory`, `performance profile`, `performance shaders`, `plugin disable`, `plugin enable`, `plugin install`, `plugin list`, `plugin remove`, `report html`, `report json`, `root doctor`.

## Smoke Test Matrix

# Smoke Test Matrix

<!-- AUTO-GENERATED FILE. DO NOT EDIT. -->
<!-- Source: unrealmate/registry/command_registry.toml + tests/smoke -->
<!-- Regenerate with: python scripts/sync_docs_from_registry.py -->

Bu dosya stable command metadata ve mevcut smoke test inventory'sinden otomatik uretilir.

## Coverage Summary
- Stable commands in registry: `28`
- Stable commands mapped to smoke tiers: `28`
- Mapped commands with implemented smoke tests: `28`
- Stable commands pending smoke mapping: `0`

## Non-Destructive Stable Commands

| Command | Preconditions | Expected Exit Code | Expected Signal | Risk Level | Automated? |
|---|---|---|---|---|---|
| `python -m unrealmate asset duplicates <fixture_project>/Content` | Fixture Unreal-like project path is required. | `0` | Find and report duplicate assets by name or content hash. | `Medium` | `Yes` |
| `python -m unrealmate asset scan <fixture_project>/Content` | Fixture Unreal-like project path is required. | `0` | Scan directory for Unreal Engine assets and provide a detailed report. | `Medium` | `Yes` |
| `python -m unrealmate build info <fixture_project>` | Fixture Unreal-like project path is required. | `0` | Show build information and recommendations. | `Medium` | `Yes` |
| `python -m unrealmate config edit` | No additional preconditions. | `0` | Opens .unrealmate.toml in the system default editor. | `Medium` | `Yes` |
| `python -m unrealmate config get performance.cache_enabled` | No additional preconditions. | `0` | Get a configuration value. | `Medium` | `Yes` |
| `python -m unrealmate config show` | No additional preconditions. | `0` | Show current configuration. | `Medium` | `Yes` |
| `python -m unrealmate config validate` | No additional preconditions. | `0` | Validates .unrealmate.toml structure and values. | `Medium` | `Yes` |
| `python -m unrealmate performance memory <fixture_project>` | Fixture Unreal-like project path is required. | `0` | Audit memory usage and identify optimization opportunities. | `Medium` | `Yes` |
| `python -m unrealmate performance profile <fixture_project>` | Fixture Unreal-like project path is required. External dependency: profiling-csv-data. | `0` | Analyze performance metrics and detect bottlenecks. | `Medium` | `Yes` |
| `python -m unrealmate performance shaders <fixture_project>` | Fixture Unreal-like project path is required. External dependency: shader-source-files. | `0` | Analyze shader complexity and optimization opportunities. | `Medium` | `Yes` |
| `python -m unrealmate plugin list <fixture_project>` | Fixture Unreal-like project path is required. | `0` | List all installed plugins. | `Medium` | `Yes` |
| `python -m unrealmate doctor` | No additional preconditions. | `0` | Run interactive health checks for the project. | `Medium` | `Yes` |
| `python -m unrealmate version` | No additional preconditions. | `0` | Show system and version information. | `Low` | `Yes` |

## Destructive Stable Commands

| Command | Preconditions | Expected Exit Code | Expected Signal | Risk Level | Automated? |
|---|---|---|---|---|---|
| `python -m unrealmate asset organize <fixture_project>/Content --dry-run --yes` | Run in disposable temp workspace. Fixture Unreal-like project path is required. Use --dry-run for isolated smoke runs. | `0` | Organize assets into proper directory structure based on file types. | `High` | `Yes` |
| `python -m unrealmate build ci-init --platform github --path <fixture_project>` | Run in disposable temp workspace. Fixture Unreal-like project path is required. Use --dry-run for isolated smoke runs. | `0` | Generate CI/CD pipeline configuration. | `High` | `Yes` |
| `python -m unrealmate build docker --path <fixture_project>` | Run in disposable temp workspace. Fixture Unreal-like project path is required. Use --dry-run for isolated smoke runs. | `0` | Generate optimized Dockerfile for Unreal Engine. | `High` | `Yes` |
| `python -m unrealmate config init --force` | Run in disposable temp workspace. | `0` | Initialize .unrealmate.toml configuration file. | `High` | `Yes` |
| `python -m unrealmate config set signature.author "Smoke User"` | Run in disposable temp workspace. | `0` | Set a configuration value. | `High` | `Yes` |
| `python -m unrealmate config template mobile` | Run in disposable temp workspace. Use --dry-run for isolated smoke runs. | `0` | Apply a performance preset template to .unrealmate.toml. | `High` | `Yes` |
| `python -m unrealmate git clean --dry-run --yes` | Run in disposable temp workspace. Use --dry-run for isolated smoke runs. | `0` | Clean build artifacts, intermediate files, and temporary data. | `High` | `Yes` |
| `python -m unrealmate git init --force` | Run in disposable temp workspace. | `0` | Initialize git configuration with optimized settings for Unreal Engine. | `High` | `Yes` |
| `python -m unrealmate git lfs --force` | Run in disposable temp workspace. External dependency: git-lfs. | `0` | Setup Git LFS used for large binary files (assets, maps, etc). | `High` | `Yes (skip if git lfs is unavailable)` |
| `python -m unrealmate plugin disable SmokePlugin --path <fixture_project>` | Run in disposable temp workspace. Fixture Unreal-like project path is required. | `0` | Disable a plugin by editing the local .uproject file only. | `High` | `Yes` |
| `python -m unrealmate plugin enable SmokePlugin --path <fixture_project>` | Run in disposable temp workspace. Fixture Unreal-like project path is required. | `0` | Enable a plugin by editing the local .uproject file only. | `High` | `Yes` |
| `python -m unrealmate plugin install <local_plugin_source> --path <fixture_project> --name SmokePlugin` | Run in disposable temp workspace. Fixture Unreal-like project path is required. External dependency: git-or-local-plugin-source. | `0` | Clone or copy a plugin into the local Plugins directory. | `High` | `Yes` |
| `python -m unrealmate plugin remove SmokePlugin --path <fixture_project> --yes` | Run in disposable temp workspace. Fixture Unreal-like project path is required. | `0` | Delete a local plugin directory; .uproject cleanup stays manual. | `High` | `Yes` |
| `python -m unrealmate report html <fixture_project> --output <temp>/report.html` | Run in disposable temp workspace. Fixture Unreal-like project path is required. | `0` | Generate HTML project report with real stats. | `High` | `Yes` |
| `python -m unrealmate report json <fixture_project> --output <temp>/report.json` | Run in disposable temp workspace. Fixture Unreal-like project path is required. | `0` | Export project stats as JSON (prints or saves to file). | `High` | `Yes` |

## Stable Commands Pending Smoke Mapping

| Command | Preconditions | Expected Exit Code | Expected Signal | Risk Level | Automated? |
|---|---|---|---|---|---|
| - | - | - | - | - | - |

## Safety Notes

- `destructive=true` satirlari sadece disposable fixture/temp workspace'te kosulmalidir.
- `supports_dry_run=true` komutlar smoke kosularinda dry-run ile calistirilmalidir.
- Sistem bagimli testler acik skip nedeni ile calisabilir (`git lfs` gibi).
- UTF-8 guvenli output ortami (`PYTHONIOENCODING=utf-8`) smoke job varsayimi olarak korunmalidir.
