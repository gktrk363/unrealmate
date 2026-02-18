"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    UnrealMate - Notification System                          ║
║                                                                              ║
║  Author: gktrk363                                                            ║
║  GitHub: https://github.com/gktrk363/unrealmate                              ║
║  Purpose: Email and Slack/Discord notifications                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

© 2026 gktrk363 - Crafted with passion for Unreal Engine developers
"""

from __future__ import annotations

import json
import os
import smtplib
import ssl
from abc import ABC, abstractmethod
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Optional
from urllib.request import Request, urlopen

from rich.console import Console

console = Console()


# ═══════════════════════════════════════════════════════════════════════════════
# BASE NOTIFIER
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class NotificationMessage:
    """Notification message structure."""
    title: str
    body: str
    level: str = "info"  # info, success, warning, error
    extra: Optional[dict[str, Any]] = None


class BaseNotifier(ABC):
    """Base class for all notification providers."""

    @abstractmethod
    def send(self, message: NotificationMessage) -> bool:
        """Send a notification message."""
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Check if the notifier is properly configured."""
        pass


# ═══════════════════════════════════════════════════════════════════════════════
# EMAIL NOTIFIER
# ═══════════════════════════════════════════════════════════════════════════════


class EmailNotifier(BaseNotifier):
    """Email notification provider using SMTP."""

    def __init__(
        self,
        smtp_host: Optional[str] = None,
        smtp_port: int = 587,
        username: Optional[str] = None,
        password: Optional[str] = None,
        from_email: Optional[str] = None,
        to_emails: Optional[list[str]] = None,
        use_tls: bool = True,
    ):
        self.smtp_host = smtp_host or os.environ.get("UNREALMATE_SMTP_HOST", "")
        self.smtp_port = smtp_port or int(os.environ.get("UNREALMATE_SMTP_PORT", "587"))
        self.username = username or os.environ.get("UNREALMATE_SMTP_USER", "")
        self.password = password or os.environ.get("UNREALMATE_SMTP_PASS", "")
        self.from_email = from_email or os.environ.get("UNREALMATE_EMAIL_FROM", "")
        self.to_emails = to_emails or os.environ.get("UNREALMATE_EMAIL_TO", "").split(",")
        self.use_tls = use_tls

    def is_configured(self) -> bool:
        """Check if email is properly configured."""
        return bool(
            self.smtp_host
            and self.username
            and self.password
            and self.from_email
            and self.to_emails
        )

    def send(self, message: NotificationMessage) -> bool:
        """Send an email notification."""
        if not self.is_configured():
            console.print("[yellow]Email not configured, skipping notification[/yellow]")
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"[UnrealMate] {message.title}"
            msg["From"] = self.from_email
            msg["To"] = ", ".join(self.to_emails)

            # Create HTML body
            html_body = self._create_html_body(message)
            msg.attach(MIMEText(message.body, "plain"))
            msg.attach(MIMEText(html_body, "html"))

            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls(context=context)
                server.login(self.username, self.password)
                server.sendmail(self.from_email, self.to_emails, msg.as_string())

            console.print("[green]✓ Email notification sent[/green]")
            return True

        except Exception as e:
            console.print(f"[red]✗ Email failed: {e}[/red]")
            return False

    def _create_html_body(self, message: NotificationMessage) -> str:
        """Create HTML email body."""
        level_colors = {
            "info": "#00d4ff",
            "success": "#00ff88",
            "warning": "#ffcc00",
            "error": "#ff4444",
        }
        color = level_colors.get(message.level, "#00d4ff")

        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; background: #1a1a2e; color: #fff; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: #16213e; border-radius: 10px; padding: 20px;">
                <h1 style="color: {color}; margin-bottom: 10px;">🎮 UnrealMate</h1>
                <h2 style="color: #fff; margin-bottom: 20px;">{message.title}</h2>
                <div style="background: #0f3460; padding: 15px; border-radius: 5px; border-left: 4px solid {color};">
                    <p style="margin: 0; line-height: 1.6;">{message.body.replace(chr(10), '<br>')}</p>
                </div>
                <p style="color: #888; font-size: 12px; margin-top: 20px;">
                    © 2026 gktrk363 - Crafted with passion for Unreal Engine developers
                </p>
            </div>
        </body>
        </html>
        """


# ═══════════════════════════════════════════════════════════════════════════════
# SLACK NOTIFIER
# ═══════════════════════════════════════════════════════════════════════════════


class SlackNotifier(BaseNotifier):
    """Slack notification provider using webhooks."""

    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or os.environ.get("UNREALMATE_SLACK_WEBHOOK", "")

    def is_configured(self) -> bool:
        """Check if Slack is properly configured."""
        return bool(self.webhook_url)

    def send(self, message: NotificationMessage) -> bool:
        """Send a Slack notification."""
        if not self.is_configured():
            console.print("[yellow]Slack not configured, skipping notification[/yellow]")
            return False

        try:
            level_emojis = {
                "info": "ℹ️",
                "success": "✅",
                "warning": "⚠️",
                "error": "❌",
            }
            emoji = level_emojis.get(message.level, "ℹ️")

            payload = {
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"🎮 UnrealMate - {message.title}",
                            "emoji": True,
                        },
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"{emoji} {message.body}",
                        },
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": "© 2026 gktrk363 | <https://github.com/gktrk363/unrealmate|GitHub>",
                            }
                        ],
                    },
                ]
            }

            data = json.dumps(payload).encode("utf-8")
            req = Request(self.webhook_url, data=data, headers={"Content-Type": "application/json"})

            with urlopen(req, timeout=10) as response:
                if response.status == 200:
                    console.print("[green]✓ Slack notification sent[/green]")
                    return True

            return False

        except Exception as e:
            console.print(f"[red]✗ Slack failed: {e}[/red]")
            return False


# ═══════════════════════════════════════════════════════════════════════════════
# DISCORD NOTIFIER
# ═══════════════════════════════════════════════════════════════════════════════


class DiscordNotifier(BaseNotifier):
    """Discord notification provider using webhooks."""

    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or os.environ.get("UNREALMATE_DISCORD_WEBHOOK", "")

    def is_configured(self) -> bool:
        """Check if Discord is properly configured."""
        return bool(self.webhook_url)

    def send(self, message: NotificationMessage) -> bool:
        """Send a Discord notification."""
        if not self.is_configured():
            console.print("[yellow]Discord not configured, skipping notification[/yellow]")
            return False

        try:
            level_colors = {
                "info": 0x00D4FF,
                "success": 0x00FF88,
                "warning": 0xFFCC00,
                "error": 0xFF4444,
            }
            color = level_colors.get(message.level, 0x00D4FF)

            payload = {
                "embeds": [
                    {
                        "title": f"🎮 UnrealMate - {message.title}",
                        "description": message.body,
                        "color": color,
                        "footer": {
                            "text": "© 2026 gktrk363 - Crafted with passion for Unreal Engine developers"
                        },
                    }
                ]
            }

            data = json.dumps(payload).encode("utf-8")
            req = Request(self.webhook_url, data=data, headers={"Content-Type": "application/json"})

            with urlopen(req, timeout=10) as response:
                if response.status == 204:
                    console.print("[green]✓ Discord notification sent[/green]")
                    return True

            return False

        except Exception as e:
            console.print(f"[red]✗ Discord failed: {e}[/red]")
            return False


# ═══════════════════════════════════════════════════════════════════════════════
# NOTIFICATION MANAGER
# ═══════════════════════════════════════════════════════════════════════════════


class NotificationManager:
    """Manages multiple notification providers."""

    def __init__(self):
        self.notifiers: list[BaseNotifier] = []

    def add_notifier(self, notifier: BaseNotifier) -> "NotificationManager":
        """Add a notification provider."""
        if notifier.is_configured():
            self.notifiers.append(notifier)
        return self

    def auto_configure(self) -> "NotificationManager":
        """Auto-configure all available notifiers from environment."""
        self.add_notifier(EmailNotifier())
        self.add_notifier(SlackNotifier())
        self.add_notifier(DiscordNotifier())
        return self

    def notify(self, message: NotificationMessage) -> dict[str, bool]:
        """Send notification to all configured providers."""
        results: dict[str, bool] = {}
        for notifier in self.notifiers:
            name = notifier.__class__.__name__
            results[name] = notifier.send(message)
        return results

    def notify_success(self, title: str, body: str) -> dict[str, bool]:
        """Send a success notification."""
        return self.notify(NotificationMessage(title, body, "success"))

    def notify_error(self, title: str, body: str) -> dict[str, bool]:
        """Send an error notification."""
        return self.notify(NotificationMessage(title, body, "error"))

    def notify_warning(self, title: str, body: str) -> dict[str, bool]:
        """Send a warning notification."""
        return self.notify(NotificationMessage(title, body, "warning"))

    def notify_info(self, title: str, body: str) -> dict[str, bool]:
        """Send an info notification."""
        return self.notify(NotificationMessage(title, body, "info"))
