# Plugin Submission

## Plugin information

- **Author**: cotletdev
- **Plugin name**: cotlet
- **Version**: 0.0.1
- **Source repository**: https://github.com/cotletdev/dify-plugin-cotlet
- **Contact**: contact@cotlet.dev

## Submission type

- [x] New plugin
- [ ] Version update

## What changed

New tool plugin for Cotlet (https://cotlet.dev), a hosted MCP server and REST API that lets AI agents use apps with no API, signed in as the user. The plugin adds 4 tools that call Cotlet's documented REST API (https://cotlet.dev/docs/api):

- `list_apps`, `get_app`, `get_endpoint`: public discovery of the apps Cotlet supports, their endpoints and input schemas.
- `call_endpoint`: calls one Cotlet endpoint with the user's Cotlet API key.

## Risk level

- [ ] Low risk
- [x] Medium risk
- [ ] High risk

`call_endpoint` can perform write actions in third-party services through Cotlet and sends user-provided inputs to cotlet.dev.

## Required checks

- [x] I have read and followed the [Marketplace submission requirements](https://github.com/langgenius/dify-plugins/blob/main/docs/plugin-submission-requirements.md).
- [ ] I have read and comply with the Plugin Developer Agreement.
- [x] I tested this plugin on Dify Community Edition and Dify Cloud, or documented any limitation below.
- [x] The package contains only files needed at runtime.
- [x] The package does not contain secrets, local credentials, `.env` files, `.git` directories, virtual environments, caches, logs, or IDE files.
- [x] The package does not contain executables or bundled binaries, or I explained why they are required below.
- [x] The plugin README includes setup steps, usage instructions, required APIs or credentials, connection requirements, and the source repository link.
- [x] The plugin includes `PRIVACY.md` or a hosted privacy policy, and `manifest.yaml` references it.
- [x] All user-facing text is primarily in English, with any localized README files following the [i18n guidance](https://docs.dify.ai/en/develop-plugin/features-and-specs/plugin-types/multilingual-readme).

## Security and privacy notes

- The plugin only talks to one fixed host, `cotlet.dev` (declared in `network.domains`). The base URL is fixed; the user picks the app slug, HTTP method (GET/POST/PUT/PATCH/DELETE) and the path after the app slug. Paths containing `..`, `?`, `#`, `://` or spaces are rejected, so requests cannot leave `https://cotlet.dev/api/v1/`.
- Credential: one secret field (Cotlet API key), sent only as `Authorization: Bearer` to cotlet.dev. It is never logged or returned in error messages. Requests have timeouts.
- Disclosure about the service behind the API: Cotlet's own backend operates third-party apps through the user's signed-in session (a cloud browser session the user connects on cotlet.dev). The plugin does not automate browsers, store sessions or handle passwords; it only calls Cotlet's REST API. Actions that reach other people (publish, message, email) are held by Cotlet for the account owner's approval by default and return `202` with an `approval_url`.
- Cotlet is an independent service, not affiliated with the apps it integrates. No third-party logos are used.

## Local validation

```
dify plugin package . -o cotlet.difypkg
INFO plugin packaged successfully output_path=cotlet.difypkg

python3 validator/validate-difypkg.py cotlet.difypkg --pr-body-file PR-BODY.md
manifest_metadata, readme_metadata, package_dependencies, python_compile: PASS (blocking)
python_safety, prohibited_financial_activity, access_domains, dependency_vulnerabilities: PASS (warning)

python tests/smoke_test.py   # live against https://cotlet.dev/api/v1
ALL OK (discovery tools, credential validation with a real and a fake key, call_endpoint with a real key)

Live test with a real account on a Skool test group: list_groups, get_group, list_categories, list_posts returned 200; create_post returned 202 pending with approval_url (held for owner approval, as designed).
```

## Reviewer notes

- Limitation: tested with the Dify plugin SDK locally (tools invoked against the live Cotlet API, credential validation with a real and a fake key). Not yet installed on Dify Community Edition or Dify Cloud.
- No dedicated "who am I" endpoint exists in Cotlet's API, so credential validation calls an authenticated lookup (`GET /api/v1/calls/{uuid}`): `401` means the key is rejected.
