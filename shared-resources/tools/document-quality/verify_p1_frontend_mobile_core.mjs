// Execute marked, self-contained P1 frontend/mobile documentation contracts.
// Cases are extracted verbatim; this intentionally excludes framework/device UI.
import { mkdtemp, readFile, rm, writeFile, mkdir } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { tmpdir } from 'node:os';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '../../..');
const reportDir = resolve(root, 'shared-resources/tools/document-quality/reports');
const cases = [
  ['next-title-boundary', '02-nextjs-frontend/reference/language-concepts/03-typescript-types.md', 'js', 'Case.mjs', 'node:24-bookworm-slim', 'node Case.mjs', 'A|缺少标题|缺少标题|标题必须是非空文本|标题必须是非空文本\n'],
  ['tanstack-query-key-factory', '03-tanstack-stack/reference/language-concepts/05-typescript-patterns.md', 'js', 'Case.mjs', 'node:24-bookworm-slim', 'node Case.mjs', '[["todos"],["todos","list"],["todos","detail",3],["todos","list",{"page":2,"status":"open"}]]\n'],
  ['kotlin-sequence-short-circuit', '05-kotlin-compose/reference/language-concepts/10-sequences.md', 'kotlin', 'Case.kt', process.env.DEV_QUEST_KOTLIN_IMAGE ?? 'dev-quest-validation:local', 'kotlinc Case.kt -include-runtime -d /tmp/case.jar && java -jar /tmp/case.jar', 'Sequence short-circuit contracts passed\n'],
  ['swift-optionals-collections', '06-swift-swiftui/reference/language-concepts/02-optionals-collections.md', 'swift', 'Case.swift', 'swift:6.3.3-noble', 'swift Case.swift', 'Swift optional and collection contracts passed\n'],
];
const sha = (value) => createHash('sha256').update(value).digest('hex');

async function runCase([id, source, language, filename, image, command, expected]) {
  const text = (await readFile(resolve(root, source), 'utf8')).replace(/\r\n/g, '\n');
  const expression = new RegExp('<!-- p1-runtime-case: ' + id + ' -->\\n```' + language + '\\n([\\s\\S]*?)\\n```');
  const matches = [...text.matchAll(new RegExp(expression, 'g'))];
  if (matches.length !== 1) throw new Error(`Expected one complete marked program: ${id}`);
  const code = matches[0][1];
  const work = await mkdtemp(resolve(tmpdir(), 'devquest-p1-core-'));
  try {
    await writeFile(resolve(work, filename), `${code}\n`, 'utf8');
    const args = ['run', '--rm', '--network', 'none', '--read-only', '--cap-drop', 'ALL', '--pids-limit', '256', '--memory', '1g', '--cpus', '2', '--tmpfs', '/tmp:rw,exec,nosuid,size=512m', '-e', 'HOME=/tmp', '-v', `${work}:/work:ro`, '-w', '/work', image, 'sh', '-c', command];
    const result = spawnSync('docker', args, { encoding: 'utf8', timeout: 120_000, windowsHide: true });
    const stdout = (result.stdout ?? '').replace(/\r\n/g, '\n');
    return { id, source, language, source_sha256: sha(text), extracted_code_sha256: sha(code), image, command, expected_stdout: expected, stdout, stderr: result.stderr ?? '', exit_code: result.status, error: result.error?.message ?? null, status: result.status === 0 && stdout === expected && !(result.stderr ?? '') ? 'PASS' : 'FAIL' };
  } finally { await rm(work, { recursive: true, force: true }); }
}

const results = [];
for (const item of cases) { const result = await runCase(item); results.push(result); console.log(`${result.id} ${result.status}`); }
const report = { scope: 'Four exact marked P1 core/standard-library programs: Next.js-adjacent input boundary, TanStack query-key factory, Kotlin Sequence, and Swift Optional/collections.', execution: 'Docker containers: no network, read-only root filesystem, capabilities dropped, bounded resources.', not_verified: ['TypeScript compiler diagnostics', 'TanStack Query invalidation or cache runtime', 'Next.js browser, SSR, routing, or build', 'Compose/Android runtime', 'SwiftUI/iOS runtime'], passed: results.filter((x) => x.status === 'PASS').length, total: results.length, results };
await mkdir(reportDir, { recursive: true });
await writeFile(resolve(reportDir, 'p1-frontend-mobile-core-runtime.json'), `${JSON.stringify(report, null, 2)}\n`);
const rows = results.map((x) => `| \`${x.id}\` | \`${x.source}\` | \`${x.image}\` | ${x.status} |`).join('\n');
await writeFile(resolve(reportDir, 'p1-frontend-mobile-core-runtime.md'), `# P1 frontend/mobile core runtime validation\n\nMarked, complete programs were extracted unchanged and run in network-disabled containers.\n\n| Case | Source | Runtime | Status |\n|---|---|---|---|\n${rows}\n\n## Boundary\n\nThis evidence covers only the listed portable logic. It excludes TypeScript type-checking, TanStack Query client behavior, browser/SSR execution, Compose/Android, and SwiftUI/iOS behavior.\n`);
if (report.passed !== report.total) process.exitCode = 1;
