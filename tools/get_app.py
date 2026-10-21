from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.cotlet_client import as_object, error_body, failure, is_valid_slug, request


def _split_call(call: str, slug: str) -> tuple[str, str]:
    """'GET /api/v1/skool/groups/{group}' -> ('GET', 'groups/{group}'), the path call_endpoint expects."""
    method, _, full = (call or "").partition(" ")
    prefix = f"/api/v1/{slug}/"
    full = full.strip()
    return method.strip(), full[len(prefix):] if full.startswith(prefix) else full


class GetAppTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        app = str(tool_parameters.get("app") or "").strip()
        if not is_valid_slug(app):
            yield self.create_json_message(
                error_body("invalid_input", "app must be an app slug from list_apps, for example 'skool'.")
            )
            return

        resp = request("GET", f"/apps/{app}")
        if not resp.ok:
            yield self.create_json_message(failure(resp))
            return

        data = as_object(resp.body)
        endpoints = []
        for ep in data.get("endpoints") or []:
            if not isinstance(ep, dict):
                continue
            method, path = _split_call(str(ep.get("call") or ""), app)
            endpoints.append(
                {
                    "name": ep.get("name"),
                    "method": method,
                    "path": path,
                    "title": ep.get("title"),
                    "access": ep.get("access"),
                    "description": ep.get("description"),
                }
            )
        yield self.create_json_message(
            {
                "slug": data.get("slug", app),
                "name": data.get("name"),
                "about": data.get("about"),
                "login": data.get("login"),
                "docs_url": data.get("docs_url"),
                "endpoints_count": len(endpoints),
                "endpoints": endpoints,
            }
        )
