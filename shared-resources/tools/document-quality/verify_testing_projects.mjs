// Verify selected documentation source modules verbatim with Node's TS stripping.
// This verifies behavior, not a TypeScript type check or a framework/device build.
import { readFile, writeFile, mkdtemp, mkdir, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { resolve, dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';

if (Number(process.versions.node.split('.')[0]) < 24) {
  throw new Error(`Node 24+ required; found ${process.version}. No report overwritten.`);
}
const root = resolve(dirname(fileURLToPath(import.meta.url)), '../../..');
const report = resolve(process.argv[2] ?? join(root, 'shared-resources/tools/document-quality/reports/testing-projects.json'));
const hash = (text) => createHash('sha256').update(text).digest('hex');
const cases = [
  {
    id: 'next-utility-contracts',
    source: '02-nextjs-frontend/testing/01-unit-testing.md',
    firstLine: '// src/lib/utils/date.ts',
    test: `import { formatDate, truncateText, generateSlug, isValidEmail } from './source.ts';
test('UTC date and invalid input', () => {
  assert.equal(formatDate('2025-01-01T01:00:00+08:00'), '2024年12月31日');
  assert.throws(() => formatDate('not-a-date'), RangeError);
});
test('truncation counts code points and validates length', () => {
  assert.equal(truncateText('这是一个很长的文本，需要被截断', 10), '这是一个很长的文本，...');
  assert.equal(truncateText('😀ab', 1), '😀...');
  assert.equal(truncateText('a', 0), '...');
  assert.equal(truncateText('', 0), '');
  assert.equal(truncateText('😀a', 2), '😀a');
  for (const n of [-1, 0.5, NaN, Infinity]) assert.throws(() => truncateText('a', n), RangeError);
});
test('slug and basic email boundaries', () => {
  assert.equal(generateSlug('--Hello--'), 'hello');
  assert.equal(generateSlug('React & Next.js'), 'react-nextjs');
  assert.equal(generateSlug('中文'), '');
  assert.equal(isValidEmail('a+b@example.org'), true);
  assert.equal(isValidEmail(' a@example.org'), false);
});`,
  },
  {
    id: 'tanstack-optimistic-move',
    source: '03-tanstack-stack/testing/01-unit-testing.md',
    firstLine: '// src/features/board/optimistic.ts',
    test: `import { applyMove } from './source.ts';
const base = { columns: [{ id:'c1', title:'todo', cardIds:['a','b'] }, { id:'c2', title:'doing', cardIds:[] }], cards: { a:{id:'a', title:'A', columnId:'c1', version:1}, b:{id:'b', title:'B', columnId:'c1', version:1} } };
function freeze(value) { Object.values(value).forEach(v => { if (v && typeof v === 'object') freeze(v); }); return Object.freeze(value); }
freeze(base);
test('cross-column move does not mutate frozen source', () => {
  const next = applyMove(base, 'a', 'c2', 0);
  assert.deepEqual(next.columns.map(c => c.cardIds), [['b'],['a']]);
  assert.equal(next.cards.a.columnId, 'c2');
  assert.equal(next.cards.b, base.cards.b);
  assert.deepEqual(base.columns[0].cardIds, ['a','b']);
});
test('missing card, missing target and invalid index preserve original', () => {
  assert.equal(applyMove(base, 'ghost', 'c2', 0), base);
  assert.equal(applyMove(base, 'a', 'missing', 0), base);
  for (const index of [-1, 0.5, NaN, Infinity, 1]) assert.equal(applyMove(base, 'a', 'c2', index), base);
});
test('same-column index is measured after removal', () => {
  assert.deepEqual(applyMove(base, 'a', 'c1', 1).columns[0].cardIds, ['b','a']);
  assert.equal(applyMove(base, 'a', 'c1', 2), base);
});`,
  },
  {
    id: 'tanstack-http-contracts',
    source: '03-tanstack-stack/projects/01-todo-app.md',
    firstLine: '// src/api/todos.ts',
    test: `import { todoApi, todoKeys } from './source.ts';
test('JSON list and hierarchical keys', async () => {
  mock.method(globalThis, 'fetch', async () => Response.json([{id:1,title:'a',done:false}]));
  try {
    assert.deepEqual(await todoApi.list(), [{id:1,title:'a',done:false}]);
    assert.deepEqual(todoKeys.detail(7), ['todos','detail',7]);
    assert.deepEqual(todoKeys.detail(7).slice(0,2), todoKeys.details());
  } finally { mock.restoreAll(); }
});
test('204 delete succeeds without parsing JSON', async () => {
  const calls = [];
  mock.method(globalThis, 'fetch', async (...args) => { calls.push(args); return new Response(null, {status:204}); });
  try {
    assert.equal(await todoApi.remove(1), undefined);
    assert.deepEqual(calls, [['/api/todos/1', {method:'DELETE'}]]);
  } finally { mock.restoreAll(); }
});
test('HTTP failures and invalid JSON reject', async () => {
  mock.method(globalThis, 'fetch', async () => new Response('', {status:500}));
  try {
    await assert.rejects(todoApi.list(), /请求失败 500/);
    await assert.rejects(todoApi.remove(1), /请求失败 500/);
  } finally { mock.restoreAll(); }
  mock.method(globalThis, 'fetch', async () => new Response('not json', {status:200}));
  try { await assert.rejects(todoApi.list(), SyntaxError); } finally { mock.restoreAll(); }
});`,
  },
  {
    id: 'rn-todo-domain',
    source: '04-multiplatform-apps/projects/01-todo-app.md',
    firstLine: '// utils/todos.ts',
    test: `import { createTodo, toggleTodo, remainingCount } from './source.ts';
test('normalized creation and rejected input', () => {
  assert.deepEqual(createTodo('  买菜  ', 'a', 0), {id:'a',title:'买菜',done:false,createdAt:0});
  assert.equal(createTodo('  ', 'a', 0), null);
  assert.throws(() => createTodo('a', '', 0), RangeError);
  for (const time of [NaN, Infinity, -1]) assert.throws(() => createTodo('a', 'a', time), RangeError);
});
test('toggle is immutable and missing IDs preserve source', () => {
  const a = Object.freeze(createTodo('A', 'a', 0));
  const b = Object.freeze(createTodo('B', 'b', 0));
  const source = Object.freeze([a,b]);
  const next = toggleTodo(source, 'a');
  assert.equal(next[0].done, true);
  assert.equal(source[0].done, false);
  assert.equal(next[1], b);
  assert.equal(toggleTodo(source, 'missing'), source);
  assert.deepEqual(toggleTodo(next, 'a'), source);
  assert.equal(remainingCount(next), 1);
  assert.equal(remainingCount([]), 0);
});`,
  },
];
const results = [];
const work = await mkdtemp(join(tmpdir(), 'dev-quest-testing-'));
try {
  await writeFile(join(work, 'package.json'), '{"type":"module"}\n');
  for (const spec of cases) {
    const document = (await readFile(join(root, spec.source), 'utf8')).replace(/\r\n/g, '\n');
    const blocks = [...document.matchAll(/^```(?:ts|typescript)\n([\s\S]*?)^```\s*$/gm)]
      .filter(match => match[1].split('\n')[0] === spec.firstLine);
    if (blocks.length !== 1) throw new Error(`Expected exactly one ${spec.firstLine} block in ${spec.source}`);
    const [block] = blocks;
    const code = block[1];
    const folder = join(work, spec.id);
    await mkdir(folder);
    await writeFile(join(folder, 'source.ts'), code);
    const testCode = `import test, { mock } from 'node:test';\nimport assert from 'node:assert/strict';\n${spec.test}\n`;
    await writeFile(join(folder, 'contracts.test.mjs'), testCode);
    const run = spawnSync(process.execPath, ['--test', '--test-reporter=tap', 'contracts.test.mjs'], {
      cwd: folder, encoding: 'utf8', timeout: 15000, windowsHide: true,
    });
    const passed = run.status === 0;
    results.push({ id: spec.id, source: spec.source, source_line: document.slice(0, block.index).split('\n').length + 1,
      source_sha256: hash(document), code_sha256: hash(code), code, test_code: testCode,
      status: passed ? 'PASS' : 'FAIL', stdout: run.stdout, stderr: run.stderr,
      exit_code: run.status, error: run.error?.message ?? null });
    console.log(`${passed ? 'PASS' : 'FAIL'} ${spec.id}`);
  }
} finally { await rm(work, { recursive: true, force: true }); }
await mkdir(dirname(report), { recursive: true });
await writeFile(report, JSON.stringify({ generated_at: new Date().toISOString(), node: process.version,
  command: 'node shared-resources/tools/document-quality/verify_testing_projects.mjs',
  scope: 'Four exact documentation source blocks; 11 Node behavior tests. Only fetch is replaced explicitly for HTTP contract tests. Not Vitest/Jest setup, TS typecheck, React, SSR, browser, native MMKV or device validation.',
  source_hash_normalization: 'UTF-8 with CRLF normalized to LF',
  passed: results.filter(r => r.status === 'PASS').length, total: results.length, results }, null, 2) + '\n');
if (results.some(r => r.status !== 'PASS')) process.exitCode = 1;
