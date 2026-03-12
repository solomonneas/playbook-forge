"""API key authentication helpers."""

from __future__ import annotations

import os
import uuid
from typing import Optional

from fastapi import Header, HTTPException, status

_API_KEY: Optional[str] = None


def initialize_api_key() -> str:
    global _API_KEY
    if _API_KEY:
        return _API_KEY

    configured = os.getenv("PLAYBOOK_FORGE_API_KEY")
    if configured:
        _API_KEY = configured
    else:
        _API_KEY = str(uuid.uuid4())
        print(f"[playbook-forge] Generated API key: {_API_KEY}")

    return _API_KEY


def get_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> str:
    expected_key = initialize_api_key()
    if x_api_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return x_api_key
