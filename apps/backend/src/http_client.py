from urllib.parse import urlparse

import httpx

# Whitelist of allowed domains for server-side requests
ALLOWED_OUTBOUND_DOMAINS = [
    "googleapis.com",
    "stripe.com",
    "aws.amazon.com",
    "identitytoolkit.googleapis.com",
    # Add others as needed
]


class SafeAsyncClient(httpx.AsyncClient):
    def __init__(self, *args, **kwargs):
        # Enforce timeout default if not present
        if "timeout" not in kwargs:
            kwargs["timeout"] = 10.0
        super().__init__(*args, **kwargs)

    async def request(self, method, url, **kwargs):
        self._validate_url(str(url))
        return await super().request(method, url, **kwargs)

    def _validate_url(self, url: str):
        parsed = urlparse(url)
        hostname = parsed.hostname
        if not hostname:
            raise ValueError(f"Invalid URL: {url}")

        # Check against whitelist
        # Allow subdomains
        is_allowed = False
        for domain in ALLOWED_OUTBOUND_DOMAINS:
            if hostname == domain or hostname.endswith(f".{domain}"):
                is_allowed = True
                break

        if not is_allowed:
            raise ValueError(f"URL {url} is not allowed. Host {hostname} is not in whitelist.")
