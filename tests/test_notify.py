import os
import pytest
from unittest.mock import patch, MagicMock
from optimization_loop.autoresearch_notify import (
    NotifyConfig,
    load_notify_config,
    send_notification,
    notify_improvement,
)


class TestNotifyConfig:
    def test_from_env_vars(self):
        env = {
            "AUTORESEARCH_SMTP_HOST": "smtp.example.com",
            "AUTORESEARCH_SMTP_PORT": "587",
            "AUTORESEARCH_SMTP_USER": "user@example.com",
            "AUTORESEARCH_SMTP_PASS": "secret",
            "AUTORESEARCH_NOTIFY_EMAIL": "dest@example.com",
            "AUTORESEARCH_WEBHOOK_URL": "https://hooks.example.com/notify",
        }
        with patch.dict(os.environ, env, clear=False):
            config = load_notify_config()
        assert config.smtp_host == "smtp.example.com"
        assert config.webhook_url == "https://hooks.example.com/notify"
        assert config.notify_email == "dest@example.com"

    def test_empty_config(self):
        with patch.dict(os.environ, {}, clear=True):
            config = load_notify_config()
        assert config.smtp_host is None
        assert config.webhook_url is None


class TestSendNotification:
    @patch("optimization_loop.autoresearch_notify._send_webhook")
    def test_webhook_notification(self, mock_webhook):
        config = NotifyConfig(webhook_url="https://hooks.example.com/notify")
        send_notification(config, "Test Subject", "Test body")
        mock_webhook.assert_called_once()

    @patch("optimization_loop.autoresearch_notify._send_email")
    def test_email_notification(self, mock_email):
        config = NotifyConfig(
            smtp_host="smtp.example.com",
            smtp_port=587,
            smtp_user="user@test.com",
            smtp_pass="pass",
            notify_email="dest@test.com",
        )
        send_notification(config, "Subject", "Body")
        mock_email.assert_called_once()

    def test_no_config_no_crash(self):
        config = NotifyConfig()
        # Should not raise
        send_notification(config, "Subject", "Body")


class TestNotifyImprovement:
    @patch("optimization_loop.autoresearch_notify.send_notification")
    def test_notify_on_improvement(self, mock_send):
        config = NotifyConfig(webhook_url="https://hooks.example.com")
        notify_improvement(config, "accuracy", 0.95, 0.90)
        mock_send.assert_called_once()
        call_args = mock_send.call_args
        assert "0.95" in call_args[0][2] or "0.95" in str(call_args)
