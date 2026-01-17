from urllib.parse import urlparse

import httpx

from app.core.config import settings


def validate_url(url: str):
    parsed = urlparse(url)
    # Handle relative URLs or URLs without hostname (though httpx usually wants full URLs for some calls)
    if not parsed.hostname:
        return

    if parsed.hostname not in settings.ALLOWED_DOMAINS:
        raise ValueError(
            f"External request to {parsed.hostname} is blocked by security policy."
        )


class SafeAsyncClient(httpx.AsyncClient):
    """
    A wrapper around httpx.AsyncClient that validates URLs against a whitelist
    to prevent SSRF attacks.
    """

    def __init__(self, *args, **kwargs):
        if "timeout" not in kwargs:
            kwargs["timeout"] = 10.0
        super().__init__(*args, **kwargs)

    async def request(
        self, method: str, url: httpx._types.URLTypes, **kwargs
    ) -> httpx.Response:
        validate_url(str(url))
        return await super().request(method, url, **kwargs)
