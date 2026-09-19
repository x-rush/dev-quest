import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const toolDirectory = resolve(fileURLToPath(new URL('.', import.meta.url)));
const repositoryRoot = resolve(toolDirectory, '../../..');
const reportDirectory = join(toolDirectory, 'reports');
const cases = [
  { id: 'next-product-guard', source: '02-nextjs-frontend/reference/language-concepts/07-type-narrowing-guards.md', language: 'js', image: 'node:24-bookworm-slim', command: ['node', 'Case.mjs'], expected: 'Product guard runtime contracts passed\n' },
  { id: 'tanstack-query-key-factory-core-api', source: '03-tanstack-stack/reference/language-concepts/01-query-core-api.md', language: 'js', image: 'node:24-bookworm-slim', command: ['node', 'Case.mjs'], expected: 'Query key factory contracts passed\n' },
  { id: 'react-native-detail-parameter-boundary', source: '04-multiplatform-apps/reference/language-concepts/04-typescript-patterns.md', language: 'js', image: 'node:24-bookworm-slim', command: ['node', 'Case.mjs'], expected: 'Detail parameter boundary contracts passed\n' },
  { id: 'kotlin-collection-operations', source: '05-kotlin-compose/reference/language-concepts/09-collections-operations.md', language: 'kotlin', image: 'dev-quest-validation:local', command: ['sh', '-lc', 'kotlinc Case.kt -include-runtime -d /tmp/case.jar && java -jar /tmp/case.jar'], expected: 'Collection operation contracts passed\n' },
  { id: 'swift-enum-pattern-matching', source: '06-swift-swiftui/reference/language-concepts/07-enums-pattern-matching.md', language: 'swift', image: 'swift:6.3.3-noble', command: ['swift', 'Case.swift'], expected: 'Enum pattern-matching contracts passed\n' },
];

const sha256 = (text) => createHash('sha256').update(text).digest('hex');

function extractCase(source, language) {
  const marker = '### 可直接提取的运行案例';
  const start = source.indexOf(marker);
  if (start < 0) throw new Error(`missing runtime-case heading for ${language}`);
  const match = source.slice(start).match(new RegExp('```' + language + '\\r?\\n([\\s\\S]*?)\\r?\\n```'));
  if (!match) throw new Error(`missing ${language} fence after runtime-case heading`);
  return match[1] + '\n';
}

function dockerRun(directory, image, command) {
  return execFileSync('docker', [
    'run', '--rm', '--network', 'none', '--read-only', '--cap-drop', 'ALL', '--pids-limit', '64', '--memory', '256m',
    '--tmpfs', '/tmp:rw,noexec,nosuid,size=64m', '-e', 'HOME=/tmp', '-e', 'XDG_CACHE_HOME=/tmp',
    '-v', `${directory}:/work:ro`, '-w', '/work', image, ...command,
  ], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] });
}

const results = cases.map((testCase) => {
  const source = readFileSync(join(repositoryRoot, testCase.source), 'utf8');
  const code = extractCase(source, testCase.language);
  const work = mkdtempSync(join(tmpdir(), 'dq-p1-runtime-'));
  const filename = testCase.language === 'kotlin' ? 'Case.kt' : testCase.language === 'swift' ? 'Case.swift' : 'Case.mjs';
  writeFileSync(join(work, filename), code, 'utf8');
  let stdout = '', stderr = '', exitCode = 0, error = null;
  try { stdout = dockerRun(work, testCase.image, testCase.command); }
  catch (failure) { exitCode = failure.status ?? 1; stdout = failure.stdout?.toString() ?? ''; stderr = failure.stderr?.toString() ?? ''; error = failure.message; }
  rmSync(work, { recursive: true, force: true });
  const status = exitCode === 0 && stdout === testCase.expected ? 'PASS' : 'FAIL';
  return {
    id: testCase.id, source: testCase.source, language: testCase.language, image: testCase.image,
    command: testCase.command.join(' '), source_sha256: sha256(source), extracted_code_sha256: sha256(code),
    expected_stdout: testCase.expected, stdout, stderr, exit_code: exitCode, error, status,
  };
});

const report = {
  scope: 'Five P1 queue core/standard-library pages without prior named runtime evidence; each program is extracted unchanged from its source body.',
  execution: 'Docker containers: network disabled, read-only root filesystem, capabilities dropped, and bounded PID/memory/tmpfs resources.',
  not_verified: ['TypeScript compiler diagnostics', 'Next.js browser, SSR, routing, or build', 'TanStack Query cache invalidation/refetch runtime', 'React Navigation or device runtime', 'Compose/Android runtime', 'SwiftUI/iOS runtime'],
  passed: results.filter((result) => result.status === 'PASS').length,
  total: results.length,
  results,
};

writeFileSync(join(reportDirectory, 'p1-next-web-mobile-runtime.json'), JSON.stringify(report, null, 2) + '\n');
const rows = results.map((result) => `| \`${result.id}\` | \`${result.source}\` | \`${result.image}\` | ${result.status} |`).join('\n');
writeFileSync(join(reportDirectory, 'p1-next-web-mobile-runtime.md'), `# P1 Next/web/mobile core runtime validation\n\nEach listed complete program was extracted unchanged from its source body and run in a network-disabled container.\n\n| Case | Source | Runtime | Status |\n|---|---|---|---|\n${rows}\n\n## Reproduce\n\n\`node shared-resources/tools/document-quality/verify-p1-next-web-mobile.mjs\`\n\n## Boundary\n\nThis evidence covers only the listed portable logic. It does not claim TypeScript type checking, Next.js browser/SSR/build behavior, TanStack Query cache behavior, React Native navigation/device behavior, Compose/Android, or SwiftUI/iOS validation.\n`);
if (report.passed !== report.total) process.exitCode = 1;
console.log(`P1 runtime validation: ${report.passed}/${report.total} passed`);
