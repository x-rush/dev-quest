/** Extract and execute three named Go, PHP, and Java P1 Markdown programs. */
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDirectory = fileURLToPath(new URL('.', import.meta.url));
const root = resolve(scriptDirectory, '../../..');
const reports = join(scriptDirectory, 'reports');
const cases = [
  ['go', '01-go-backend/reference/language-concepts/10-slice-semantics.md', 'golang:1.27', 'main.go'],
  ['php', '07-php-mastery/reference/language-concepts/13-weak-comparison.md', 'php:8.5-cli', 'main.php'],
  ['java', '08-java-revisited/reference/language-concepts/07-string-immutability-pool.md', 'eclipse-temurin:21-jdk', 'Main.java'],
];
const fence = /<!-- ninth-reference-case: (\{.*?\}) -->\s*```(go|php|java)\s*\n(.*?)\n```/gs;
const scope = 'Three named P1 core/standard-library Markdown programs (one each for Go, PHP, and Java) extracted unchanged from pages that had no runtime-evidence marker. Portable language/library behavior only.';
const boundary = 'Docker network disabled; read-only root filesystem and source mount; only /tmp is writable. This does not validate whole documents, frameworks, servers, databases, browsers, devices, or platform integrations.';

function execute(command) {
  try {
    return { command, exit_code: 0, stdout: execFileSync(command[0], command.slice(1), { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] }), stderr: '' };
  } catch (error) {
    return { command, exit_code: error.status ?? 1, stdout: error.stdout?.toString() ?? '', stderr: error.stderr?.toString() ?? error.message };
  }
}

const temporary = mkdtempSync(join(tmpdir(), 'dq-go-php-java-ninth-'));
const results = [];
try {
  for (const [language, relative, image, filename] of cases) {
    const body = readFileSync(join(root, relative), 'utf8');
    if (body.includes('runtime-evidence')) throw new Error(`selected page already has runtime evidence: ${relative}`);
    const matches = [...body.matchAll(fence)];
    if (matches.length !== 1) throw new Error(`expected exactly one ninth fence in ${relative}, found ${matches.length}`);
    const [, encoded, fencedLanguage, code] = matches[0];
    if (language !== fencedLanguage) throw new Error(`language mismatch in ${relative}`);
    const metadata = JSON.parse(encoded);
    const source = `${code}\n`;
    const work = join(temporary, metadata.id);
    mkdirSync(work);
    writeFileSync(join(work, filename), source, 'utf8');
    const docker = ['docker', 'run', '--rm', '--network', 'none', '--read-only', '--tmpfs', '/tmp:exec', '-v', `${work}:/work:ro`, '-w', '/work', image];
    const command = language === 'go'
      ? [...docker, 'sh', '-c', 'GOCACHE=/tmp/go-cache go run main.go']
      : language === 'php'
        ? [...docker, 'php', 'main.php']
        : [...docker, 'sh', '-c', 'javac --release 21 -d /tmp/classes Main.java && java -cp /tmp/classes Main'];
    const execution = execute(command);
    results.push({ id: metadata.id, document: relative, language, image, source_sha256: createHash('sha256').update(source).digest('hex'), expected_stdout: metadata.stdout, actual_stdout: execution.stdout, execution, passed: execution.exit_code === 0 && execution.stdout === metadata.stdout });
  }
} finally {
  rmSync(temporary, { recursive: true, force: true });
}
const report = { schema_version: 1, generated_at: new Date().toISOString(), scope, execution_boundary: boundary, results, passed: results.every((row) => row.passed) };
writeFileSync(join(reports, 'go-php-java-ninth-runtime.json'), `${JSON.stringify(report, null, 2)}\n`);
const rows = results.map((row) => `| \`${row.id}\` | \`${row.document}\` | \`${row.image}\` | ${row.passed ? 'PASS' : 'FAIL'} |`);
writeFileSync(join(reports, 'go-php-java-ninth-runtime.md'), `# Go / PHP / Java P1 第九轮正文提取验证\n\n${scope}\n\n| Case | Source | Runtime image | Result |\n| --- | --- | --- | --- |\n${rows.join('\n')}\n\n## 执行边界\n\n${boundary}\n\nJSON 限定报告保存源码 SHA-256、预期与实际标准输出、完整命令、标准错误、退出码和逐项断言。\n`);
console.log(`Go/PHP/Java ninth validation: ${results.filter((row) => row.passed).length}/${results.length} passed`);
process.exitCode = report.passed ? 0 : 1;
