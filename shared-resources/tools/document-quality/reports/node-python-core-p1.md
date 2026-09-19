# Node/Python P1 Core Reference Runtime Check

Generated: 2026-09-19T12:52:20.579Z

Result: **4/4 passed**.

## Scope

Four named, complete programs extracted unchanged from two Node and two Python P1 core-reference documents. They run in pre-existing local Docker images with network disabled, a read-only root filesystem and a temporary input bind mount. Only the listed contracts execute; no whole-document, network, database, permission, platform, or framework coverage is claimed.

## Results

| ID | Source | Runtime | Exit | Status |
| --- | --- | --- | ---: | --- |
| node-async-combinators | `09-nodejs-backend/reference/language-concepts/02-async-api.md` | `v24.21.0` | 0 | PASS |
| node-core-file-url | `09-nodejs-backend/reference/library-guides/01-core-modules.md` | `v24.21.0` | 0 | PASS |
| python-builtins-iteration | `10-python-discovery/reference/language-concepts/02-built-in-functions.md` | `Python 3.14.7` | 0 | PASS |
| python-stdlib-contracts | `10-python-discovery/reference/library-guides/01-standard-library.md` | `Python 3.14.7` | 0 | PASS |

The JSON companion preserves source and extracted-code SHA-256 values, expected and actual stdout, stderr, commands, and runtime versions. This report does not claim whole-document, network, database, permission, platform, or framework coverage.
