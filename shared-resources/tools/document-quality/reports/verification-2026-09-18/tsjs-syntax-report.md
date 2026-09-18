# TypeScript / JavaScript syntax report

Parser: TypeScript 5.9.3, createSourceFile().parseDiagnostics. Scope: 1166 fences from the canonical manifest.

The fence language alone chooses the parser. No TSX fallback, fragment wrapper, synthetic imports or execution is used. A syntax PASS does not establish package types, runtime behavior, React Hook correctness or framework integration. ArkTS requires the Harmony toolchain.

| Status | Blocks |
| --- | ---: |
| PASS_SYNTAX | 1165 |
| NOT_VERIFIED_ARKTS | 1 |

## Remaining diagnostics

None.

## Reproduce

Install TypeScript 5.9.3 in a separate tools directory and set TYPESCRIPT_PATH to that directory’s node_modules/typescript. From the repository root run:

    python shared-resources/tools/code-block-verify/extract_blocks.py .
    node shared-resources/tools/code-block-verify/verify_tsjs_syntax.mjs shared-resources/tools/code-block-verify/manifest.jsonl

The optional second argument selects an output directory. Extraction rules, including nested fences and archive exclusions, come from extract_blocks.py. Each result contains the exact manifest content SHA-256.
