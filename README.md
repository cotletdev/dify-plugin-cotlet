# Cotlet

Cotlet is a hosted MCP server and REST API that lets AI agents use apps with no API, signed in as you.

Cotlet lets your AI agent use the apps that never built an API. Connect an app once, sign in yourself, and Claude, ChatGPT, Cursor or n8n can call it as a tool over MCP or REST. Cotlet builds, tests and maintains every integration.

This plugin brings the same REST API to Dify agents and workflows (for example Skool, Substack, Milanote or Partiful).

## Security

Cotlet never stores passwords. It keeps only the app session, in an AES-256 vault, and the model never sees it. Actions that reach other people wait for your approval, and credits for failed calls are refunded.

Cotlet is an independent service and is not affiliated with the apps it integrates.

## Setup

1. Sign up at https://cotlet.dev/signup, request the apps you need, and sign in to each app once in your Cloud Browser.
2. In the Cotlet console (https://cotlet.dev/app, API keys) create an API key.
3. In Dify, install the plugin and paste the key into **Cotlet API key**. The key is checked when you save it.

## Tools

| Tool | What it does | Needs a key |
|---|---|---|
| `list_apps` | Lists the apps Cotlet supports, with an optional filter by slug, name or category. | No |
| `get_app` | Lists one app's endpoints with name, method and path. | No |
| `get_endpoint` | Returns an endpoint's input schema and an example response. | No |
| `call_endpoint` | Calls an endpoint: app, method, path and an optional JSON object of inputs. | Yes |

Inputs go in the query string for GET and DELETE, and in a JSON body for POST, PUT and PATCH. Actions that reach other people (publish, message, email) return `202` with `status: pending` and an `approval_url`; nothing runs until you approve it there. Errors come back as Cotlet's own error JSON with the HTTP status. If your account has no access to an app yet, the response says so and links to the page where you turn it on or request it; nothing is charged.

## Example flow

1. `list_apps` with `query` = `skool` returns the slug `skool`.
2. `get_app` with `app` = `skool` shows `GET groups/{group}/members`.
3. `get_endpoint` with `app` = `skool`, `endpoint` = `list_members` shows the accepted inputs.
4. `call_endpoint` with `app` = `skool`, `method` = `GET`, `path` = `groups/mygroup/members`, `params_json` = `{"limit": 20}` returns the members.

## Links

- REST API docs: https://cotlet.dev/docs/api
- Supported apps: https://cotlet.dev/integrations
- Privacy: https://cotlet.dev/privacy (see also `PRIVACY.md`)
- Contact: https://cotlet.dev/contact
- Source repository: https://github.com/cotletdev/dify-plugin-cotlet
