"""Notification hooks: email, webhooks, apprise, desktop notifications.

Never crashes on notification failure -- all errors are silently caught.
Config via environment variables or YAML.
"""
from __future__ import annotations

import json
import os
import smtplib
from dataclasses import dataclass, field
from email.mime.text import MIMEText


@dataclass
class NotifyConfig:
    """Notification configuration."""
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_pass: str | None = None
    notify_email: str | None = None
    webhook_url: str | None = None
    apprise_url: str | None = None
    desktop: bool = False


def load_notify_config() -> NotifyConfig:
    """Load notification config from environment variables."""
    return NotifyConfig(
        smtp_host=os.environ.get("AUTORESEARCH_SMTP_HOST"),
        smtp_port=int(os.environ.get("AUTORESEARCH_SMTP_PORT", "587")),
        smtp_user=os.environ.get("AUTORESEARCH_SMTP_USER"),
        smtp_pass=os.environ.get("AUTORESEARCH_SMTP_PASS"),
        notify_email=os.environ.get("AUTORESEARCH_NOTIFY_EMAIL"),
        webhook_url=os.environ.get("AUTORESEARCH_WEBHOOK_URL"),
        apprise_url=os.environ.get("AUTORESEARCH_APPRISE_URL"),
        desktop=os.environ.get("AUTORESEARCH_DESKTOP_NOTIFY", "").lower() in ("1", "true", "yes"),
    )


def _send_email(config: NotifyConfig, subject: str, body: str) -> None:
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = config.smtp_user or ""
    msg["To"] = config.notify_email or ""

    with smtplib.SMTP(config.smtp_host, config.smtp_port) as server:
        server.starttls()
        if config.smtp_user and config.smtp_pass:
            server.login(config.smtp_user, config.smtp_pass)
        server.send_message(msg)


def _send_webhook(url: str, subject: str, body: str) -> None:
    import urllib.request

    data = json.dumps({"subject": subject, "body": body}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    urllib.request.urlopen(req, timeout=10)


def _send_apprise(url: str, subject: str, body: str) -> None:
    try:
        import apprise
        ap = apprise.Apprise()
        ap.add(url)
        ap.notify(title=subject, body=body)
    except ImportError:
        pass


def _send_desktop(subject: str, body: str) -> None:
    try:
        from plyer import notification
        notification.notify(title=subject, message=body[:256], timeout=5)
    except ImportError:
        pass


def send_notification(config: NotifyConfig, subject: str, body: str) -> None:
    """Send notifications via all configured channels. Never raises."""
    if config.smtp_host and config.notify_email:
        try:
            _send_email(config, subject, body)
        except Exception:
            pass

    if config.webhook_url:
        try:
            _send_webhook(config.webhook_url, subject, body)
        except Exception:
            pass

    if config.apprise_url:
        try:
            _send_apprise(config.apprise_url, subject, body)
        except Exception:
            pass

    if config.desktop:
        try:
            _send_desktop(subject, body)
        except Exception:
            pass


def notify_improvement(
    config: NotifyConfig,
    metric_name: str,
    new_value: float,
    old_value: float | None,
) -> None:
    """Send a notification about a metric improvement."""
    if old_value is not None:
        body = f"{metric_name} improved from {old_value:.4f} to {new_value:.4f}"
    else:
        body = f"{metric_name} initial value: {new_value:.4f}"
    subject = f"[autoresearch] {metric_name} improved: {new_value:.4f}"
    send_notification(config, subject, body)
