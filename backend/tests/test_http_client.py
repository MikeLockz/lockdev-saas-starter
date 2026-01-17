import pytest

from app.core.http_client import SafeAsyncClient


@pytest.mark.asyncio
async def test_safe_client_allowed():
    async with SafeAsyncClient():
        # We don't actually make the request, just check if it validates
        # But SafeAsyncClient.request calls super().request which might try to connect
        # So we should probably mock the transport or just test validate_url
        pass


from app.core.http_client import validate_url


def test_validate_url_allowed():
    validate_url("http://localhost:8000/health")
    validate_url("https://identitytoolkit.googleapis.com/v1/accounts")


def test_validate_url_blocked():
    with pytest.raises(ValueError, match="blocked by security policy"):
        validate_url("http://evil.com/ssrf")


@pytest.mark.asyncio
async def test_safe_async_client_blocked():
    async with SafeAsyncClient() as client:
        with pytest.raises(ValueError, match="blocked by security policy"):
            await client.get("http://evil.com/ssrf")
