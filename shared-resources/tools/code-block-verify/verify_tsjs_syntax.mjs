#!/usr/bin/env node
// Static parsing only. Canonical extraction; no fence execution or implicit wrappers.
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { createHash } from 'node:crypto';
const require = createRequire(process.env.TYPESCRIPT_PATH ? path.join(path.resolve(process.env.TYPESCRIPT_PATH), 'package.json') : import.meta.url);
const ts = require('typescript');
const manifestPath = path.resolve(process.argv[2] ?? path.join(import.meta.dirname, 'manifest.jsonl'));
const outputDir = path.resolve(process.argv[3] ?? import.meta.dirname);
const kinds = { ts: ts.ScriptKind.TS, typescript: ts.ScriptKind.TS, tsx: ts.ScriptKind.TSX, jsx: ts.ScriptKind.JSX, js: ts.ScriptKind.JS, javascript: ts.ScriptKind.JS };
const blocks = fs.readFileSync(manifestPath, 'utf8').split(/\r?\n/).filter(Boolean).map(JSON.parse);
const rows = [];
for (const b of blocks) {
  if (!(b.lang in kinds) && b.lang !== 'arkts') continue;
  const source = b.content;
  const sf = b.lang === 'arkts' ? null : ts.createSourceFile(b.file + '.' + b.lang, source, ts.ScriptTarget.Latest, true, kinds[b.lang]);
  const diagnostics = sf ? sf.parseDiagnostics.map(d => ({ code: d.code, line: ts.getLineAndCharacterOfPosition(sf, d.start ?? 0).line + 1, message: ts.flattenDiagnosticMessageText(d.messageText, '\n') })) : [];
  rows.push({ id: b.id, file: b.file, start: b.start, end: b.end, lang: b.lang, source_sha256: createHash('sha256').update(source, 'utf8').digest('hex'), parser: b.lang === 'arkts' ? null : ts.ScriptKind[kinds[b.lang]], status: b.lang === 'arkts' ? 'NOT_VERIFIED_ARKTS' : diagnostics.length ? 'NEEDS_REVIEW' : 'PASS_SYNTAX', diagnostics });
}
fs.mkdirSync(outputDir, { recursive: true });
fs.writeFileSync(path.join(outputDir, 'tsjs-syntax-results.jsonl'), rows.map(r => JSON.stringify(r)).join('\n') + '\n');
const counts = {};
for (const r of rows) counts[r.status] = (counts[r.status] ?? 0) + 1;
const failures = rows.filter(r => r.status === 'NEEDS_REVIEW');
const report = [
  '# TypeScript / JavaScript syntax report', '',
  'Parser: TypeScript ' + ts.version + ', createSourceFile().parseDiagnostics. Scope: ' + rows.length + ' fences from the canonical manifest.', '',
  'The fence language alone chooses the parser. No TSX fallback, fragment wrapper, synthetic imports or execution is used. A syntax PASS does not establish package types, runtime behavior, React Hook correctness or framework integration. ArkTS requires the Harmony toolchain.', '',
  '| Status | Blocks |', '| --- | ---: |',
  ...Object.entries(counts).map(([k,v]) => '| ' + k + ' | ' + v + ' |'), '',
  '## Remaining diagnostics', '',
  ...(failures.length ? failures.map(r => '- ' + r.file + ':' + r.start + ': ' + r.diagnostics.map(d => 'TS' + d.code + ' at block line ' + d.line + ': ' + d.message).join('; ')) : ['None.']), '',
  '## Reproduce', '',
  'Install TypeScript 5.9.3 in a separate tools directory and set TYPESCRIPT_PATH to that directory’s node_modules/typescript. From the repository root run:', '',
  '    python shared-resources/tools/code-block-verify/extract_blocks.py .',
  '    node shared-resources/tools/code-block-verify/verify_tsjs_syntax.mjs shared-resources/tools/code-block-verify/manifest.jsonl', '',
  'The optional second argument selects an output directory. Extraction rules, including nested fences and archive exclusions, come from extract_blocks.py. Each result contains the exact manifest content SHA-256.', ''
];
fs.writeFileSync(path.join(outputDir, 'tsjs-syntax-report.md'), report.join('\n'));
console.log(JSON.stringify({ typescript: ts.version, blocks: rows.length, counts }));
process.exitCode = failures.length ? 1 : 0;