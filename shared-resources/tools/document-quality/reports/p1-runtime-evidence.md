# P1 runtime evidence

Every program below was extracted unchanged from its source Markdown body and executed in a network-disabled container.

| Case | Source | Runtime | Status |
|---|---|---|---|
| `next-js-bindings` | `02-nextjs-frontend/reference/language-concepts/09-js-core-semantics.md` | `node:24-bookworm-slim` | PASS |
| `tanstack-query-key-factory` | `03-tanstack-stack/reference/language-concepts/05-typescript-patterns.md` | `node:24-bookworm-slim` | PASS |
| `react-native-amount-input` | `04-multiplatform-apps/reference/language-concepts/02-components-props.md` | `node:24-bookworm-slim` | PASS |
| `react-native-deeplink-input` | `04-multiplatform-apps/reference/language-concepts/01-rn-core-api.md` | `node:24-bookworm-slim` | PASS |
| `kotlin-sequence-short-circuit` | `05-kotlin-compose/reference/language-concepts/10-sequences.md` | `dev-quest-validation:local` | PASS |
| `swift-optionals-collections` | `06-swift-swiftui/reference/language-concepts/02-optionals-collections.md` | `swift:6.3.3-noble` | PASS |

## Reproduce

`node shared-resources/tools/document-quality/verify-p1-runtime-evidence.mjs`

## Boundary

This evidence covers only the listed portable language or standard-library contracts. It does not claim framework, browser, device, Android, iOS, or SwiftUI validation.
