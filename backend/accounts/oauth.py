"""Google and Apple OAuth token verification and user provisioning."""
import json
import logging
import time
from typing import Any
from urllib.parse import urlencode

import jwt
import requests
from django.conf import settings
from django.contrib.auth import get_user_model

logger = logging.getLogger("estateos.oauth")
User = get_user_model()

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
APPLE_AUTH_URL = "https://appleid.apple.com/auth/authorize"
APPLE_TOKEN_URL = "https://appleid.apple.com/auth/token"
APPLE_KEYS_URL = "https://appleid.apple.com/auth/keys"

_apple_keys_cache: dict[str, Any] = {"keys": None, "expires_at": 0}


def get_google_authorize_url(state: str = "") -> str:
    params = {
        "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
        "redirect_uri": settings.OAUTH_REDIRECT_URL,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }
    return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"


def exchange_google_code(code: str) -> dict:
    response = requests.post(
        GOOGLE_TOKEN_URL,
        data={
            "code": code,
            "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
            "redirect_uri": settings.OAUTH_REDIRECT_URL,
            "grant_type": "authorization_code",
        },
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def verify_google_id_token(token: str) -> dict:
    try:
        from google.auth.transport import requests as google_requests
        from google.oauth2 import id_token as google_id_token
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "Google OAuth requires the google-auth package. "
            "Install backend dependencies with: pip install -r requirements.txt"
        ) from exc

    return google_id_token.verify_oauth2_token(
        token,
        google_requests.Request(),
        settings.GOOGLE_OAUTH_CLIENT_ID,
    )


def get_apple_authorize_url(state: str = "") -> str:
    params = {
        "client_id": settings.APPLE_OAUTH_CLIENT_ID,
        "redirect_uri": settings.OAUTH_REDIRECT_URL,
        "response_type": "code id_token",
        "response_mode": "form_post",
        "scope": "name email",
        "state": state,
    }
    return f"{APPLE_AUTH_URL}?{urlencode(params)}"


def _get_apple_public_keys() -> list[dict]:
    now = time.time()
    if _apple_keys_cache["keys"] and _apple_keys_cache["expires_at"] > now:
        return _apple_keys_cache["keys"]
    response = requests.get(APPLE_KEYS_URL, timeout=15)
    response.raise_for_status()
    keys = response.json()["keys"]
    _apple_keys_cache["keys"] = keys
    _apple_keys_cache["expires_at"] = now + 3600
    return keys


def verify_apple_identity_token(identity_token: str) -> dict:
    header = jwt.get_unverified_header(identity_token)
    keys = _get_apple_public_keys()
    public_key = None
    for key in keys:
        if key.get("kid") == header.get("kid"):
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
            break
    if public_key is None:
        raise ValueError("Unable to find matching Apple public key.")

    return jwt.decode(
        identity_token,
        public_key,
        algorithms=["RS256"],
        audience=settings.APPLE_OAUTH_CLIENT_ID,
        issuer="https://appleid.apple.com",
    )


def exchange_apple_code(code: str) -> dict:
    client_secret = _build_apple_client_secret()
    response = requests.post(
        APPLE_TOKEN_URL,
        data={
            "client_id": settings.APPLE_OAUTH_CLIENT_ID,
            "client_secret": client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": settings.OAUTH_REDIRECT_URL,
        },
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def _build_apple_client_secret() -> str:
    if not settings.APPLE_OAUTH_PRIVATE_KEY:
        raise ValueError("APPLE_OAUTH_PRIVATE_KEY is not configured.")
    private_key = settings.APPLE_OAUTH_PRIVATE_KEY.replace("\\n", "\n")
    now = int(time.time())
    headers = {"kid": settings.APPLE_OAUTH_KEY_ID}
    payload = {
        "iss": settings.APPLE_OAUTH_TEAM_ID,
        "iat": now,
        "exp": now + 3600,
        "aud": "https://appleid.apple.com",
        "sub": settings.APPLE_OAUTH_CLIENT_ID,
    }
    return jwt.encode(payload, private_key, algorithm="ES256", headers=headers)


def get_or_create_oauth_user(provider: str, profile: dict) -> User:
    email = profile.get("email")
    if not email:
        raise ValueError("Email is required from OAuth provider.")

    sub = profile.get("sub") or profile.get("provider_id")
    metadata_key = f"{provider}_id"

    user = User.objects.filter(email__iexact=email).first()
    if user:
        metadata = user.metadata or {}
        if sub and metadata.get(metadata_key) != sub:
            metadata[metadata_key] = sub
            user.metadata = metadata
            user.save(update_fields=["metadata"])
        if not user.is_email_verified:
            user.is_email_verified = True
            user.save(update_fields=["is_email_verified"])
        return user

    first_name = profile.get("given_name") or profile.get("first_name") or ""
    last_name = profile.get("family_name") or profile.get("last_name") or ""
    username = email.split("@")[0][:140]
    base_username = username
    counter = 1
    while User.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1

    user = User.objects.create_user(
        username=username,
        email=email,
        password=User.objects.make_random_password(length=32),
        first_name=first_name,
        last_name=last_name,
        is_email_verified=True,
        metadata={metadata_key: sub} if sub else {},
    )
    logger.info("Created user via %s OAuth: %s", provider, email)
    return user
