# Node/Python P1 Final Runtime Check

Generated: 2026-09-19T13:30:30.206Z

Result: **4/4 passed**.

## Scope

Four named, complete programs extracted unchanged from two Node and two Python P1 reference documents not covered by the earlier core and follow-up checks. They run in pre-existing local Docker images with network disabled, a read-only root filesystem and a temporary input bind mount. Only the listed language and standard-library contracts execute; no whole-document, network, database, permission, platform, or framework coverage is claimed.

## Results

| ID | Source | Runtime | Exit | Status |
| --- | --- | ---: | ---: | --- |
| node-modern-syntax-contracts | `09-nodejs-backend/reference/language-concepts/01-js-modern-syntax.md` | `v24.21.0` | 0 | PASS |
| node-globals-response-contracts | `09-nodejs-backend/reference/language-concepts/09-globals-reference.md` | `v24.21.0` | 0 | PASS |
| python-keywords-control-flow | `10-python-discovery/reference/language-concepts/01-python-keywords.md` | `Python 3.14.7` | 0 | PASS |
| python-os-sys-environment-contracts | `10-python-discovery/reference/library-guides/04-os-sys.md` | `Python 3.14.7` | 0 | PASS |

The JSON companion preserves source and extracted-code SHA-256 values, expected and actual stdout, stderr, commands, and runtime versions.
