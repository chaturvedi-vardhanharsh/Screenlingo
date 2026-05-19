from __future__ import annotations

from .config import AppConfig
from .ssl_setup import configure_ssl, patch_requests


def init_app() -> AppConfig:
    """Load config and configure TLS before any network or UI work."""
    cfg = AppConfig.load()
    configure_ssl(
        use_system_certificates=cfg.use_system_certificates,
        ssl_verify=cfg.ssl_verify,
    )
    patch_requests()
    return cfg
