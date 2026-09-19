# Frontend and mobile P1 runtime validation

Five exact marked programs: Next URL input, TanStack Query cache identity, React JSX child structure used by React Native, Kotlin collections, and Swift control-flow keywords.

| Case | Source | Runtime | Status |
| --- | --- | --- | --- |
| `next-route-url-contract` | `02-nextjs-frontend/basics/04-layouts-routing.md` | `node:24-bookworm-slim` | PASS |
| `tanstack-query-key-contract` | `03-tanstack-stack/basics/03-query-fundamentals.md` | `node:24-bookworm-slim` | PASS |
| `react-native-jsx-children-contract` | `04-multiplatform-apps/basics/03-components-jsx.md` | `node:24-bookworm-slim` | PASS |
| `kotlin-collections-contract` | `05-kotlin-compose/reference/language-concepts/02-null-safety-collections.md` | `dev-quest-validation:local` | PASS |
| `swift-control-flow-keywords-contract` | `06-swift-swiftui/reference/language-concepts/01-swift-keywords.md` | `swift:6.3.3-noble` | PASS |

## Boundary

- Next.js server, route-file build, SSR, or browser navigation
- React Native Android/iOS renderer, Flexbox, accessibility, or device input
- React mounting, Query Provider lifecycle, hydration, and real network retry
- Compose/Android and SwiftUI/iOS lifecycle behavior
