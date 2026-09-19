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
  { id: 'next-js-bindings', marker: 'next-js-bindings', source: '02-nextjs-frontend/reference/language-concepts/09-js-core-semantics.md', language: 'js', image: 'node:24-bookworm-slim', command: ['node', 'Case.mjs'], expected: 'JavaScript binding contracts passed\n' },
  { id: 'tanstack-query-key-factory', marker: 'tanstack-query-key-factory', source: '03-tanstack-stack/reference/language-concepts/05-typescript-patterns.md', language: 'js', image: 'node:24-bookworm-slim', command: ['node', 'Case.mjs'], expected: '[["todos"],["todos","list"],["todos","detail",3],["todos","list",{"page":2,"status":"open"}]]\n' },
  { id: 'react-native-amount-input', marker: 'react-native-amount-input', source: '04-multiplatform-apps/reference/language-concepts/02-components-props.md', language: 'js', image: 'node:24-bookworm-slim', command: ['node', 'Case.mjs'], expected: 'React Native amount-input contracts passed\n' },
  { id: 'kotlin-sequence-short-circuit', marker: 'kotlin-sequence-short-circuit', source: '05-kotlin-compose/reference/language-concepts/10-sequences.md', language: 'kotlin', image: 'dev-quest-validation:local', command: ['sh', '-lc', 'kotlinc Case.kt -include-runtime -d /tmp/case.jar && java -jar /tmp/case.jar'], expected: 'Sequence short-circuit contracts passed\n' },
  { id: 'swift-optionals-collections', marker: 'swift-optionals-collections', source: '06-swift-swiftui/reference/language-concepts/02-optionals-collections.md', language: 'swift', image: 'swift:6.3.3-noble', command: ['swift', 'Case.swift'], expected: 'Swift optional and collection contracts passed\n' },
];

const sha256 = (text) => createHash('sha256').update(text).digest('hex');

function extractMarkedFence(source, marker, language) {
  const start = source.indexOf(`<!-- p1-runtime-case: ${marker} -->`);
  if (start < 0) throw new Error(`missing runtime marker: ${marker}`);
  const match = source.slice(start).match(new RegExp('```' + language + '\\r?\\n([\\s\\S]*?)\\r?\\n```'));
  if (!match) throw new Error(`missing ${language} fence after marker: ${marker}`);
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
  const code = extractMarkedFence(source, testCase.marker, testCase.language);
  const work = mkdtempSync(join(tmpdir(), 'dq-p1-evidence-'));
  const filename = testCase.language === 'kotlin' ? 'Case.kt' : testCase.language === 'swift' ? 'Case.swift' : 'Case.mjs';
  writeFileSync(join(work, filename), code, 'utf8');
  let stdout = '', stderr = '', exitCode = 0, error = null;
  try { stdout = dockerRun(work, testCase.image, testCase.command); }
  catch (failure) { exitCode = failure.status ?? 1; stdout = failure.stdout?.toString() ?? ''; stderr = failure.stderr?.toString() ?? ''; error = failure.message; }
  rmSync(work, { recursive: true, force: true });
  return {
    id: testCase.id, source: testCase.source, marker: testCase.marker, language: testCase.language, image: testCase.image,
    command: testCase.command.join(' '), source_sha256: sha256(source), extracted_code_sha256: sha256(code),
    expected_stdout: testCase.expected, stdout, stderr, exit_code: exitCode, error,
    status: exitCode === 0 && stdout === testCase.expected ? 'PASS' : 'FAIL',
  };
});

const report = {
  scope: 'Five P1 core or standard-library pages selected outside the earlier named validation pages. Each program is extracted unchanged from its Markdown body by its p1-runtime-case marker.',
  execution: 'Docker containers run without network, with a read-only root filesystem, dropped capabilities, and bounded PID, memory, and tmpfs resources.',
  not_verified: ['Next.js rendering, routing, or build', 'TanStack Query cache integration', 'React Native device/UI/accessibility behavior', 'Compose or Android runtime', 'SwiftUI or iOS runtime'],
  passed: results.filter((result) => result.status === 'PASS').length,
  total: results.length,
  results,
};

writeFileSync(join(reportDirectory, 'p1-runtime-evidence.json'), JSON.stringify(report, null, 2) + '\n');
const rows = results.map((result) => `| \`${result.id}\` | \`${result.source}\` | \`${result.image}\` | ${result.status} |`).join('\n');
writeFileSync(join(reportDirectory, 'p1-runtime-evidence.md'), `# P1 runtime evidence\n\nEvery program below was extracted unchanged from its source Markdown body and executed in a network-disabled container.\n\n| Case | Source | Runtime | Status |\n|---|---|---|---|\n${rows}\n\n## Reproduce\n\n\`node shared-resources/tools/document-quality/verify-p1-runtime-evidence.mjs\`\n\n## Boundary\n\nThis evidence covers only the listed portable language or standard-library contracts. It does not claim framework, browser, device, Android, iOS, or SwiftUI validation.\n`);
if (report.passed !== report.total) process.exitCode = 1;
console.log(`P1 runtime evidence: ${report.passed}/${report.total} passed`);
