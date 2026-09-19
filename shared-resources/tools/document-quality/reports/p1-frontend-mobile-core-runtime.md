# P1 frontend/mobile core runtime validation

Marked, complete programs were extracted unchanged and run in network-disabled containers.

| Case | Source | Runtime | Status |
|---|---|---|---|
| `next-title-boundary` | `02-nextjs-frontend/reference/language-concepts/03-typescript-types.md` | `node:24-bookworm-slim` | PASS |
| `tanstack-query-key-factory` | `03-tanstack-stack/reference/language-concepts/05-typescript-patterns.md` | `node:24-bookworm-slim` | PASS |
| `kotlin-sequence-short-circuit` | `05-kotlin-compose/reference/language-concepts/10-sequences.md` | `dev-quest-validation:local` | PASS |
| `swift-optionals-collections` | `06-swift-swiftui/reference/language-concepts/02-optionals-collections.md` | `swift:6.3.3-noble` | PASS |

## Boundary

This evidence covers only the listed portable logic. It excludes TypeScript type-checking, TanStack Query client behavior, browser/SSR execution, Compose/Android, and SwiftUI/iOS behavior.
