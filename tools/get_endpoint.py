from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.cotlet_client import as_object, error_body, failure, is_valid_slug, request


class GetEndpointTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        app = str(tool_parameters.get("app") or "").strip()
        endpoint = str(tool_parameters.get("endpoint") or "").strip()
        if not is_valid_slug(app) or not is_valid_slug(endpoint):
            yield self.create_json_message(
                error_body(
                    "invalid_input",
                    "app is an app slug and endpoint is an endpoint name, both from get_app (for example 'skool' and 'list_groups').",
                )
            )
            return

        resp = request("GET", f"/apps/{app}/endpoints/{endpoint}")
        if not resp.ok:
            yield self.create_json_message(failure(resp))
            return
        yield self.create_json_message(as_object(resp.body))
