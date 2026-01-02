import pytest
from src.http_client import SafeAsyncClient

@pytest.mark.asyncio
async def test_safe_client_allowed():
    async with SafeAsyncClient() as client:
        # Should NOT raise ValueError
        try:
            # We don't care if it fails network-wise, only that validation passes
            await client.get("https://identitytoolkit.googleapis.com/foo")
        except ValueError:
            pytest.fail("Should not raise ValueError")
        except Exception:
             pass 

@pytest.mark.asyncio
async def test_safe_client_blocked():
    async with SafeAsyncClient() as client:
        with pytest.raises(ValueError, match="not allowed"):
            await client.get("https://evil.com/foo")
