from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.cotlet_client import as_object, failure, request


class ListAppsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        query = str(tool_parameters.get("query") or "").strip().lower()
        resp = request("GET", "/apps")
        if not resp.ok:
            yield self.create_json_message(failure(resp))
            return

        apps = as_object(resp.body).get("apps")
        if not isinstance(apps, list):
            yield self.create_json_message({"error": "unexpected_response", "message": "Cotlet returned no app list."})
            return

        rows = []
        for app in apps:
            if not isinstance(app, dict):
                continue
            haystack = " ".join(str(app.get(k) or "") for k in ("slug", "name", "category")).lower()
            if query and query not in haystack:
                continue
            rows.append(
                {
                    "slug": app.get("slug"),
                    "name": app.get("name"),
                    "summary": app.get("summary"),
                    "endpoints_count": app.get("endpoints_count"),
                    "docs_url": app.get("docs_url"),
                }
            )
        yield self.create_json_message({"count": len(rows), "apps": rows})
