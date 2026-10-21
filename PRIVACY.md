# Privacy Policy

The Cotlet plugin sends data to one service only: `cotlet.dev` (the Cotlet REST API, `https://cotlet.dev/api/v1`).

## What the plugin sends

- Your Cotlet API key, as an `Authorization: Bearer` header, on `call_endpoint` calls and once when you save the key (to check it).
- The inputs of each call: app slug, HTTP method, path and the JSON parameters that you or your agent provide.
- `list_apps`, `get_app` and `get_endpoint` are public discovery requests and carry no key and no user data.

## What the plugin stores

Nothing. The plugin has no storage, no logging of requests or responses, no analytics and no third-party services. The API key is kept by Dify as an encrypted credential.

## What Cotlet does with it

Cotlet processes calls to run the app action you requested in your own account. How Cotlet handles that data is described in its privacy policy: https://cotlet.dev/privacy
