from unittest.mock import patch

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.core.auth import require_mfa, verify_token


@pytest.mark.asyncio
async def test_verify_token_mock():
    with patch("firebase_admin.auth.verify_id_token") as mock_verify:
        mock_verify.return_value = {"email": "test@example.com", "uid": "123"}

        res = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid-token")
        token = await verify_token(res)
        assert token["email"] == "test@example.com"


def test_require_mfa_valid():
    token = {"amr": ["mfa"]}
    assert require_mfa(token) is True


def test_require_mfa_invalid():
    token = {"amr": ["pwd"]}
    with pytest.raises(HTTPException) as exc:
        require_mfa(token)
    assert exc.value.status_code == 403
