"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    UnrealMate - Web Dashboard                                ║
║                                                                              ║
║  Author: G & E ZYNTH                                                            ║
║  GitHub: https://github.com/gktrk363/unrealmate                              ║
║  Purpose: Web-based dashboard for project analytics                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

© 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
"""

from __future__ import annotations

import http.server
import socketserver
import threading
import webbrowser
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from rich.console import Console

console = Console()


@dataclass
class DashboardData:
    """Data structure for dashboard display."""
    project_name: str = "UnrealMate Project"
    project_path: str = ""
    last_scan: str = ""
    assets: dict[str, Any] = None
    blueprints: dict[str, Any] = None
    performance: dict[str, Any] = None
    git_status: dict[str, Any] = None

    def __post_init__(self):
        self.assets = self.assets or {}
        self.blueprints = self.blueprints or {}
        self.performance = self.performance or {}
        self.git_status = self.git_status or {}


class DashboardServer:
    """Simple HTTP server for the web dashboard."""

    def __init__(self, data: DashboardData, port: int = 8080):
        self.data = data
        self.port = port
        self.server: Optional[socketserver.TCPServer] = None
        self.thread: Optional[threading.Thread] = None

    def generate_html(self) -> str:
        """Generate the dashboard HTML."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UnrealMate Dashboard</title>
    <style>
        :root {{
            --primary: #00d4ff;
            --secondary: #ff00ff;
            --success: #00ff88;
            --warning: #ffcc00;
            --error: #ff4444;
            --bg: #0a0a0a;
            --card-bg: #1a1a2e;
            --text: #ffffff;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
        }}
        .header {{
            background: linear-gradient(135deg, var(--card-bg), #16213e);
            padding: 2rem;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        .header h1 {{
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5rem;
        }}
        .header p {{ color: #888; margin-top: 0.5rem; }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-top: 2rem;
        }}
        .card {{
            background: var(--card-bg);
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid rgba(255,255,255,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 32px rgba(0,212,255,0.1);
        }}
        .card h2 {{
            color: var(--primary);
            font-size: 1.2rem;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .stat {{
            display: flex;
            justify-content: space-between;
            padding: 0.75rem 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }}
        .stat:last-child {{ border-bottom: none; }}
        .stat-label {{ color: #888; }}
        .stat-value {{ font-weight: bold; color: var(--success); }}
        .stat-value.warning {{ color: var(--warning); }}
        .stat-value.error {{ color: var(--error); }}
        .progress-bar {{
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            height: 8px;
            margin-top: 0.5rem;
            overflow: hidden;
        }}
        .progress-fill {{
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            height: 100%;
            border-radius: 10px;
            transition: width 0.5s ease;
        }}
        .badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: bold;
        }}
        .badge.success {{ background: rgba(0,255,136,0.2); color: var(--success); }}
        .badge.warning {{ background: rgba(255,204,0,0.2); color: var(--warning); }}
        .badge.error {{ background: rgba(255,68,68,0.2); color: var(--error); }}
        .footer {{
            text-align: center;
            padding: 2rem;
            color: #666;
            border-top: 1px solid rgba(255,255,255,0.1);
            margin-top: 2rem;
        }}
        .footer a {{ color: var(--primary); text-decoration: none; }}
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        .live {{ animation: pulse 2s infinite; color: var(--success); }}
    </style>
</head>
<body>
    <header class="header">
        <h1>🎮 UnrealMate Dashboard</h1>
        <p>Project: {self.data.project_name} | Last scan: {self.data.last_scan or 'Never'}</p>
    </header>

    <div class="container">
        <div class="grid">
            <!-- Project Overview -->
            <div class="card">
                <h2>📁 Project Overview</h2>
                <div class="stat">
                    <span class="stat-label">Project Path</span>
                    <span class="stat-value">{self.data.project_path or 'Not set'}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Status</span>
                    <span class="badge success">● Active</span>
                </div>
            </div>

            <!-- Assets -->
            <div class="card">
                <h2>📦 Assets</h2>
                <div class="stat">
                    <span class="stat-label">Total Assets</span>
                    <span class="stat-value">{self.data.assets.get('total', 0)}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Textures</span>
                    <span class="stat-value">{self.data.assets.get('textures', 0)}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Meshes</span>
                    <span class="stat-value">{self.data.assets.get('meshes', 0)}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Materials</span>
                    <span class="stat-value">{self.data.assets.get('materials', 0)}</span>
                </div>
            </div>

            <!-- Blueprints -->
            <div class="card">
                <h2>📊 Blueprints</h2>
                <div class="stat">
                    <span class="stat-label">Total Blueprints</span>
                    <span class="stat-value">{self.data.blueprints.get('total', 0)}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Complex</span>
                    <span class="stat-value warning">{self.data.blueprints.get('complex', 0)}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Average Nodes</span>
                    <span class="stat-value">{self.data.blueprints.get('avg_nodes', 0)}</span>
                </div>
            </div>

            <!-- Performance -->
            <div class="card">
                <h2>⚡ Performance</h2>
                <div class="stat">
                    <span class="stat-label">Health Score</span>
                    <span class="stat-value">{self.data.performance.get('score', 'N/A')}</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {self.data.performance.get('score_percent', 0)}%"></div>
                </div>
                <div class="stat" style="margin-top: 1rem;">
                    <span class="stat-label">Issues Found</span>
                    <span class="stat-value {'error' if self.data.performance.get('issues', 0) > 5 else 'warning' if self.data.performance.get('issues', 0) > 0 else ''}">{self.data.performance.get('issues', 0)}</span>
                </div>
            </div>

            <!-- Git Status -->
            <div class="card">
                <h2>🔧 Git Status</h2>
                <div class="stat">
                    <span class="stat-label">Branch</span>
                    <span class="stat-value">{self.data.git_status.get('branch', 'N/A')}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Modified Files</span>
                    <span class="stat-value">{self.data.git_status.get('modified', 0)}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">LFS Enabled</span>
                    <span class="badge {'success' if self.data.git_status.get('lfs', False) else 'warning'}">{'Yes' if self.data.git_status.get('lfs', False) else 'No'}</span>
                </div>
            </div>

            <!-- Quick Actions -->
            <div class="card">
                <h2>🚀 Quick Actions</h2>
                <p style="color: #888; line-height: 1.6;">
                    Run these commands in your terminal:<br><br>
                    <code style="background: rgba(255,255,255,0.1); padding: 0.25rem 0.5rem; border-radius: 4px;">unrealmate asset scan</code><br><br>
                    <code style="background: rgba(255,255,255,0.1); padding: 0.25rem 0.5rem; border-radius: 4px;">unrealmate bp analyze</code><br><br>
                    <code style="background: rgba(255,255,255,0.1); padding: 0.25rem 0.5rem; border-radius: 4px;">unrealmate perf audit</code>
                </p>
            </div>
        </div>
    </div>

    <footer class="footer">
        <p>Generated by <a href="https://github.com/gktrk363/unrealmate">UnrealMate</a> | © 2026 G & E ZYNTH</p>
        <p style="margin-top: 0.5rem;"><span class="live">●</span> Dashboard is running on port {self.port}</p>
    </footer>

    <script>
        // Auto-refresh every 30 seconds
        setTimeout(() => location.reload(), 30000);
    </script>
</body>
</html>"""

    def start(self, open_browser: bool = True) -> None:
        """Start the dashboard server."""
        html_content = self.generate_html()

        class Handler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self_handler):
                self_handler.send_response(200)
                self_handler.send_header("Content-type", "text/html")
                self_handler.end_headers()
                self_handler.wfile.write(html_content.encode())

            def log_message(self_handler, format, *args):
                pass  # Suppress logging

        try:
            self.server = socketserver.TCPServer(("", self.port), Handler)
            self.thread = threading.Thread(target=self.server.serve_forever)
            self.thread.daemon = True
            self.thread.start()

            url = f"http://localhost:{self.port}"
            console.print(f"[green]✓ Dashboard running at {url}[/green]")

            if open_browser:
                webbrowser.open(url)

        except OSError as e:
            console.print(f"[red]✗ Could not start dashboard: {e}[/red]")

    def stop(self) -> None:
        """Stop the dashboard server."""
        if self.server:
            self.server.shutdown()
            console.print("[yellow]Dashboard stopped[/yellow]")


def launch_dashboard(
    project_path: Optional[Path] = None,
    port: int = 8080,
    open_browser: bool = True,
) -> DashboardServer:
    """
    Launch the web dashboard.

    Args:
        project_path: Path to the Unreal project
        port: Port to run the server on
        open_browser: Whether to open browser automatically

    Returns:
        DashboardServer instance
    """
    data = DashboardData(
        project_name=project_path.name if project_path else "UnrealMate",
        project_path=str(project_path) if project_path else "",
        last_scan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        assets={"total": 0, "textures": 0, "meshes": 0, "materials": 0},
        blueprints={"total": 0, "complex": 0, "avg_nodes": 0},
        performance={"score": "A", "score_percent": 85, "issues": 2},
        git_status={"branch": "main", "modified": 0, "lfs": True},
    )

    server = DashboardServer(data, port)
    server.start(open_browser)
    return server

