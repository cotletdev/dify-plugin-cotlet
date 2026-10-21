"""Minimal HTTP client for the Cotlet REST API. Never raises: errors come back as data."""

import json
import re
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import quote

import requests

BASE_URL = "https://cotlet.dev/api/v1"
DEFAULT_TIMEOUT = 60
USER_AGENT = "cotlet-dify-plugin/0.0.1"

_SLUG_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")
_BAD_PATH_CHARS = re.compile(r"[\s?#\\\x00-\x1f]")


@dataclass
class CotletResponse:
    status: int  # HTTP status, 0 when the request never got an answer
    body: Any
    headers: dict[str, str] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return 200 <= self.status < 300


def error_body(code: str, message: str, **extra: Any) -> dict[str, Any]:
    return {"error": code, "message": message, **extra}


def is_valid_slug(value: str) -> bool:
    return bool(value) and bool(_SLUG_RE.match(value))


def clean_path(path: str) -> str | None:
    """Return a safe, percent-encoded path (no leading slash) or None when it is not acceptable."""
    path = (path or "").strip().lstrip("/")
    if not path or "://" in path or _BAD_PATH_CHARS.search(path):
        return None
    segments = path.split("/")
    if any(seg in ("", ".", "..") for seg in segments):
        return None
    return "/".join(quote(seg, safe="%") for seg in segments)


def normalize_query(params: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in params.items():
        if value is None:
            continue
        if isinstance(value, bool):
            out[key] = "true" if value else "false"
        elif isinstance(value, dict):
            out[key] = json.dumps(value, separators=(",", ":"))
        elif isinstance(value, list):
            out[key] = [
                json.dumps(v, separators=(",", ":")) if isinstance(v, (dict, list)) else
                ("true" if v is True else "false" if v is False else v)
                for v in value
            ]
        else:
            out[key] = value
    return out


def request(
    method: str,
    url_path: str,
    api_key: str | None = None,
    query: dict[str, Any] | None = None,
    json_body: Any = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> CotletResponse:
    """Call BASE_URL + url_path. url_path starts with a slash and is already encoded."""
    headers = {"Accept": "application/json", "User-Agent": USER_AGENT}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    kwargs: dict[str, Any] = {"headers": headers, "allow_redirects": False}
    if query:
        kwargs["params"] = query
    if json_body is not None:
        kwargs["json"] = json_body
    try:
        resp = requests.request(method.upper(), BASE_URL + url_path, timeout=timeout, **kwargs)
    except requests.Timeout:
        return CotletResponse(0, error_body("timeout", f"Cotlet did not answer within {timeout} seconds."))
    except requests.RequestException as exc:
        return CotletResponse(0, error_body("network_error", f"Could not reach cotlet.dev: {type(exc).__name__}"))

    try:
        body: Any = resp.json()
    except ValueError:
        text = (resp.text or "").strip()
        body = error_body("non_json_response", text[:500] or f"Empty response (HTTP {resp.status_code}).")
    # A 3xx is never expected from the API; surface it instead of following it.
    return CotletResponse(resp.status_code, body, dict(resp.headers))


def as_object(body: Any) -> dict[str, Any]:
    """Dify JSON messages are objects; wrap anything else."""
    return body if isinstance(body, dict) else {"result": body}


def failure(resp: CotletResponse) -> dict[str, Any]:
    """Cotlet's own error JSON (kept as-is) plus the HTTP status."""
    out = as_object(resp.body)
    if "error" not in out:
        out = error_body("http_error", f"Cotlet returned HTTP {resp.status}.", details=out)
    out = {**out, "http_status": resp.status}
    retry = resp.headers.get("Retry-After")
    if resp.status == 429 and retry:
        out["retry_after_seconds"] = retry
    return out
