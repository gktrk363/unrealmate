"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        UnrealMate - Team Dashboard                           ║
║                                                                              ║
║  Author: G & E ZYNTH                                                            ║
║  Purpose: Web-based team dashboard for project monitoring                    ║
║  Created: 2026-02-06                                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

Flask-based team dashboard for monitoring Unreal Engine project status.
Displays health metrics, build status, and team activity.

© 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
"""

from unrealmate._version import __version__
import json
import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


@dataclass
class BuildStatus:
    """Represents a build status."""
    status: str  # success, failed, building, pending
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    configuration: str  # Development, Shipping, etc.
    platform: str
    log_path: Optional[str] = None
    error_count: int = 0
    warning_count: int = 0
    
    @property
    def duration(self) -> Optional[timedelta]:
        """Get build duration."""
        if self.started_at and self.finished_at:
            return self.finished_at - self.started_at
        return None
    
    def to_dict(self) -> Dict:
        return {
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "configuration": self.configuration,
            "platform": self.platform,
            "duration_seconds": self.duration.total_seconds() if self.duration else None,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
        }


@dataclass
class TeamMember:
    """Represents a team member."""
    name: str
    email: str
    role: str
    avatar_url: Optional[str] = None
    last_activity: Optional[datetime] = None
    recent_commits: int = 0
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "avatar_url": self.avatar_url,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "recent_commits": self.recent_commits,
        }


@dataclass
class ActivityEvent:
    """Represents a project activity event."""
    id: str
    type: str  # commit, build, issue, merge
    title: str
    description: str
    author: str
    timestamp: datetime
    url: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.type,
            "title": self.title,
            "description": self.description,
            "author": self.author,
            "timestamp": self.timestamp.isoformat(),
            "url": self.url,
        }


@dataclass
class ProjectHealth:
    """Project health metrics."""
    overall_score: float  # 0-100
    build_health: float
    code_quality: float
    test_coverage: float
    asset_health: float
    last_updated: datetime
    issues: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "overall_score": self.overall_score,
            "build_health": self.build_health,
            "code_quality": self.code_quality,
            "test_coverage": self.test_coverage,
            "asset_health": self.asset_health,
            "last_updated": self.last_updated.isoformat(),
            "issues": self.issues,
        }


class DashboardDataProvider:
    """
    Provides data for the team dashboard.
    Collects metrics from various sources.
    """
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self._cache: Dict[str, Any] = {}
        self._cache_expiry: Dict[str, datetime] = {}
    
    def _is_cache_valid(self, key: str, max_age_seconds: int = 60) -> bool:
        """Check if cached data is still valid."""
        if key not in self._cache_expiry:
            return False
        return datetime.now() - self._cache_expiry[key] < timedelta(seconds=max_age_seconds)
    
    def get_project_health(self) -> ProjectHealth:
        """Get current project health metrics."""
        cache_key = "project_health"
        
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        # Calculate health metrics
        build_health = self._calculate_build_health()
        code_quality = self._calculate_code_quality()
        test_coverage = self._get_test_coverage()
        asset_health = self._calculate_asset_health()
        
        overall = (build_health + code_quality + test_coverage + asset_health) / 4
        
        issues = []
        if build_health < 70:
            issues.append("Recent build failures detected")
        if test_coverage < 50:
            issues.append("Test coverage below threshold")
        if asset_health < 60:
            issues.append("Asset issues need attention")
        
        health = ProjectHealth(
            overall_score=overall,
            build_health=build_health,
            code_quality=code_quality,
            test_coverage=test_coverage,
            asset_health=asset_health,
            last_updated=datetime.now(),
            issues=issues,
        )
        
        self._cache[cache_key] = health
        self._cache_expiry[cache_key] = datetime.now()
        
        return health
    
    def _calculate_build_health(self) -> float:
        """Calculate build health score."""
        # Check for recent successful builds
        saved_dir = self.project_path / "Saved" / "Logs"
        if not saved_dir.exists():
            return 80.0  # Default if no logs
        
        log_files = list(saved_dir.glob("*.log"))
        if not log_files:
            return 80.0
        
        # Check most recent log for errors
        latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
        try:
            with open(latest_log, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                error_count = content.lower().count("error")
                if error_count == 0:
                    return 100.0
                elif error_count < 5:
                    return 80.0
                elif error_count < 20:
                    return 60.0
                else:
                    return 40.0
        except Exception:
            return 75.0
    
    def _calculate_code_quality(self) -> float:
        """Calculate code quality score."""
        # Simplified - would integrate with linting tools
        source_dir = self.project_path / "Source"
        if not source_dir.exists():
            return 85.0
        
        cpp_files = list(source_dir.rglob("*.cpp"))
        h_files = list(source_dir.rglob("*.h"))
        
        total_files = len(cpp_files) + len(h_files)
        if total_files == 0:
            return 85.0
        
        # Check for code style issues (simplified)
        issues = 0
        for cpp in cpp_files[:20]:  # Sample check
            try:
                with open(cpp, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # Check for basic issues
                    if "goto" in content:
                        issues += 1
                    if content.count("    ") > 0 and content.count("\t") > 0:
                        issues += 1  # Mixed indentation
            except Exception:
                pass
        
        return max(50.0, 100.0 - issues * 5)
    
    def _get_test_coverage(self) -> float:
        """Get test coverage percentage."""
        # Check for coverage report
        coverage_file = self.project_path / "coverage.json"
        if coverage_file.exists():
            try:
                with open(coverage_file, 'r') as f:
                    data = json.load(f)
                    return data.get("coverage_percent", 60.0)
            except Exception:
                pass
        return 60.0  # Default estimate
    
    def _calculate_asset_health(self) -> float:
        """Calculate asset health score."""
        content_dir = self.project_path / "Content"
        if not content_dir.exists():
            return 90.0
        
        # Check for large assets, missing references, etc.
        large_assets = 0
        for asset in content_dir.rglob("*.uasset"):
            if asset.stat().st_size > 100 * 1024 * 1024:  # > 100MB
                large_assets += 1
        
        score = 100.0 - (large_assets * 5)
        return max(50.0, score)
    
    def get_build_history(self, limit: int = 10) -> List[BuildStatus]:
        """Get recent build history from real log files."""
        builds = []
        saved_dir = self.project_path / "Saved" / "Logs"
        
        if not saved_dir.exists():
            return []
            
        # Parse real logs
        log_files = sorted(list(saved_dir.glob("*.log")), key=lambda f: f.stat().st_mtime, reverse=True)
        
        for log_file in log_files[:limit]:
            try:
                # Basic parsing based on file stats and content
                stats = log_file.stat()
                created_at = datetime.fromtimestamp(stats.st_ctime)
                modified_at = datetime.fromtimestamp(stats.st_mtime)
                
                status = "success"
                error_count = 0
                warning_count = 0
                
                # Read file for status
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().lower()
                    error_count = content.count("error:") + content.count("error ")
                    warning_count = content.count("warning:") + content.count("warning ")
                    
                    if "build successful" in content or "success" in content or "result: 0" in content:
                        status = "success"
                    elif error_count > 0:
                        status = "failed"
                    else:
                        status = "unknown" # Could be a crash or incomplete log

                builds.append(BuildStatus(
                    status=status,
                    started_at=created_at,
                    finished_at=modified_at,
                    configuration="Development", # Assumed, hard to parse without context
                    platform="Win64", # Default
                    error_count=error_count,
                    warning_count=warning_count,
                    log_path=str(log_file.name)
                ))
            except Exception as e:
                logger.error(f"Error parsing log {log_file}: {e}")
        
        return builds
    
    def get_team_members(self) -> List[TeamMember]:
        """Get team member list from git history."""
        members = []
        
        try:
            import subprocess
            # Get authors sorted by commit count
            result = subprocess.run(
                ["git", "shortlog", "-sne", "--all"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    # Format: "   10  Name <email>"
                    parts = line.strip().split("\t")
                    if len(parts) == 2:
                        count = int(parts[0])
                        author_info = parts[1]
                        
                        # Parse "Name <email>"
                        if "<" in author_info:
                            name = author_info.split("<")[0].strip()
                            email = author_info.split("<")[1].strip(">")
                        else:
                            name = author_info
                            email = ""
                        
                        # Clean up name if it looks like an email username
                        if "@" in name:
                            name = name.split("@")[0]
                        
                        members.append(TeamMember(
                            name=name.title(), # Make it look nicer
                            email=email,
                            role="Developer",
                            recent_commits=count,
                            last_activity=datetime.now(), # Git log doesn't give latest date easily here
                        ))
        except Exception as e:
            logger.error(f"Error getting team members: {e}")
        
        return members[:10]
    
    def get_recent_activity(self, limit: int = 20) -> List[ActivityEvent]:
        """Get recent project activity from git log."""
        events = []
        
        try:
            import subprocess
            result = subprocess.run(
                ["git", "log", "--format=%H|%s|%an|%aI", f"-{limit}"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            if result.returncode == 0:
                for i, line in enumerate(result.stdout.strip().split("\n")):
                    parts = line.split("|")
                    if len(parts) >= 4:
                        events.append(ActivityEvent(
                            id=parts[0][:8],
                            type="commit",
                            title=parts[1],
                            description="",
                            author=parts[2].title(), # Fix casing
                            timestamp=datetime.fromisoformat(parts[3]),
                        ))
        except Exception:
            pass
        
        return events


class TeamDashboard:
    """
    Web-based team dashboard server.
    Uses Flask for serving the dashboard.
    """
    
    def __init__(
        self,
        project_path: str,
        port: int = 8080,
        report_core_snapshot: Optional[Dict[str, Any]] = None,
    ):
        self.project_path = Path(project_path).resolve()
        self.port = port
        self.data_provider = DashboardDataProvider(project_path)
        self.report_core_snapshot = report_core_snapshot or {}
        self._server_thread: Optional[threading.Thread] = None
        self._app = None
    
    def _create_app(self):
        """Create Flask application."""
        try:
            from flask import Flask, jsonify, render_template_string
        except ImportError:
            logger.error("Flask not installed. Install with: pip install flask")
            return None
        
        app = Flask(__name__)
        
        # Dashboard HTML template
        DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UnrealMate Project Dashboard</title>
    <style>
        :root {
            --bg: #091119;
            --bg-elevated: #101b24;
            --surface: rgba(15, 25, 34, 0.94);
            --surface-strong: rgba(18, 31, 41, 0.98);
            --border: rgba(160, 186, 201, 0.16);
            --text: #edf5fa;
            --muted: #8ba2b2;
            --accent: #49d3a5;
            --accent-soft: rgba(73, 211, 165, 0.14);
            --warning: #ffbe5b;
            --danger: #ff7d78;
            --success: #6ce0a7;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            min-height: 100vh;
            font-family: "Aptos", "Segoe UI Variable", "Segoe UI", sans-serif;
            color: var(--text);
            background:
                radial-gradient(circle at top left, rgba(73, 211, 165, 0.16), transparent 26%),
                radial-gradient(circle at top right, rgba(92, 169, 255, 0.14), transparent 24%),
                linear-gradient(180deg, #081017 0%, #0d1620 55%, #091119 100%);
            line-height: 1.5;
        }

        .shell {
            max-width: 1400px;
            margin: 0 auto;
            padding: 28px 24px 42px;
        }

        .hero, .panel {
            border: 1px solid var(--border);
            border-radius: 26px;
            background: linear-gradient(180deg, var(--surface-strong) 0%, var(--surface) 100%);
            box-shadow: 0 20px 48px rgba(0, 0, 0, 0.22);
        }

        .hero {
            padding: 30px;
            position: relative;
            overflow: hidden;
        }

        .hero::after {
            content: "";
            position: absolute;
            inset: auto -100px -120px auto;
            width: 320px;
            height: 320px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(92, 169, 255, 0.12), transparent 68%);
            pointer-events: none;
        }

        .hero-top, .panel-head {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 20px;
        }

        .eyebrow, .label {
            color: var(--muted);
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.14em;
        }

        h1 {
            margin-top: 8px;
            font-size: clamp(2rem, 3vw, 3.1rem);
            line-height: 1.05;
            letter-spacing: -0.03em;
        }

        .subtitle {
            margin-top: 10px;
            font-size: 1rem;
            color: #d7e5ee;
        }

        .support-copy, .panel-copy, .muted {
            color: var(--muted);
        }

        .support-copy {
            max-width: 760px;
            margin-top: 12px;
        }

        .badges {
            display: flex;
            flex-wrap: wrap;
            justify-content: flex-end;
            gap: 10px;
        }

        .badge, .status-badge, .chip {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 8px 12px;
            border-radius: 999px;
            border: 1px solid transparent;
            font-size: 0.8rem;
            font-weight: 700;
        }

        .badge.experimental { background: rgba(255, 190, 91, 0.14); color: #ffd391; border-color: rgba(255, 190, 91, 0.2); }
        .badge.secondary { background: rgba(92, 169, 255, 0.13); color: #b9dbff; border-color: rgba(92, 169, 255, 0.18); }
        .badge.snapshot { background: rgba(73, 211, 165, 0.12); color: #b4efd8; border-color: rgba(73, 211, 165, 0.2); }
        .badge.snapshot-unavailable { background: rgba(255, 125, 120, 0.12); color: #ffc5c1; border-color: rgba(255, 125, 120, 0.2); }

        .meta-grid, .metric-grid, .report-grid {
            display: grid;
            gap: 14px;
        }

        .meta-grid {
            grid-template-columns: repeat(4, minmax(0, 1fr));
            margin-top: 24px;
        }

        .meta, .metric, .report-stat, .note, .empty {
            border-radius: 18px;
            border: 1px solid rgba(160, 186, 201, 0.1);
            background: rgba(255, 255, 255, 0.03);
        }

        .meta, .metric, .report-stat { padding: 16px 18px; }

        .meta strong, .metric strong, .report-stat strong {
            display: block;
            margin-top: 8px;
            font-size: 1rem;
            color: var(--text);
            word-break: break-word;
        }

        .layout {
            display: grid;
            grid-template-columns: repeat(12, minmax(0, 1fr));
            gap: 18px;
            margin-top: 22px;
        }

        .panel { padding: 24px; }
        .span-12 { grid-column: span 12; }
        .span-7 { grid-column: span 7; }
        .span-6 { grid-column: span 6; }
        .span-5 { grid-column: span 5; }

        .panel-title {
            margin-top: 6px;
            font-size: 1.35rem;
            letter-spacing: -0.02em;
        }

        .panel-copy { margin-top: 6px; max-width: 700px; }

        .health-layout {
            display: grid;
            grid-template-columns: 210px 1fr;
            gap: 22px;
            margin-top: 18px;
        }

        .score-ring {
            --ring-color: var(--accent);
            width: 190px;
            height: 190px;
            margin: 4px auto 0;
            border-radius: 50%;
            display: grid;
            place-items: center;
            background:
                radial-gradient(circle at 50% 50%, rgba(9, 17, 25, 0.96) 60%, transparent 61%),
                conic-gradient(var(--ring-color) calc(var(--score) * 1%), rgba(255, 255, 255, 0.06) 0);
        }

        .score-ring.score-warn { --ring-color: var(--warning); }
        .score-ring.score-bad { --ring-color: var(--danger); }
        .score-inner { text-align: center; }
        .score-value { display: block; font-size: 2.9rem; font-weight: 700; line-height: 1; letter-spacing: -0.04em; }
        .score-caption { display: block; margin-top: 10px; color: var(--muted); font-size: 0.88rem; }

        .metric-grid, .report-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); margin-top: 4px; }
        .metric strong, .report-stat strong { font-size: 1.9rem; line-height: 1; }

        .note, .empty {
            margin-top: 18px;
            padding: 16px 18px;
        }

        .note {
            border-left: 3px solid var(--accent);
            background: var(--accent-soft);
        }

        .attention-warning .title { color: var(--warning); }
        .attention-good .title { color: var(--success); }
        .title { display: block; margin-bottom: 10px; font-weight: 700; }
        .issues { padding-left: 18px; }
        .issues li + li { margin-top: 8px; }

        .rows { margin-top: 12px; }
        .row {
            display: grid;
            grid-template-columns: auto 1fr auto;
            gap: 16px;
            align-items: center;
            padding: 15px 0;
            border-bottom: 1px solid rgba(160, 186, 201, 0.12);
        }

        .row:last-child { border-bottom: none; }
        .icon {
            width: 42px;
            height: 42px;
            display: grid;
            place-items: center;
            border-radius: 14px;
            background: rgba(255, 255, 255, 0.04);
            color: #d5e3ec;
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }

        .row-title { display: block; font-weight: 600; }
        .row-sub { display: block; margin-top: 5px; color: var(--muted); font-size: 0.92rem; }
        .row-meta { min-width: 130px; text-align: right; }

        .status-success { background: rgba(108, 224, 167, 0.14); color: #bbf2d3; border-color: rgba(108, 224, 167, 0.18); }
        .status-failed { background: rgba(255, 125, 120, 0.14); color: #ffc1bd; border-color: rgba(255, 125, 120, 0.18); }
        .status-warning { background: rgba(255, 190, 91, 0.14); color: #ffd79f; border-color: rgba(255, 190, 91, 0.18); }
        .status-muted { background: rgba(255, 255, 255, 0.05); color: #dbe6ec; border-color: rgba(255, 255, 255, 0.08); }

        .chip {
            background: rgba(255, 255, 255, 0.05);
            border-color: rgba(255, 255, 255, 0.08);
            color: #d8e4eb;
            font-family: Consolas, "SFMono-Regular", monospace;
            font-size: 0.82rem;
        }

        .footer {
            margin-top: 22px;
            padding-top: 6px;
            text-align: center;
            color: var(--muted);
        }

        .footer strong { color: var(--text); }
        .footer-sub { margin-top: 6px; font-size: 0.92rem; }

        @media (max-width: 1080px) {
            .meta-grid, .layout { grid-template-columns: repeat(2, minmax(0, 1fr)); }
            .span-7, .span-6, .span-5, .span-12 { grid-column: span 2; }
            .health-layout { grid-template-columns: 1fr; }
        }

        @media (max-width: 760px) {
            .shell { padding: 18px 16px 32px; }
            .hero, .panel { padding: 20px; }
            .hero-top, .panel-head, .row { display: block; }
            .badges { justify-content: flex-start; margin-top: 16px; }
            .meta-grid, .layout, .metric-grid, .report-grid { grid-template-columns: 1fr; }
            .span-7, .span-6, .span-5, .span-12 { grid-column: span 1; }
            .row-meta { margin-top: 10px; text-align: left; min-width: 0; }
        }
    </style>
</head>
<body>
    <main class="shell">
        <section class="hero">
            <div class="hero-top">
                <div>
                    <span class="eyebrow">UnrealMate CLI</span>
                    <h1>Project Dashboard</h1>
                    <p class="subtitle">Visual snapshot for {{ project_name }}</p>
                    <p class="support-copy">Use report json or report html when you need stable local report artifacts.</p>
                </div>
                <div class="badges">
                    <span class="badge experimental">Experimental</span>
                    <span class="badge secondary">CLI-launched secondary surface</span>
                </div>
            </div>

            <div class="meta-grid">
                <div class="meta">
                    <span class="label">Project path</span>
                    <strong>{{ project_path_label }}</strong>
                </div>
                <div class="meta">
                    <span class="label">Last health refresh</span>
                    <strong>{{ health_updated_label }}</strong>
                </div>
                <div class="meta">
                    <span class="label">Refresh behavior</span>
                    <strong>Auto-refresh every 30s</strong>
                </div>
                <div class="meta">
                    <span class="label">Report snapshot</span>
                    <strong>
                        <span class="badge {% if report_snapshot_available %}snapshot{% else %}snapshot-unavailable{% endif %}">
                            {% if report_snapshot_available %}Local report snapshot available{% else %}Local report snapshot unavailable{% endif %}
                        </span>
                    </strong>
                </div>
            </div>
        </section>

        <section class="layout">
            <article class="panel span-7">
                <div class="panel-head">
                    <div>
                        <span class="label">Local health</span>
                        <h2 class="panel-title">Health Overview</h2>
                        <p class="panel-copy">High-level project health from local build, code, test, and asset signals.</p>
                    </div>
                </div>
                <div class="health-layout">
                    <div class="score-ring {{ health_class }}" style="--score: {{ health_score }};">
                        <div class="score-inner">
                            <span class="score-value">{{ health_score }}%</span>
                            <span class="score-caption">Overall score</span>
                        </div>
                    </div>
                    <div>
                        <div class="metric-grid">
                            <div class="metric"><span class="label">Builds</span><strong>{{ build_health }}%</strong></div>
                            <div class="metric"><span class="label">Code</span><strong>{{ code_quality }}%</strong></div>
                            <div class="metric"><span class="label">Tests</span><strong>{{ test_coverage }}%</strong></div>
                            <div class="metric"><span class="label">Assets</span><strong>{{ asset_health }}%</strong></div>
                        </div>
                        <div class="note {% if health_issues %}attention-warning{% else %}attention-good{% endif %}">
                            <span class="title">{% if health_issues %}Attention needed{% else %}Health status looks steady{% endif %}</span>
                            {% if health_issues %}
                            <ul class="issues">
                                {% for issue in health_issues %}
                                <li>{{ issue }}</li>
                                {% endfor %}
                            </ul>
                            {% else %}
                            <p>No urgent issues surfaced by current local health checks.</p>
                            {% endif %}
                        </div>
                    </div>
                </div>
            </article>

            <article class="panel span-5">
                <div class="panel-head">
                    <div>
                        <span class="label">Artifact relationship</span>
                        <h2 class="panel-title">Report Snapshot</h2>
                        <p class="panel-copy">This dashboard is a secondary visual surface over the same local project data used for stable exports.</p>
                    </div>
                </div>
                {% if report_snapshot_available %}
                <p class="panel-copy">Generated from local report data</p>
                <p class="muted" style="margin-top: 8px;">Generated {{ report_generated_label }}</p>
                <div class="report-grid">
                    <div class="report-stat"><span class="label">UProject files</span><strong>{{ report_stats.uproject_files }}</strong></div>
                    <div class="report-stat"><span class="label">C++ source</span><strong>{{ report_stats.cpp_source_files }}</strong></div>
                    <div class="report-stat"><span class="label">Blueprint assets</span><strong>{{ report_stats.blueprint_assets }}</strong></div>
                    <div class="report-stat"><span class="label">Scene maps</span><strong>{{ report_stats.scene_maps }}</strong></div>
                </div>
                <div class="note">This dashboard is a secondary visual surface over the same local project data used for report exports.</div>
                {% else %}
                <div class="empty">Local report snapshot is unavailable for this run. Use report json or report html for stable local report artifacts.</div>
                {% endif %}
            </article>

            <article class="panel span-6">
                <div class="panel-head">
                    <div>
                        <span class="label">Build history</span>
                        <h2 class="panel-title">Recent Builds</h2>
                        <p class="panel-copy">Recent local build outcomes from project logs.</p>
                    </div>
                </div>
                {% if has_builds %}
                <div class="rows">
                    {% for build in build_rows %}
                    <div class="row">
                        <div class="icon">{{ build.status_short }}</div>
                        <div>
                            <span class="row-title">{{ build.configuration }} / {{ build.platform }}</span>
                            <span class="row-sub">{{ build.error_count }} errors • {{ build.warning_count }} warnings • {{ build.duration_label }}</span>
                        </div>
                        <div class="row-meta"><span class="status-badge {{ build.status_class }}">{{ build.status_label }}</span></div>
                    </div>
                    {% endfor %}
                </div>
                {% else %}
                <div class="empty">No recent build logs were found in this project.</div>
                {% endif %}
            </article>

            <article class="panel span-6">
                <div class="panel-head">
                    <div>
                        <span class="label">Git insight</span>
                        <h2 class="panel-title">Team Activity</h2>
                        <p class="panel-copy">Recent contribution signals derived from local git history.</p>
                    </div>
                </div>
                {% if has_team %}
                <div class="rows">
                    {% for member in team_rows %}
                    <div class="row">
                        <div class="icon">{{ member.initials }}</div>
                        <div>
                            <span class="row-title">{{ member.name }}</span>
                            <span class="row-sub">{{ member.role }} • {{ member.last_activity_label }}</span>
                        </div>
                        <div class="row-meta">
                            <div style="font-size: 1.35rem; font-weight: 700;">{{ member.recent_commits }}</div>
                            <div class="muted" style="font-size: 0.84rem; margin-top: 4px;">Recent commits</div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
                {% else %}
                <div class="empty">No team activity was detected from local git history.</div>
                {% endif %}
            </article>

            <article class="panel span-12">
                <div class="panel-head">
                    <div>
                        <span class="label">Recent commits</span>
                        <h2 class="panel-title">Recent Activity</h2>
                        <p class="panel-copy">Latest local git events visible from the current project checkout.</p>
                    </div>
                </div>
                {% if has_activity %}
                <div class="rows">
                    {% for event in activity_rows %}
                    <div class="row">
                        <div class="icon">{{ event.type_short }}</div>
                        <div>
                            <span class="row-title">{{ event.title }}</span>
                            <span class="row-sub">by {{ event.author }} • {{ event.timestamp_label }}</span>
                        </div>
                        <div class="row-meta"><span class="chip">{{ event.id }}</span></div>
                    </div>
                    {% endfor %}
                </div>
                {% else %}
                <div class="empty">No recent git activity was found for this project yet.</div>
                {% endif %}
            </article>
        </section>

        <footer class="footer">
            <div>Experimental local dashboard • Powered by UnrealMate CLI</div>
            <div class="footer-sub">Secondary visual surface for local project data</div>
        </footer>
    </main>

    <script>
        setTimeout(() => location.reload(), 30000);
    </script>
</body>
</html>
        """
        
        def _format_datetime_label(value: Optional[datetime]) -> str:
            if value is None:
                return "Unavailable"
            return value.strftime("%Y-%m-%d %H:%M:%S")

        def _format_iso_label(value: Optional[str]) -> str:
            if not value:
                return "Unavailable"
            try:
                return datetime.fromisoformat(value).strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                return value

        def _format_duration_label(seconds: Optional[float]) -> str:
            if seconds is None:
                return "Duration unavailable"
            total_seconds = max(int(seconds), 0)
            minutes, secs = divmod(total_seconds, 60)
            hours, minutes = divmod(minutes, 60)
            if hours:
                return f"{hours}h {minutes}m {secs}s"
            if minutes:
                return f"{minutes}m {secs}s"
            return f"{secs}s"

        @app.route('/')
        def dashboard():
            health = self.data_provider.get_project_health()
            builds = self.data_provider.get_build_history(5)
            team = self.data_provider.get_team_members()
            activity = self.data_provider.get_recent_activity(10)

            health_score = int(health.overall_score)
            health_class = "score-good" if health.overall_score >= 70 else ("score-warn" if health.overall_score >= 50 else "score-bad")
            project_name = self.report_core_snapshot.get("project_name") or self.project_path.name
            project_path_label = self.report_core_snapshot.get("project_path") or str(self.project_path)

            report_stats_source = self.report_core_snapshot.get("stats") or {}
            report_stats = {
                "uproject_files": int(report_stats_source.get("uproject_files", 0) or 0),
                "cpp_source_files": int(report_stats_source.get("cpp_source_files", 0) or 0),
                "blueprint_assets": int(report_stats_source.get("blueprint_assets", 0) or 0),
                "scene_maps": int(report_stats_source.get("scene_maps", 0) or 0),
            }
            report_snapshot_available = bool(self.report_core_snapshot)

            status_map = {
                "success": ("status-success", "success", "ok"),
                "failed": ("status-failed", "failed", "fail"),
                "building": ("status-warning", "building", "run"),
                "pending": ("status-warning", "pending", "wait"),
                "unknown": ("status-muted", "unknown", "unk"),
            }

            build_rows = []
            for build in builds:
                build_dict = build.to_dict()
                status_class, status_label, status_short = status_map.get(
                    build_dict["status"],
                    ("status-muted", build_dict["status"], build_dict["status"][:3].upper()),
                )
                build_rows.append(
                    {
                        **build_dict,
                        "status_class": status_class,
                        "status_label": status_label,
                        "status_short": status_short,
                        "duration_label": _format_duration_label(build_dict.get("duration_seconds")),
                    }
                )

            team_rows = []
            for member in team:
                member_dict = member.to_dict()
                name = member_dict.get("name") or "Unknown"
                initials = "".join(part[:1] for part in name.split()[:2]).upper() or "NA"
                team_rows.append(
                    {
                        **member_dict,
                        "initials": initials,
                        "last_activity_label": _format_iso_label(member_dict.get("last_activity")),
                    }
                )

            activity_rows = []
            for event in activity:
                event_dict = event.to_dict()
                activity_rows.append(
                    {
                        **event_dict,
                        "type_short": (event_dict.get("type") or "act")[:3].upper(),
                        "timestamp_label": _format_iso_label(event_dict.get("timestamp")),
                    }
                )

            return render_template_string(
                DASHBOARD_HTML,
                project_name=project_name,
                project_path_label=project_path_label,
                health_score=health_score,
                health_class=health_class,
                health_updated_label=_format_datetime_label(health.last_updated),
                build_health=int(health.build_health),
                code_quality=int(health.code_quality),
                test_coverage=int(health.test_coverage),
                asset_health=int(health.asset_health),
                health_issues=health.issues,
                report_snapshot_available=report_snapshot_available,
                report_generated_label=_format_iso_label(self.report_core_snapshot.get("generated_at_iso")),
                report_stats=report_stats,
                has_builds=bool(build_rows),
                has_team=bool(team_rows),
                has_activity=bool(activity_rows),
                build_rows=build_rows,
                team_rows=team_rows,
                activity_rows=activity_rows,
            )
        
        @app.route('/api/health')
        def api_health():
            payload = self.data_provider.get_project_health().to_dict()
            if self.report_core_snapshot:
                payload["report_core"] = {
                    "project_name": self.report_core_snapshot.get("project_name"),
                    "project_path": self.report_core_snapshot.get("project_path"),
                    "generated_at_iso": self.report_core_snapshot.get("generated_at_iso"),
                    "stats": self.report_core_snapshot.get("stats"),
                    "config_snapshot": self.report_core_snapshot.get("config_snapshot"),
                }
            return jsonify(payload)
        
        @app.route('/api/builds')
        def api_builds():
            return jsonify([b.to_dict() for b in self.data_provider.get_build_history()])
        
        @app.route('/api/team')
        def api_team():
            return jsonify([m.to_dict() for m in self.data_provider.get_team_members()])
        
        @app.route('/api/activity')
        def api_activity():
            return jsonify([e.to_dict() for e in self.data_provider.get_recent_activity()])
        
        return app
    
    def start(self, open_browser: bool = True) -> bool:
        """Start the dashboard server."""
        self._app = self._create_app()
        if not self._app:
            return False
        
        def run_server():
            self._app.run(host='127.0.0.1', port=self.port, debug=False, use_reloader=False)
        
        self._server_thread = threading.Thread(target=run_server, daemon=True)
        self._server_thread.start()
        
        url = f"http://127.0.0.1:{self.port}"
        logger.info(f"Dashboard started at: {url}")
        
        if open_browser:
            import webbrowser
            webbrowser.open(url)
        
        return True
    
    def stop(self) -> None:
        """Stop the dashboard server."""
        # Flask doesn't have a clean shutdown mechanism in simple mode
        # The thread is daemon so it will stop when main thread exits
        logger.info("Dashboard server stopping...")



# Developer signature
DEVELOPER_SIGNATURE = "G & E ZYNTH"
MODULE_VERSION = __version__

