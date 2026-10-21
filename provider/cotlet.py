from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from utils.cotlet_client import request

# Cotlet has no "who am I" endpoint. Reading a call that cannot exist is the cheapest
# authenticated request: a bad key answers 401 invalid_api_key, a good key answers 404.
_PROBE_PATH = "/calls/00000000-0000-4000-8000-000000000000"


class CotletProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        api_key = str(credentials.get("api_key") or "").strip()
        if not api_key:
            raise ToolProviderCredentialValidationError("Cotlet API key is required.")

        resp = request("GET", _PROBE_PATH, api_key, timeout=20)
        if resp.status == 0:
            raise ToolProviderCredentialValidationError("Could not reach cotlet.dev to check the key. Try again.")
        if resp.status == 401:
            raise ToolProviderCredentialValidationError(
                "Cotlet rejected this API key (unknown, expired or revoked). Create a new one at https://cotlet.dev/app."
            )
        if resp.status >= 500 or resp.status == 429:
            raise ToolProviderCredentialValidationError(f"Cotlet could not check the key right now (HTTP {resp.status}). Try again.")
