from __future__ import annotations

"""Configure TLS for translation APIs (corporate proxies / custom CAs)."""

_ssl_verify = True


def configure_ssl(*, use_system_certificates: bool = True, ssl_verify: bool = True) -> None:
    global _ssl_verify
    _ssl_verify = ssl_verify

    if not ssl_verify:
        return

    if use_system_certificates:
        try:
            import truststore

            truststore.inject_into_ssl()
        except ImportError:
            pass

    try:
        import os

        import certifi

        bundle = certifi.where()
        os.environ.setdefault("SSL_CERT_FILE", bundle)
        os.environ.setdefault("REQUESTS_CA_BUNDLE", bundle)
    except ImportError:
        pass


def requests_verify_setting():
    """Value for requests ``verify=`` — uses cert bundle or False if disabled."""
    if not _ssl_verify:
        return False
    try:
        import certifi

        return certifi.where()
    except ImportError:
        return True


_requests_patched = False


def patch_requests() -> None:
    """Ensure all requests calls respect SSL settings (incl. deep-translator)."""
    global _requests_patched
    if _requests_patched:
        return
    _requests_patched = True

    import requests as req

    original_get = req.get
    original_post = req.post

    def get(*args, **kwargs):
        kwargs.setdefault("verify", requests_verify_setting())
        kwargs.setdefault("timeout", kwargs.get("timeout", 20))
        return original_get(*args, **kwargs)

    def post(*args, **kwargs):
        kwargs.setdefault("verify", requests_verify_setting())
        kwargs.setdefault("timeout", kwargs.get("timeout", 20))
        return original_post(*args, **kwargs)

    req.get = get
    req.post = post
