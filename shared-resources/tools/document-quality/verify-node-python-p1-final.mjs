/** Extract four named programs unchanged from Markdown and execute their stated contracts. */
import { createHash } from 'node:crypto';
import { execFileSync, spawnSync } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const toolDirectory = dirname(fileURLToPath(import.meta.url));
const root = resolve(toolDirectory, '../../..');
const cases = [
  ['09-nodejs-backend/reference/language-concepts/01-js-modern-syntax.md', 'node-modern-syntax-contracts', 'js', [], 'modern-syntax: fallback=3/0/null; shared=node,js\n'],
  ['09-nodejs-backend/reference/language-concepts/09-globals-reference.md', 'node-globals-response-contracts', 'js', [], 'globals-response: clone reads twice; original body locks after read\n'],
  ['10-python-discovery/reference/language-concepts/01-python-keywords.md', 'python-keywords-control-flow', 'python', [], 'keywords-control-flow: first=3; missing=True\n'],
  ['10-python-discovery/reference/library-guides/04-os-sys.md', 'python-os-sys-environment-contracts', 'python', ['hello'], "os-sys-environment: argv=['hello']; cwd=True; executable=True\n"],
];
const images = { js: 'node:24-bookworm-slim', python: 'python:3.14-alpine' };
const arguments_ = process.argv.slice(2);
const reportPath = valueAfter('--report');
const markdownPath = valueAfter('--markdown-report');
if (!reportPath || !markdownPath) throw new Error('Usage: node verify-node-python-p1-final.mjs --report FILE --markdown-report FILE');

function valueAfter(flag) { const index = arguments_.indexOf(flag); return index < 0 ? null : arguments_[index + 1]; }
function sha(value) { return createHash('sha256').update(value, 'utf8').digest('hex'); }
function docker(command) { return execFileSync('docker', command, { encoding: 'utf8' }).trim(); }
function extract(source, id, language) {
  const document = readFileSync(join(root, source), 'utf8');
  const expression = new RegExp('<!-- node-python-p1-final-case: ' + id + ' -->\\r?\\n```' + language + '\\r?\\n([\\s\\S]*?)\\r?\\n```', 'g');
  const matches = [...document.matchAll(expression)];
  if (matches.length !== 1) throw new Error(`Expected one ${id} case in ${source}; found ${matches.length}`);
  return { document, code: `${matches[0][1]}\n` };
}

const runtimes = Object.fromEntries(Object.entries(images).map(([language, image]) => [language, {
  image,
  image_id: docker(['image', 'inspect', image, '--format', '{{.Id}}']),
  version: docker(['run', '--rm', '--pull=never', '--network=none', image, ...(language === 'js' ? ['node', '--version'] : ['python', '--version'])]),
}]));
const temporary = mkdtempSync(join(tmpdir(), 'dev-quest-p1-final-'));
const results = [];
try {
  for (const [index, [source, id, language, programArgs, expected_stdout]] of cases.entries()) {
    const { document, code } = extract(source, id, language);
    const filename = `case-${index}.${language === 'js' ? 'mjs' : 'py'}`;
    writeFileSync(join(temporary, filename), code, 'utf8');
    const runner = language === 'js' ? ['node', `/input/${filename}`, ...programArgs] : ['python', '-I', `/input/${filename}`, ...programArgs];
    const command = ['run', '--rm', '--pull=never', '--network=none', '--read-only', '--cap-drop=ALL', '--pids-limit=64', '--memory=128m', '--cpus=1', '--tmpfs', '/tmp:rw,nosuid,size=16m', '--workdir=/tmp', '--mount', `type=bind,source=${temporary},target=/input,readonly`, images[language], ...runner];
    const execution = spawnSync('docker', command, { encoding: 'utf8', timeout: 30000 });
    const stdout = (execution.stdout ?? '').replaceAll('\r\n', '\n');
    const stderr = (execution.stderr ?? '').replaceAll('\r\n', '\n');
    results.push({ id, source, language, runtime: runtimes[language].version, image: images[language], image_id: runtimes[language].image_id, command: ['docker', ...command], source_sha256: sha(document), code_sha256: sha(code), expected_stdout, stdout, stderr, exit_code: execution.status, status: execution.status === 0 && stdout === expected_stdout && !stderr ? 'PASS' : 'FAIL' });
  }
} finally { rmSync(temporary, { recursive: true, force: true }); }
const scope = 'Four named, complete programs extracted unchanged from two Node and two Python P1 reference documents not covered by the earlier core and follow-up checks. They run in pre-existing local Docker images with network disabled, a read-only root filesystem and a temporary input bind mount. Only the listed language and standard-library contracts execute; no whole-document, network, database, permission, platform, or framework coverage is claimed.';
const report = { generated_at: new Date().toISOString(), scope, source_hash_normalization: 'Node UTF-8 reads normalize CRLF to LF; extracted programs end with exactly one LF.', command: 'node shared-resources/tools/document-quality/verify-node-python-p1-final.mjs --report ... --markdown-report ...', runtimes, passed: results.filter((item) => item.status === 'PASS').length, total: results.length, results };
writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`, 'utf8');
const rows = ['# Node/Python P1 Final Runtime Check', '', `Generated: ${report.generated_at}`, '', `Result: **${report.passed}/${report.total} passed**.`, '', '## Scope', '', scope, '', '## Results', '', '| ID | Source | Runtime | Exit | Status |', '| --- | --- | ---: | ---: | --- |', ...results.map((item) => `| ${item.id} | \`${item.source}\` | \`${item.runtime}\` | ${item.exit_code} | ${item.status} |`), '', 'The JSON companion preserves source and extracted-code SHA-256 values, expected and actual stdout, stderr, commands, and runtime versions.', ''];
writeFileSync(markdownPath, rows.join('\n'), 'utf8');
console.log(JSON.stringify({ status: report.passed === report.total ? 'PASS' : 'FAIL', passed: report.passed, total: report.total, runtimes: Object.fromEntries(Object.entries(runtimes).map(([key, value]) => [key, value.version])) }));
process.exitCode = report.passed === report.total ? 0 : 1;
