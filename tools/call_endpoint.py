import json
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.cotlet_client import (
    as_object,
    clean_path,
    error_body,
    failure,
    is_valid_slug,
    normalize_query,
    request,
)

ALLOWED_METHODS = ("GET", "POST", "PUT", "PATCH", "DELETE")


class CallEndpointTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        api_key = str((self.runtime.credentials or {}).get("api_key") or "").strip()
        if not api_key:
            yield self.create_json_message(
                error_body("api_key_required", "Add your Cotlet API key in the plugin credentials (https://cotlet.dev/app, API keys).")
            )
            return

        app = str(tool_parameters.get("app") or "").strip()
        method = str(tool_parameters.get("method") or "").strip().upper()
        path = clean_path(str(tool_parameters.get("path") or ""))
        if not is_valid_slug(app) or method not in ALLOWED_METHODS or path is None:
            yield self.create_json_message(
                error_body(
                    "invalid_input",
                    "Need app (slug), method (GET, POST, PUT, PATCH or DELETE) and path (the part after the app slug, e.g. 'groups/mygroup/members'). Use get_app to find them.",
                )
            )
            return

        raw = tool_parameters.get("params_json")
        params: dict[str, Any] = {}
        if isinstance(raw, dict):
            params = raw
        elif raw is not None and str(raw).strip():
            try:
                parsed = json.loads(str(raw))
            except ValueError as exc:
                yield self.create_json_message(error_body("invalid_input", f"params_json is not valid JSON: {exc}"))
                return
            if not isinstance(parsed, dict):
                yield self.create_json_message(error_body("invalid_input", "params_json must be a JSON object, e.g. {\"limit\": 20}."))
                return
            params = parsed

        url_path = f"/{app}/{path}"
        if method in ("GET", "DELETE"):
            resp = request(method, url_path, api_key, query=normalize_query(params))
        else:
            resp = request(method, url_path, api_key, json_body=params)

        if resp.status == 202:
            body = as_object(resp.body)
            yield self.create_json_message(body)
            url = body.get("approval_url") or "https://cotlet.dev/app/activity?tab=approvals"
            yield self.create_text_message(
                f"Approval needed: this action reaches other people, so it has not run yet. Approve it at {url}, then read the result from status_url."
            )
        elif resp.ok:
            yield self.create_json_message(as_object(resp.body))
        else:
            yield self.create_json_message(failure(resp))
