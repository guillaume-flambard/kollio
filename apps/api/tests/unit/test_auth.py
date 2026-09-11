from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from starlette.requests import Request

from src.platform import auth
from src.platform.config import Settings


@pytest.fixture
def signing_keys(monkeypatch):
    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    monkeypatch.setattr(
        auth,
        "jwks_client",
        lambda url: SimpleNamespace(
            get_signing_key_from_jwt=lambda token: SimpleNamespace(key=private.public_key())
        ),
    )
    return private


@pytest.mark.parametrize("changed_claim", [None, "iss", "aud", "exp", "sub", "signature"])
async def test_identity_validates_all_security_claims(signing_keys, changed_claim):
    claims = {
        "sub": "member",
        "iss": "https://identity.example/oidc",
        "aud": "https://kollio.example/api",
        "exp": datetime.now(UTC) + timedelta(minutes=1),
    }
    if changed_claim in {"iss", "aud", "sub"}:
        claims[changed_claim] = "" if changed_claim == "sub" else "other"
    if changed_claim == "exp":
        claims["exp"] = datetime.now(UTC) - timedelta(seconds=1)
    key = (
        rsa.generate_private_key(public_exponent=65537, key_size=2048)
        if changed_claim == "signature"
        else signing_keys
    )
    token = jwt.encode(claims, key, algorithm="RS256")
    request = Request({"type": "http", "state": {"locale": "en"}})
    settings = Settings(
        _env_file=None,
        logto_issuer="https://identity.example/oidc",
        logto_audience="https://kollio.example/api",
        logto_jwks_url="https://identity.example/jwks",
    )
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    if changed_claim is None:
        identity = await auth.current_identity(request, credentials, settings)
        assert identity.subject == "member"
    else:
        with pytest.raises(HTTPException) as rejected:
            await auth.current_identity(request, credentials, settings)
        assert rejected.value.status_code == 401
