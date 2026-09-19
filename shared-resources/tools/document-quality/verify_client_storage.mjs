// Node 24+, dependency workspace: react, react-dom, jsdom, @testing-library/react.
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';

if (!process.argv[2] || Number(process.versions.node.split('.')[0]) < 24) {
  throw new Error('Usage: Node 24+ verify_client_storage.mjs <dependency-workspace> [report]');
}
const root = resolve(dirname(fileURLToPath(import.meta.url)), '../../..');
const workspace = resolve(process.argv[2]);
const require = createRequire(resolve(workspace, 'package.json'));
const source = '02-nextjs-frontend/testing/01-unit-testing.md';
const text = (await readFile(resolve(root, source), 'utf8')).replace(/\r\n/g, '\n');
const blocks = [...text.matchAll(/^```typescript\n(\/\/ src\/hooks\/use-local-storage\.ts\n[\s\S]*?)^```/gm)];
assert.equal(blocks.length, 1, 'Expected exactly one Hook source block');
const code = blocks[0][1];
const folder = resolve(workspace, 'client-storage-verification');
await mkdir(folder, { recursive: true });
await writeFile(resolve(folder, 'package.json'), '{"type":"module"}\n');
const modulePath = resolve(folder, 'use-local-storage.ts');
await writeFile(modulePath, code);
const sourceUrl = pathToFileURL(modulePath).href;
const results = [];
const server = `import { createElement } from 'react';
import { renderToString } from 'react-dom/server';
import assert from 'node:assert/strict';
import { useLocalStorage } from ${JSON.stringify(sourceUrl)};
function Probe() { const [value] = useLocalStorage('key', 'server'); return createElement('span', null, value); }
assert.equal(renderToString(createElement(Probe)), '<span>server</span>');`;
await writeFile(resolve(folder, 'server.mjs'), server);
const ssr = spawnSync(process.execPath, ['server.mjs'], { cwd: folder, encoding: 'utf8', timeout: 15000 });
assert.equal(ssr.status, 0, ssr.stderr);
results.push({ case: 'Node server renderer uses initial value without window', status: 'PASS' });

const { JSDOM } = require('jsdom');
const dom = new JSDOM('<!doctype html><html><body></body></html>', { url: 'https://example.test/' });
for (const key of ['window', 'document', 'navigator', 'HTMLElement', 'MutationObserver']) {
  Object.defineProperty(globalThis, key, { value: dom.window[key], configurable: true });
}
globalThis.IS_REACT_ACT_ENVIRONMENT = true;
const { renderHook, act, cleanup } = require('@testing-library/react');
const { useLocalStorage } = await import(sourceUrl);
try {
  let hook = renderHook(() => useLocalStorage('counter', 0));
  act(() => { hook.result.current[1](n => n + 1); hook.result.current[1](n => n + 1); });
  assert.equal(hook.result.current[0], 2);
  assert.equal(dom.window.localStorage.getItem('counter'), '2');
  cleanup();
  hook = renderHook(() => useLocalStorage('counter', 0));
  assert.equal(hook.result.current[0], 2);
  cleanup();
  results.push({ case: 'Batched updates persist 2 and remount reads persisted value', status: 'PASS' });

  dom.window.localStorage.setItem('broken', '{');
  const oldError = console.error;
  const errors = [];
  console.error = (...args) => errors.push(args);
  try {
    hook = renderHook(() => useLocalStorage('broken', 'fallback'));
    assert.equal(hook.result.current[0], 'fallback');
    assert.equal(dom.window.localStorage.getItem('broken'), '{');
    assert.equal(errors.length, 1);
    cleanup();
    results.push({ case: 'Invalid JSON returns fallback without overwriting data', status: 'PASS' });

    hook = renderHook(() => useLocalStorage('quota', 'initial'));
    const originalSet = dom.window.Storage.prototype.setItem;
    dom.window.Storage.prototype.setItem = () => { throw new Error('quota'); };
    try {
      act(() => hook.result.current[1]('changed'));
      assert.equal(hook.result.current[0], 'initial');
      assert.equal(dom.window.localStorage.getItem('quota'), null);
    } finally { dom.window.Storage.prototype.setItem = originalSet; }
    act(() => hook.result.current[1](previous => previous + '-retry'));
    assert.equal(hook.result.current[0], 'initial-retry');
    assert.equal(dom.window.localStorage.getItem('quota'), '"initial-retry"');
    results.push({ case: 'Write failure preserves state; retry starts from last successful value', status: 'PASS' });
  } finally { console.error = oldError; }
} finally { cleanup(); dom.window.close(); }
const report = resolve(process.argv[3] ?? resolve(root, 'shared-resources/tools/document-quality/reports/client-storage.json'));
await mkdir(dirname(report), { recursive: true });
await writeFile(report, JSON.stringify({ generated_at: new Date().toISOString(), node: process.version,
  source, source_sha256: createHash('sha256').update(text).digest('hex'),
  code_sha256: createHash('sha256').update(code).digest('hex'), code,
  dependencies: Object.fromEntries(['react', 'react-dom', 'jsdom', '@testing-library/react'].map(name => [name, require(name + '/package.json').version])),
  scope: 'Exact Hook source executed with real React and jsdom, plus a separate Node server renderer. No browser hydration, Next build, cross-tab storage or dynamic key support.',
  passed: results.length, results,
}, null, 2) + '\n');
console.log(`${results.length}/${results.length} client storage cases passed`);
