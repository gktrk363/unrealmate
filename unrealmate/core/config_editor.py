"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    UnrealMate - GUI Config Editor                            ║
║                                                                              ║
║  Author: G & E ZYNTH                                                            ║
║  GitHub: https://github.com/gktrk363/unrealmate                              ║
║  Purpose: Browser-based GUI for configuration editing                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

© 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
"""

from __future__ import annotations

import http.server
import json
import socketserver
import threading
import webbrowser
from pathlib import Path
from typing import Any, Optional

from rich.console import Console

console = Console()


class ConfigEditorServer:
    """Browser-based configuration editor."""

    def __init__(self, config_path: Path, port: int = 8081):
        self.config_path = config_path
        self.port = port
        self.server: Optional[socketserver.TCPServer] = None
        self.config: dict[str, Any] = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from file."""
        if not self.config_path.exists():
            return self._default_config()

        try:
            import toml
            return toml.load(self.config_path)
        except Exception:
            return self._default_config()

    def _default_config(self) -> dict[str, Any]:
        """Return default configuration."""
        return {
            "version": "1.0.0",
            "performance": {
                "cache_enabled": True,
                "cache_ttl_hours": 24,
                "max_cache_size_mb": 100,
                "parallel_processing": True,
                "max_workers": 4,
            },
            "signature": {
                "show_banner": True,
                "compact_banner": False,
                "show_footer": True,
                "color_theme": "cyan_magenta",
            },
            "git": {
                "auto_lfs": True,
                "commit_template_enabled": True,
                "pre_commit_hooks": True,
            },
        }

    def _save_config(self, config: dict[str, Any]) -> bool:
        """Save configuration to file."""
        try:
            import toml
            with open(self.config_path, "w", encoding="utf-8") as f:
                toml.dump(config, f)
            self.config = config
            return True
        except Exception as e:
            console.print(f"[red]Error saving config: {e}[/red]")
            return False

    def generate_html(self) -> str:
        """Generate the config editor HTML."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UnrealMate - Config Editor</title>
    <style>
        :root {{
            --primary: #00d4ff;
            --secondary: #ff00ff;
            --success: #00ff88;
            --warning: #ffcc00;
            --error: #ff4444;
            --bg: #0a0a0a;
            --card-bg: #1a1a2e;
            --input-bg: #0f3460;
            --text: #ffffff;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            padding: 2rem;
        }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        h1 {{
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }}
        .subtitle {{ color: #888; margin-bottom: 2rem; }}
        .section {{
            background: var(--card-bg);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .section h2 {{
            color: var(--primary);
            font-size: 1.2rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        .field {{
            margin-bottom: 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .field label {{
            color: #ccc;
            flex: 1;
        }}
        .field input[type="text"],
        .field input[type="number"],
        .field select {{
            background: var(--input-bg);
            border: 1px solid rgba(255,255,255,0.2);
            color: var(--text);
            padding: 0.5rem 1rem;
            border-radius: 6px;
            width: 200px;
        }}
        .field input:focus, .field select:focus {{
            outline: none;
            border-color: var(--primary);
        }}
        .toggle {{
            position: relative;
            width: 50px;
            height: 26px;
        }}
        .toggle input {{ opacity: 0; width: 0; height: 0; }}
        .toggle .slider {{
            position: absolute;
            cursor: pointer;
            top: 0; left: 0; right: 0; bottom: 0;
            background: var(--input-bg);
            border-radius: 26px;
            transition: 0.3s;
        }}
        .toggle .slider:before {{
            content: "";
            position: absolute;
            height: 20px; width: 20px;
            left: 3px; bottom: 3px;
            background: #fff;
            border-radius: 50%;
            transition: 0.3s;
        }}
        .toggle input:checked + .slider {{ background: var(--success); }}
        .toggle input:checked + .slider:before {{ transform: translateX(24px); }}
        .actions {{
            display: flex;
            gap: 1rem;
            margin-top: 2rem;
        }}
        button {{
            padding: 0.75rem 2rem;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            font-weight: bold;
            transition: transform 0.2s;
        }}
        button:hover {{ transform: translateY(-2px); }}
        .btn-primary {{
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
        }}
        .btn-secondary {{
            background: var(--card-bg);
            color: var(--text);
            border: 1px solid rgba(255,255,255,0.2);
        }}
        .toast {{
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            padding: 1rem 2rem;
            border-radius: 8px;
            background: var(--success);
            color: #000;
            font-weight: bold;
            opacity: 0;
            transition: opacity 0.3s;
        }}
        .toast.show {{ opacity: 1; }}
        .footer {{
            text-align: center;
            color: #666;
            margin-top: 2rem;
            padding-top: 1rem;
        }}
        .footer a {{ color: var(--primary); text-decoration: none; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>⚙️ UnrealMate Config Editor</h1>
        <p class="subtitle">Edit your .unrealmate.toml configuration</p>

        <form id="configForm">
            <!-- Performance Section -->
            <div class="section">
                <h2>⚡ Performance</h2>
                <div class="field">
                    <label>Enable Cache</label>
                    <label class="toggle">
                        <input type="checkbox" name="performance.cache_enabled" {'checked' if self.config.get('performance', {}).get('cache_enabled', True) else ''}>
                        <span class="slider"></span>
                    </label>
                </div>
                <div class="field">
                    <label>Cache TTL (hours)</label>
                    <input type="number" name="performance.cache_ttl_hours" value="{self.config.get('performance', {}).get('cache_ttl_hours', 24)}" min="0" max="168">
                </div>
                <div class="field">
                    <label>Max Cache Size (MB)</label>
                    <input type="number" name="performance.max_cache_size_mb" value="{self.config.get('performance', {}).get('max_cache_size_mb', 100)}" min="0" max="1000">
                </div>
                <div class="field">
                    <label>Parallel Processing</label>
                    <label class="toggle">
                        <input type="checkbox" name="performance.parallel_processing" {'checked' if self.config.get('performance', {}).get('parallel_processing', True) else ''}>
                        <span class="slider"></span>
                    </label>
                </div>
                <div class="field">
                    <label>Max Workers</label>
                    <input type="number" name="performance.max_workers" value="{self.config.get('performance', {}).get('max_workers', 4)}" min="1" max="16">
                </div>
            </div>

            <!-- Signature Section -->
            <div class="section">
                <h2>🎨 Appearance</h2>
                <div class="field">
                    <label>Show Banner</label>
                    <label class="toggle">
                        <input type="checkbox" name="signature.show_banner" {'checked' if self.config.get('signature', {}).get('show_banner', True) else ''}>
                        <span class="slider"></span>
                    </label>
                </div>
                <div class="field">
                    <label>Compact Banner</label>
                    <label class="toggle">
                        <input type="checkbox" name="signature.compact_banner" {'checked' if self.config.get('signature', {}).get('compact_banner', False) else ''}>
                        <span class="slider"></span>
                    </label>
                </div>
                <div class="field">
                    <label>Show Footer</label>
                    <label class="toggle">
                        <input type="checkbox" name="signature.show_footer" {'checked' if self.config.get('signature', {}).get('show_footer', True) else ''}>
                        <span class="slider"></span>
                    </label>
                </div>
                <div class="field">
                    <label>Color Theme</label>
                    <select name="signature.color_theme">
                        <option value="cyan_magenta" {'selected' if self.config.get('signature', {}).get('color_theme') == 'cyan_magenta' else ''}>Cyan & Magenta</option>
                        <option value="green_blue" {'selected' if self.config.get('signature', {}).get('color_theme') == 'green_blue' else ''}>Green & Blue</option>
                        <option value="monochrome" {'selected' if self.config.get('signature', {}).get('color_theme') == 'monochrome' else ''}>Monochrome</option>
                    </select>
                </div>
            </div>

            <!-- Git Section -->
            <div class="section">
                <h2>🔧 Git</h2>
                <div class="field">
                    <label>Auto LFS Setup</label>
                    <label class="toggle">
                        <input type="checkbox" name="git.auto_lfs" {'checked' if self.config.get('git', {}).get('auto_lfs', True) else ''}>
                        <span class="slider"></span>
                    </label>
                </div>
                <div class="field">
                    <label>Commit Template</label>
                    <label class="toggle">
                        <input type="checkbox" name="git.commit_template_enabled" {'checked' if self.config.get('git', {}).get('commit_template_enabled', True) else ''}>
                        <span class="slider"></span>
                    </label>
                </div>
                <div class="field">
                    <label>Pre-commit Hooks</label>
                    <label class="toggle">
                        <input type="checkbox" name="git.pre_commit_hooks" {'checked' if self.config.get('git', {}).get('pre_commit_hooks', True) else ''}>
                        <span class="slider"></span>
                    </label>
                </div>
            </div>

            <div class="actions">
                <button type="submit" class="btn-primary">💾 Save Configuration</button>
                <button type="button" class="btn-secondary" onclick="location.reload()">🔄 Reset</button>
            </div>
        </form>

        <div class="footer">
            <p>Generated by <a href="https://github.com/gktrk363/unrealmate">UnrealMate</a> | © 2026 G & E ZYNTH</p>
        </div>
    </div>

    <div id="toast" class="toast">✅ Configuration saved!</div>

    <script>
        document.getElementById('configForm').onsubmit = async (e) => {{
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = {{}};

            // Process form data
            for (const [key, value] of formData.entries()) {{
                const parts = key.split('.');
                if (!data[parts[0]]) data[parts[0]] = {{}};
                data[parts[0]][parts[1]] = value;
            }}

            // Handle checkboxes (unchecked ones don't appear in FormData)
            document.querySelectorAll('input[type="checkbox"]').forEach(cb => {{
                const parts = cb.name.split('.');
                if (!data[parts[0]]) data[parts[0]] = {{}};
                data[parts[0]][parts[1]] = cb.checked;
            }});

            // Convert numbers
            document.querySelectorAll('input[type="number"]').forEach(input => {{
                const parts = input.name.split('.');
                if (data[parts[0]]) {{
                    data[parts[0]][parts[1]] = parseInt(input.value);
                }}
            }});

            // Send to server
            try {{
                const response = await fetch('/save', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(data)
                }});

                if (response.ok) {{
                    const toast = document.getElementById('toast');
                    toast.classList.add('show');
                    setTimeout(() => toast.classList.remove('show'), 3000);
                }}
            }} catch (err) {{
                alert('Error saving configuration');
            }}
        }};
    </script>
</body>
</html>"""

    def start(self, open_browser: bool = True) -> None:
        """Start the config editor server."""
        parent = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(parent.generate_html().encode())

            def do_POST(self):
                if self.path == "/save":
                    content_length = int(self.headers["Content-Length"])
                    post_data = self.rfile.read(content_length)
                    config = json.loads(post_data.decode())
                    config["version"] = "1.0.0"

                    if parent._save_config(config):
                        self.send_response(200)
                        self.end_headers()
                        self.wfile.write(b"OK")
                    else:
                        self.send_response(500)
                        self.end_headers()
                        self.wfile.write(b"Error")

            def log_message(self, format, *args):
                pass

        try:
            self.server = socketserver.TCPServer(("", self.port), Handler)
            thread = threading.Thread(target=self.server.serve_forever)
            thread.daemon = True
            thread.start()

            url = f"http://localhost:{self.port}"
            console.print(f"[green]✓ Config Editor running at {url}[/green]")

            if open_browser:
                webbrowser.open(url)

        except OSError as e:
            console.print(f"[red]✗ Could not start config editor: {e}[/red]")

    def stop(self) -> None:
        """Stop the server."""
        if self.server:
            self.server.shutdown()


def launch_config_editor(
    config_path: Optional[Path] = None,
    port: int = 8081,
    open_browser: bool = True,
) -> ConfigEditorServer:
    """
    Launch the GUI config editor.

    Args:
        config_path: Path to config file
        port: Port to run server on
        open_browser: Whether to open browser

    Returns:
        ConfigEditorServer instance
    """
    if config_path is None:
        config_path = Path.cwd() / ".unrealmate.toml"

    server = ConfigEditorServer(config_path, port)
    server.start(open_browser)
    return server

