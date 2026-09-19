// Extract exact marked P1 contracts; framework/device behavior remains out of scope.
import { mkdtemp, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { dirname, resolve } from 'node:path';
import { tmpdir } from 'node:os';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '../../..');
const reportDir = resolve(root, 'shared-resources/tools/document-quality/reports');
const nodeModules = resolve(root, '..', 'verification-lab/node_modules');
// pnpm's Windows links retain their host-absolute target; expose that target too.
const workspace = resolve(root, '..');
const dockerWorkspace = workspace.replace(/^([A-Za-z]):/, (_, drive) => `/mnt/host/${drive.toLowerCase()}`).replaceAll('\\', '/');
const cases = [
  ['next-route-url-contract', '02-nextjs-frontend/basics/04-layouts-routing.md', 'js', 'Case.mjs', 'node:24-bookworm-slim', 'node Case.mjs', 'Next route URL contracts passed\n'],
  ['tanstack-query-key-contract', '03-tanstack-stack/basics/03-query-fundamentals.md', 'js', 'Case.mjs', 'node:24-bookworm-slim', 'node Case.mjs', 'TanStack query key contracts passed\n'],
  ['react-native-jsx-children-contract', '04-multiplatform-apps/basics/03-components-jsx.md', 'js', 'Case.mjs', 'node:24-bookworm-slim', 'node Case.mjs', 'React Native JSX children contracts passed\n'],
  ['kotlin-collections-contract', '05-kotlin-compose/reference/language-concepts/02-null-safety-collections.md', 'kotlin', 'Case.kt', process.env.DEV_QUEST_KOTLIN_IMAGE ?? 'dev-quest-validation:local', 'kotlinc Case.kt -include-runtime -d /tmp/case.jar && java -jar /tmp/case.jar', 'Kotlin collection contracts passed\n'],
  ['swift-control-flow-keywords-contract', '06-swift-swiftui/reference/language-concepts/01-swift-keywords.md', 'swift', 'Case.swift', 'swift:6.3.3-noble', 'swift Case.swift', 'Swift control-flow keyword contracts passed\n'],
];
const sha = (value) => createHash('sha256').update(value).digest('hex');

function extract(text, id, language) {
  const expression = new RegExp('<!-- dq-p1-case: ' + id + ' -->\\n```' + language + '\\n([\\s\\S]*?)\\n```', 'g');
  const matches = [...text.matchAll(expression)];
  if (matches.length !== 1) throw new Error(`${id}: expected exactly one marked ${language} block`);
  return matches[0][1];
}

async function runCase([id, source, language, filename, image, command, expected]) {
  const text = (await readFile(resolve(root, source), 'utf8')).replace(/\r\n/g, '\n');
  const code = extract(text, id, language);
  const work = await mkdtemp(resolve(tmpdir(), 'devquest-frontend-mobile-p1-'));
  try {
    await writeFile(resolve(work, filename), `${code}\n`, 'utf8');
    const args = ['run', '--rm', '--network', 'none', '--read-only', '--cap-drop', 'ALL', '--pids-limit', '256', '--memory', '1g', '--cpus', '2', '--tmpfs', '/tmp:rw,exec,nosuid,size=512m', '-e', 'HOME=/tmp', '-v', `${work}:/work:ro`, '-w', '/work'];
    if (language === 'js' && (id.includes('tanstack') || id.includes('react-native'))) args.push('-v', `${nodeModules}:/node_modules:ro`, '-v', `${workspace}:${dockerWorkspace}:ro`);
    args.push(image, 'sh', '-c', command);
    const result = spawnSync('docker', args, { encoding: 'utf8', timeout: 120_000, windowsHide: true });
    const stdout = (result.stdout ?? '').replace(/\r\n/g, '\n');
    return { case: id, source, source_sha256: sha(text), extracted_code_sha256: sha(code), image, command, expected_stdout: expected, stdout, stderr: result.stderr ?? '', exit_code: result.status, error: result.error?.message ?? null, status: result.status === 0 && stdout === expected && !(result.stderr ?? '') ? 'PASS' : 'FAIL' };
  } finally { await rm(work, { recursive: true, force: true }); }
}

const results = [];
for (const item of cases) { const result = await runCase(item); results.push(result); console.log(`${result.case} ${result.status}`); }
const scope = 'Five exact marked programs: Next URL input, TanStack Query cache identity, React JSX child structure used by React Native, Kotlin collections, and Swift control-flow keywords.';
const notVerified = ['Next.js server, route-file build, SSR, or browser navigation', 'React Native Android/iOS renderer, Flexbox, accessibility, or device input', 'React mounting, Query Provider lifecycle, hydration, and real network retry', 'Compose/Android and SwiftUI/iOS lifecycle behavior'];
const report = { scope, execution: 'Docker containers with no network, a read-only root filesystem, capabilities dropped, and bounded resources.', not_verified: notVerified, passed: results.filter((item) => item.status === 'PASS').length, total: results.length, results };
await mkdir(reportDir, { recursive: true });
await writeFile(resolve(reportDir, 'frontend-mobile-p1-runtime.json'), `${JSON.stringify(report, null, 2)}\n`);
const rows = results.map((item) => `| \`${item.case}\` | \`${item.source}\` | \`${item.image}\` | ${item.status} |`).join('\n');
await writeFile(resolve(reportDir, 'frontend-mobile-p1-runtime.md'), `# Frontend and mobile P1 runtime validation\n\n${scope}\n\n| Case | Source | Runtime | Status |\n| --- | --- | --- | --- |\n${rows}\n\n## Boundary\n\n${notVerified.map((item) => `- ${item}`).join('\n')}\n`);
if (report.passed !== report.total) process.exitCode = 1;
