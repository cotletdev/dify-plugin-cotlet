"""Smoke test: runs each tool's _invoke against the live Cotlet API.

Run from the plugin root:  python tests/smoke_test.py
The three discovery tools need no key. call_endpoint runs only when COTLET_API_KEY is set.
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dify_plugin.entities.tool import ToolRuntime  # noqa: E402
from dify_plugin.core.runtime import Session  # noqa: E402

from provider.cotlet import CotletProvider  # noqa: E402
from tools.call_endpoint import CallEndpointTool  # noqa: E402
from tools.get_app import GetAppTool  # noqa: E402
from tools.get_endpoint import GetEndpointTool  # noqa: E402
from tools.list_apps import ListAppsTool  # noqa: E402

API_KEY = os.environ.get("COTLET_API_KEY", "")
failures: list[str] = []


def run(tool_cls, params: dict, key: str = "") -> list[dict]:
    tool = tool_cls(
        runtime=ToolRuntime(credentials={"api_key": key} if key else {}, user_id="smoke", session_id="smoke"),
        session=Session.empty_session(),
    )
    out = []
    for msg in tool._invoke(params):
        out.append(msg.message.json_object if msg.type.value == "json" else {"text": msg.message.text})
    return out


def check(name: str, cond: bool, detail: str) -> None:
    print(f"[{'PASS' if cond else 'FAIL'}] {name}: {detail}")
    if not cond:
        failures.append(name)


def main() -> int:
    apps = run(ListAppsTool, {})[0]
    check("list_apps", apps.get("count", 0) > 10, f"{apps.get('count')} apps, first={apps['apps'][0]}")
    flt = run(ListAppsTool, {"query": "skool"})[0]
    check("list_apps filter", any(a["slug"] == "skool" for a in flt["apps"]), f"{flt['count']} match 'skool'")

    app = run(GetAppTool, {"app": "skool"})[0]
    check("get_app", app.get("endpoints_count", 0) > 0, f"{app.get('endpoints_count')} endpoints, first={app['endpoints'][0]['method']} {app['endpoints'][0]['path']}")

    ep = run(GetEndpointTool, {"app": "skool", "endpoint": "list_groups"})[0]
    check("get_endpoint", "input_schema" in ep and "example_response" in ep, f"keys={sorted(ep)[:6]}")

    bad = run(GetAppTool, {"app": "no-such-app-xyz"})[0]
    check("get_app unknown app returns error JSON", "error" in bad, json.dumps(bad)[:140])

    nokey = run(CallEndpointTool, {"app": "skool", "method": "GET", "path": "groups"})[0]
    check("call_endpoint without key", nokey.get("error") == "api_key_required", nokey.get("error", ""))
    badpath = run(CallEndpointTool, {"app": "skool", "method": "GET", "path": "../x"}, key="k")[0]
    check("call_endpoint rejects ..", badpath.get("error") == "invalid_input", badpath.get("error", ""))
    fake = run(CallEndpointTool, {"app": "skool", "method": "GET", "path": "groups"}, key="ck_fake")[0]
    check("call_endpoint fake key -> Cotlet error JSON", fake.get("error") == "invalid_api_key" and fake.get("http_status") == 401, json.dumps(fake)[:140])

    try:
        CotletProvider()._validate_credentials({"api_key": "ck_fake"})
        check("validation rejects fake key", False, "no exception")
    except Exception as exc:  # ToolProviderCredentialValidationError
        check("validation rejects fake key", "rejected" in str(exc), str(exc)[:100])

    if API_KEY:
        CotletProvider()._validate_credentials({"api_key": API_KEY})
        check("validation accepts real key", True, "no exception")
        res = run(CallEndpointTool, {"app": os.environ.get("COTLET_APP", "skool"), "method": "GET", "path": os.environ.get("COTLET_PATH", "groups")}, key=API_KEY)
        check("call_endpoint real call", True, json.dumps(res)[:200])
    else:
        print("[SKIP] real call_endpoint and key validation: set COTLET_API_KEY (optional COTLET_APP, COTLET_PATH)")

    print("FAILED: " + ", ".join(failures) if failures else "ALL OK")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
