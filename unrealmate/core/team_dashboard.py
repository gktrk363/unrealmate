"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        UnrealMate - Team Dashboard                           ║
║                                                                              ║
║  Author: gktrk363                                                            ║
║  Purpose: Web-based team dashboard for project monitoring                    ║
║  Created: 2026-02-06                                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

Flask-based team dashboard for monitoring Unreal Engine project status.
Displays health metrics, build status, and team activity.

© 2026 gktrk363 - Crafted with passion for Unreal Engine developers
"""

import os
import json
import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable

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
        except:
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
            except:
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
            except:
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
        except:
            pass
        
        return events


class TeamDashboard:
    """
    Web-based team dashboard server.
    Uses Flask for serving the dashboard.
    """
    
    def __init__(self, project_path: str, port: int = 8080):
        self.project_path = Path(project_path).resolve()
        self.port = port
        self.data_provider = DashboardDataProvider(project_path)
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
        # Dashboard HTML template - Premium Design
        DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UnrealMate Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #00ff88;
            --primary-glow: rgba(0, 255, 136, 0.4);
            --bg-dark: #0a0a12;
            --card-bg: rgba(255, 255, 255, 0.03);
            --card-border: rgba(255, 255, 255, 0.05);
            --text-main: #ffffff;
            --text-muted: #8899a6;
            --danger: #ff4444;
            --warning: #ffaa00;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body { 
            font-family: 'Outfit', sans-serif;
            background-color: var(--bg-dark);
            background-image: 
                radial-gradient(circle at 10% 20%, rgba(0, 255, 136, 0.1) 0%, transparent 20%),
                radial-gradient(circle at 90% 80%, rgba(0, 100, 255, 0.1) 0%, transparent 20%);
            color: var(--text-main);
            min-height: 100vh;
            padding-bottom: 40px;
        }

        .navbar {
            background: rgba(10, 10, 18, 0.8);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid var(--card-border);
            padding: 1.5rem 2rem;
            position: sticky;
            top: 0;
            z-index: 100;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .brand {
            font-size: 1.5rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .brand-icon {
            color: var(--primary);
            filter: drop-shadow(0 0 10px var(--primary-glow));
        }

        .project-badge {
            background: rgba(255, 255, 255, 0.05);
            padding: 0.5rem 1rem;
            border-radius: 50px;
            font-size: 0.9rem;
            border: 1px solid var(--card-border);
            color: var(--text-muted);
        }
        
        .project-badge strong { color: var(--text-main); }

        .container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 2rem;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 2rem;
        }

        .card {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 20px;
            padding: 2rem;
            backdrop-filter: blur(10px);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            border-color: rgba(255, 255, 255, 0.1);
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
        }

        .card-title {
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--text-main);
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .status-orb {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--primary);
            box-shadow: 0 0 10px var(--primary);
        }

        .big-score {
            font-size: 4rem;
            font-weight: 700;
            text-align: center;
            margin: 1rem 0;
            background: linear-gradient(135deg, #fff 0%, #888 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
            margin-top: 1rem;
        }

        .metric-item {
            background: rgba(0, 0, 0, 0.2);
            padding: 1rem;
            border-radius: 12px;
            text-align: center;
        }

        .metric-value {
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--primary);
            display: block;
        }
        
        .metric-label {
            font-size: 0.85rem;
            color: var(--text-muted);
            margin-top: 5px;
            display: block;
        }

        .list-item {
            display: flex;
            align-items: center;
            padding: 1rem 0;
            border-bottom: 1px solid var(--card-border);
        }

        .list-item:last-child { border-bottom: none; }

        .item-icon {
            width: 40px;
            height: 40px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 15px;
            font-size: 1.2rem;
        }

        .item-content { flex: 1; }
        
        .item-title { display: block; font-weight: 600; margin-bottom: 4px; }
        .item-sub { display: block; font-size: 0.85rem; color: var(--text-muted); }

        .status-badge {
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .status-success { background: rgba(0, 255, 136, 0.15); color: var(--primary); }
        .status-failed { background: rgba(255, 68, 68, 0.15); color: var(--danger); }

        .footer {
            text-align: center;
            margin-top: 4rem;
            color: var(--text-muted);
            font-size: 0.9rem;
        }

        .animate-pulse { animation: pulse 2s infinite; }
        
        @keyframes pulse {
            0% { opacity: 0.6; }
            50% { opacity: 1; }
            100% { opacity: 0.6; }
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="brand">
            <span class="brand-icon">⚡</span>
            UnrealMate
        </div>
        <div class="project-badge">
            Project: <strong>{{ project_name }}</strong>
        </div>
    </nav>

    <div class="container">
        <div class="grid">
            <!-- Health Card -->
            <div class="card">
                <div class="card-header">
                    <div class="card-title">
                        <span class="status-orb animate-pulse"></span>
                        Project Health
                    </div>
                </div>
                <div class="big-score">{{ health_score }}%</div>
                <div class="metrics-grid">
                    <div class="metric-item">
                        <span class="metric-value">{{ build_health }}%</span>
                        <span class="metric-label">Builds</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-value">{{ code_quality }}%</span>
                        <span class="metric-label">Code</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-value">{{ test_coverage }}%</span>
                        <span class="metric-label">Tests</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-value">{{ asset_health }}%</span>
                        <span class="metric-label">Assets</span>
                    </div>
                </div>
            </div>

            <!-- Builds Card -->
            <div class="card">
                <div class="card-header">
                    <div class="card-title">🚀 Recent Builds</div>
                </div>
                {% for build in builds %}
                <div class="list-item">
                    <div class="item-icon">
                        {% if build.status == 'success' %}✅{% else %}❌{% endif %}
                    </div>
                    <div class="item-content">
                        <span class="item-title">{{ build.configuration }} - {{ build.platform }}</span>
                        <span class="item-sub">{{ build.error_count }} errors • {{ build.warning_count }} warnings</span>
                    </div>
                    <span class="status-badge status-{{ build.status }}">{{ build.status }}</span>
                </div>
                {% endfor %}
            </div>

            <!-- Team Card -->
            <div class="card">
                <div class="card-header">
                    <div class="card-title">👥 Team Members</div>
                </div>
                {% for member in team %}
                <div class="list-item">
                    <div class="item-icon">👤</div>
                    <div class="item-content">
                        <span class="item-title">{{ member.name }}</span>
                        <span class="item-sub">{{ member.role }}</span>
                    </div>
                    <div style="text-align: right">
                        <span class="metric-value" style="font-size: 1.1rem">{{ member.recent_commits }}</span>
                        <span class="metric-label">commits</span>
                    </div>
                </div>
                {% endfor %}
            </div>
            
            <!-- Activity Card -->
            <div class="card" style="grid-column: 1 / -1">
                <div class="card-header">
                    <div class="card-title">📋 Activity Feed</div>
                </div>
                {% for event in activity %}
                <div class="list-item">
                    <div class="item-icon">📝</div>
                    <div class="item-content">
                        <span class="item-title">{{ event.title }}</span>
                        <span class="item-sub">by {{ event.author }} • {{ event.timestamp }}</span>
                    </div>
                    <span class="status-badge" style="background: rgba(255,255,255,0.05); color: #fff; font-family: monospace">
                        {{ event.id }}
                    </span>
                </div>
                {% endfor %}
            </div>
        </div>

        <div class="footer">
            Powered by <strong>UnrealMate CLI</strong> • Developed by <strong>gktrk363</strong>
        </div>
    </div>

    <script>
        setTimeout(() => location.reload(), 30000);
    </script>
</body>
</html>
        """
        
        @app.route('/')
        def dashboard():
            health = self.data_provider.get_project_health()
            builds = self.data_provider.get_build_history(5)
            team = self.data_provider.get_team_members()
            activity = self.data_provider.get_recent_activity(10)
            
            health_class = "score-good" if health.overall_score >= 70 else ("score-warn" if health.overall_score >= 50 else "score-bad")
            
            # Use folder name as project name
            project_name = self.project_path.name

            return render_template_string(
                DASHBOARD_HTML,
                project_name=project_name,
                health_score=int(health.overall_score),
                health_class=health_class,
                build_health=int(health.build_health),
                code_quality=int(health.code_quality),
                test_coverage=int(health.test_coverage),
                asset_health=int(health.asset_health),
                builds=[b.to_dict() for b in builds],
                team=[m.to_dict() for m in team],
                activity=[e.to_dict() for e in activity],
            )
        
        @app.route('/api/health')
        def api_health():
            return jsonify(self.data_provider.get_project_health().to_dict())
        
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
DEVELOPER_SIGNATURE = "gktrk363"
MODULE_VERSION = "1.0.0"
