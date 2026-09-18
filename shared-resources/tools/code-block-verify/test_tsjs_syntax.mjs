import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';

test('parser respects fence labels and does not silently repair fragments', () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'dq-syntax-test-'));
  const blocks = [
    { id: '1', lang: 'ts', content: 'const node = <span />;\n' },
    { id: '2', lang: 'tsx', content: 'const node = <span />;\n' },
    { id: '3', lang: 'jsx', content: '<span /><span />\n' },
    { id: '4', lang: 'arkts', content: '@Entry struct Page {}\n' },
  ].map(b => ({ file: 'fixture.md', start: 1, end: 3, ...b }));
  const manifest = path.join(dir, 'manifest.jsonl');
  try {
    fs.writeFileSync(manifest, blocks.map(b => JSON.stringify(b)).join('\n'));
    const run = spawnSync(process.execPath, [path.join(import.meta.dirname, 'verify_tsjs_syntax.mjs'), manifest, dir], { encoding: 'utf8' });
    assert.equal(run.status, 1, run.stderr);
    const rows = fs.readFileSync(path.join(dir, 'tsjs-syntax-results.jsonl'), 'utf8').trim().split('\n').map(JSON.parse);
    assert.deepEqual(rows.map(r => r.status), ['NEEDS_REVIEW', 'PASS_SYNTAX', 'NEEDS_REVIEW', 'NOT_VERIFIED_ARKTS']);
    assert.equal(rows[1].source_sha256, createHash('sha256').update(blocks[1].content).digest('hex'));
  } finally {
    for (const name of ['manifest.jsonl', 'tsjs-syntax-results.jsonl', 'tsjs-syntax-report.md']) {
      const file = path.join(dir, name);
      if (fs.existsSync(file)) fs.unlinkSync(file);
    }
    fs.rmdirSync(dir);
  }
});
