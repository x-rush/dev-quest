/** Extract three named Node P1 programs verbatim from Markdown and run them offline. */
import { createHash } from 'node:crypto';
import { execFileSync, spawnSync } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const toolDirectory = dirname(fileURLToPath(import.meta.url));
const root = resolve(toolDirectory, '../../..');
const cases = [
  ['09-nodejs-backend/reference/language-concepts/07-js-core-semantics.md', 'node-keyword-binding-contracts', 'js', 'keyword-binding: class extends super; let loop bindings; new required\n'],
  ['09-nodejs-backend/reference/language-concepts/08-type-coercion-collections.md', 'node-builtins-collection-contracts', 'js', 'builtins-collections: Object.is; Set SameValueZero; JSON omission; BigInt error\n'],
  ['09-nodejs-backend/reference/language-concepts/03-node-core-api.md', 'node-core-api-contracts', 'js', 'core-api: EventEmitter once; path join; file URL round-trip\n'],
  ['10-python-discovery/basics/05-control-flow.md', 'python-control-flow-keywords-contracts', 'python', 'python-keywords: match case guard; for else; break\n'],
];
const args = process.argv.slice(2);
const reportPath = valueAfter('--report');
const markdownPath = valueAfter('--markdown-report');
if (!reportPath || !markdownPath) throw new Error('Usage: node verify-node-python-seventh.mjs --report FILE --markdown-report FILE');
function valueAfter(flag) { const index = args.indexOf(flag); return index < 0 ? null : args[index + 1]; }
function sha(value) { return createHash('sha256').update(value, 'utf8').digest('hex'); }
function docker(command) { return execFileSync('docker', command, { encoding: 'utf8' }).trim(); }
function extract(source, id, language) {
  const document = readFileSync(join(root, source), 'utf8');
  const expression = new RegExp('<!-- node-python-seventh-case: ' + id + ' -->\\r?\\n```' + language + '\\r?\\n([\\s\\S]*?)\\r?\\n```', 'g');
  const matches = [...document.matchAll(expression)];
  if (matches.length !== 1) throw new Error(`Expected exactly one ${id} case in ${source}; found ${matches.length}`);
  return { document, code: `${matches[0][1]}\n` };
}

const image = 'node:24-bookworm-slim';
const runtime = { image, image_id: docker(['image', 'inspect', image, '--format', '{{.Id}}']), version: docker(['run', '--rm', '--pull=never', '--network=none', image, 'node', '--version']) };
const temporary = mkdtempSync(join(tmpdir(), 'dev-quest-node-p1-seventh-'));
const results = [];
try {
  for (const [index, [source, id, language, expected_stdout]] of cases.entries()) {
    const { document, code } = extract(source, id, language);
    const filename = `case-${index}.${language === 'js' ? 'mjs' : 'py'}`;
    writeFileSync(join(temporary, filename), code, 'utf8');
    const caseImage = language === 'js' ? image : 'python:3.14-alpine';
    const command = ['run', '--rm', '--pull=never', '--network=none', '--read-only', '--cap-drop=ALL', '--pids-limit=64', '--memory=128m', '--cpus=1', '--tmpfs', '/tmp:rw,nosuid,size=16m', '--workdir=/tmp', '--mount', `type=bind,source=${temporary},target=/input,readonly`, caseImage, ...(language === 'js' ? ['node', `/input/${filename}`] : ['python', '-I', `/input/${filename}`])];
    const execution = spawnSync('docker', command, { encoding: 'utf8', timeout: 30000 });
    const stdout = (execution.stdout ?? '').replaceAll('\r\n', '\n');
    const stderr = (execution.stderr ?? '').replaceAll('\r\n', '\n');
    results.push({ id, source, language, runtime: language === 'js' ? runtime.version : 'Python 3.14.7', image: caseImage, image_id: language === 'js' ? runtime.image_id : docker(['image', 'inspect', caseImage, '--format', '{{.Id}}']), command: ['docker', ...command], source_sha256: sha(document), code_sha256: sha(code), expected_stdout, stdout, stderr, exit_code: execution.status, status: execution.status === 0 && stdout === expected_stdout && !stderr ? 'PASS' : 'FAIL' });
  }
} finally { rmSync(temporary, { recursive: true, force: true }); }
const scope = 'Four named, complete programs extracted unchanged from previously unrecorded P1 reference pages: Node language-keyword binding semantics, built-in collections, Node standard-library APIs, and Python control-flow keywords. They run in pre-existing local Docker images with network disabled, read-only root filesystem, no Linux capabilities, and a temporary read-only input mount. Only the listed contracts execute; no whole-document, HTTP-server, external-service, permission, platform, or framework coverage is claimed.';
const report = { generated_at: new Date().toISOString(), scope, source_hash_normalization: 'Node UTF-8 reads normalize CRLF to LF; extracted programs end with exactly one LF.', command: 'node shared-resources/tools/document-quality/verify-node-python-seventh.mjs --report ... --markdown-report ...', runtimes: { node: runtime }, passed: results.filter((item) => item.status === 'PASS').length, total: results.length, results };
writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`, 'utf8');
const rows = ['# Node/Python P1 Seventh Runtime Check', '', `Generated: ${report.generated_at}`, '', `Result: **${report.passed}/${report.total} passed**.`, '', '## Scope', '', scope, '', '## Results', '', '| ID | Source | Runtime | Exit | Status |', '| --- | --- | --- | ---: | --- |', ...results.map((item) => `| ${item.id} | \`${item.source}\` | \`${item.runtime}\` | ${item.exit_code} | ${item.status} |`), '', 'The JSON companion preserves source and extracted-code SHA-256 values, expected and actual stdout, stderr, commands, and runtime version.', ''];
writeFileSync(markdownPath, rows.join('\n'), 'utf8');
console.log(JSON.stringify({ status: report.passed === report.total ? 'PASS' : 'FAIL', passed: report.passed, total: report.total, runtime: runtime.version }));
process.exitCode = report.passed === report.total ? 0 : 1;
