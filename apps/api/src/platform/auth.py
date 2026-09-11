import asyncio
from dataclasses import dataclass
from functools import lru_cache

import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.platform.config import Settings, get_settings
from src.platform.locale import MESSAGES

bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class Identity:
    subject: str


@lru_cache(maxsize=4)
def jwks_client(url: str) -> jwt.PyJWKClient:
    return jwt.PyJWKClient(url, cache_keys=True, lifespan=300, timeout=5)


async def current_identity(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    settings: Settings = Depends(get_settings),
) -> Identity:
    messages = MESSAGES[request.state.locale]
    if credentials is None:
        raise HTTPException(401, messages["unauthorized"], headers={"WWW-Authenticate": "Bearer"})
    if not settings.logto_issuer or not settings.logto_jwks_url:
        raise HTTPException(503, messages["unavailable"])
    try:
        key = await asyncio.to_thread(
            jwks_client(settings.logto_jwks_url).get_signing_key_from_jwt, credentials.credentials
        )
        claims = jwt.decode(
            credentials.credentials,
            key.key,
            algorithms=["ES384", "RS256"],
            issuer=settings.logto_issuer,
            audience=settings.logto_audience,
            options={"require": ["exp", "iss", "aud", "sub"]},
        )
        subject = claims["sub"]
        if not isinstance(subject, str) or not subject:
            raise jwt.InvalidTokenError("missing subject")
        return Identity(subject)
    except jwt.PyJWKClientConnectionError as exc:
        raise HTTPException(503, messages["unavailable"]) from exc
    except jwt.PyJWTError as exc:
        raise HTTPException(
            401, messages["unauthorized"], headers={"WWW-Authenticate": "Bearer"}
        ) from exc
