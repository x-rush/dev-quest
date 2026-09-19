// Execute marked, complete documentation programs verbatim under Node.
// No source wrapping, synthesized globals, third-party dependencies or network.
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';

const major = Number(process.versions.node.split('.')[0]);
const requiredGlobals = ['FormData', 'Response', 'structuredClone'];
const missingGlobals = requiredGlobals.filter((name) => typeof globalThis[name] !== 'function');
if (major < 24 || missingGlobals.length > 0 || typeof globalThis.Response?.json !== 'function') {
  console.error(`ENVIRONMENT_NOT_SUPPORTED: expected Node 24+ with native Web APIs; received ${process.version} at ${process.execPath}.`);
  if (missingGlobals.length > 0) console.error(`Missing APIs: ${missingGlobals.join(', ')}`);
  console.error('Select the intended Node executable explicitly. No examples were run and no evidence report was overwritten.');
  process.exit(2);
}

const root = resolve(dirname(fileURLToPath(import.meta.url)), '../../..');
const output = resolve(process.argv[2] ?? resolve(root,
  'shared-resources/tools/document-quality/reports/frontend-foundations.json'));
const documents = [
  '02-nextjs-frontend/reference/language-concepts/09-js-core-semantics.md',
  '02-nextjs-frontend/reference/language-concepts/10-web-platform-apis.md',
  '03-tanstack-stack/reference/library-guides/03-language-web-foundations.md',
];
const expectations = new Map([
  ['object-lifetimes', 'true,false\ntrue\ntrue\n1,0\n1,0\n'],
  ['bindings', '2\n0,1,2\n7\nundefined\n8\n'],
  ['iteration', '0,1,2\n\na:1,b:2\n'],
  ['url-form', 'a+b & 中\njs,ts\n2\n3\n'],
  ['response-contract', 'Learn\nError:HTTP 404\nTypeError:invalid task\nTypeError\n'],
  ['clone', '1\ntrue\n0,3\nDataCloneError\n'],
  ['search-input', '1:js,ts\n3:js\ninvalid page\ninvalid page\ninvalid page\nduplicate page\n'],
  ['immutable-data', 'false,true\nfalse,true\ntrue\ntrue\ntrue\n'],
]);
const hash = (value) => createHash('sha256').update(value).digest('hex');
const seen = new Set();
const results = [];
for (const path of documents) {
  const raw = await readFile(resolve(root, path), 'utf8');
  const text = raw.replace(/\r\n/g, '\n');
  const pattern = /<!-- foundation-case: ([a-z-]+) -->\n```js\n([\s\S]*?)\n```/g;
  const markers = [...text.matchAll(/<!-- foundation-case:/g)].length;
  const matches = [...text.matchAll(pattern)];
  if (markers !== matches.length) throw new Error(`Malformed case marker in ${path}`);
  for (const match of matches) {
    const [, id, code] = match;
    if (!expectations.has(id) || seen.has(id)) throw new Error(`Unknown or duplicate case: ${id}`);
    seen.add(id);
    const result = spawnSync(process.execPath, ['--input-type=module'], {
      input: code, encoding: 'utf8', timeout: 10_000,
      maxBuffer: 1024 * 1024, windowsHide: true,
    });
    const stdout = (result.stdout ?? '').replace(/\r\n/g, '\n');
    const stderr = result.stderr ?? '';
    const passed = result.status === 0 && stdout === expectations.get(id) && stderr === '';
    results.push({
      id, source: path, line: text.slice(0, match.index).split('\n').length + 2,
      source_sha256: hash(text), code_sha256: hash(code),
      status: passed ? 'PASS' : 'FAIL', code, expected_stdout: expectations.get(id),
      stdout, stderr, exit_code: result.status, signal: result.signal,
      error: result.error?.message ?? null,
    });
    console.log(`${passed ? 'PASS' : 'FAIL'} ${id}`);
  }
}
for (const id of expectations.keys()) {
  if (!seen.has(id)) throw new Error(`Required example missing: ${id}`);
}
await mkdir(dirname(output), { recursive: true });
await writeFile(output, JSON.stringify({
  generated_at: new Date().toISOString(),
  runtime: { node: process.version, platform: process.platform, arch: process.arch },
  command: 'node shared-resources/tools/document-quality/verify_frontend_foundations.mjs',
  scope: 'Eight marked complete programs, executed verbatim with Node; no browser UI, network, SSR or framework build validation.',
  source_hash_normalization: 'UTF-8 document with CRLF normalized to LF',
  passed: results.filter((entry) => entry.status === 'PASS').length,
  total: results.length, results,
}, null, 2) + '\n');
if (results.some((entry) => entry.status !== 'PASS')) process.exitCode = 1;
