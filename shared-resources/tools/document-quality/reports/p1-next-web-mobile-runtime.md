# P1 Next/web/mobile core runtime validation

Each listed complete program was extracted unchanged from its source body and run in a network-disabled container.

| Case | Source | Runtime | Status |
|---|---|---|---|
| `next-product-guard` | `02-nextjs-frontend/reference/language-concepts/07-type-narrowing-guards.md` | `node:24-bookworm-slim` | PASS |
| `tanstack-query-key-factory-core-api` | `03-tanstack-stack/reference/language-concepts/01-query-core-api.md` | `node:24-bookworm-slim` | PASS |
| `react-native-detail-parameter-boundary` | `04-multiplatform-apps/reference/language-concepts/04-typescript-patterns.md` | `node:24-bookworm-slim` | PASS |
| `kotlin-collection-operations` | `05-kotlin-compose/reference/language-concepts/09-collections-operations.md` | `dev-quest-validation:local` | PASS |
| `swift-enum-pattern-matching` | `06-swift-swiftui/reference/language-concepts/07-enums-pattern-matching.md` | `swift:6.3.3-noble` | PASS |

## Reproduce

`node shared-resources/tools/document-quality/verify-p1-next-web-mobile.mjs`

## Boundary

This evidence covers only the listed portable logic. It does not claim TypeScript type checking, Next.js browser/SSR/build behavior, TanStack Query cache behavior, React Native navigation/device behavior, Compose/Android, or SwiftUI/iOS validation.
