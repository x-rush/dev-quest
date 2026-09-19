# Node/Python P1 Seventh Runtime Check

Generated: 2026-09-19T13:57:19.242Z

Result: **4/4 passed**.

## Scope

Four named, complete programs extracted unchanged from previously unrecorded P1 reference pages: Node language-keyword binding semantics, built-in collections, Node standard-library APIs, and Python control-flow keywords. They run in pre-existing local Docker images with network disabled, read-only root filesystem, no Linux capabilities, and a temporary read-only input mount. Only the listed contracts execute; no whole-document, HTTP-server, external-service, permission, platform, or framework coverage is claimed.

## Results

| ID | Source | Runtime | Exit | Status |
| --- | --- | --- | ---: | --- |
| node-keyword-binding-contracts | `09-nodejs-backend/reference/language-concepts/07-js-core-semantics.md` | `v24.21.0` | 0 | PASS |
| node-builtins-collection-contracts | `09-nodejs-backend/reference/language-concepts/08-type-coercion-collections.md` | `v24.21.0` | 0 | PASS |
| node-core-api-contracts | `09-nodejs-backend/reference/language-concepts/03-node-core-api.md` | `v24.21.0` | 0 | PASS |
| python-control-flow-keywords-contracts | `10-python-discovery/basics/05-control-flow.md` | `Python 3.14.7` | 0 | PASS |

The JSON companion preserves source and extracted-code SHA-256 values, expected and actual stdout, stderr, commands, and runtime version.
