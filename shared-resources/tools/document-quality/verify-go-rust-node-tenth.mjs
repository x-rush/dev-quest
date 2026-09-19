/** Run three named P1 body programs extracted unchanged from Markdown. */
import { createHash } from 'node:crypto';
import { execFileSync, spawnSync } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const directory = dirname(fileURLToPath(import.meta.url));
const root = resolve(directory, '../../..');
const reports = join(directory, 'reports');
const go = resolve(root, '../verification-lab/go-toolchain/go/bin/go.exe');
const cases = [
  ['go-nil-semantics', '01-go-backend/reference/language-concepts/15-nil-semantics.md', 'go', '0 0\n[1]\n0\n0\ntrue\ntrue\ntrue\n'],
  ['rust-ownership-move-clone-copy', '11-rust-cross-platform/basics/02-ownership-borrowing.md', 'rust', '所有权\nn1 = 42, n2 = 42\ns2 = 所有权, s3 = 所有权\n'],
  ['node-crypto-aes-gcm-round-trip', '09-nodejs-backend/reference/library-guides/03-crypto.md', 'ts', '秘密消息\n'],
];
function sha(value) { return createHash('sha256').update(value).digest('hex'); }
function run(command) { const value = spawnSync(command[0], command.slice(1), { encoding: 'utf8', timeout: 30000 }); return { exit_code: value.status, stdout: (value.stdout ?? '').replaceAll('\r\n', '\n'), stderr: (value.stderr ?? '').replaceAll('\r\n', '\n') }; }
function version(command) { const value = run(command); if (value.exit_code !== 0) throw new Error(value.stderr); return value.stdout.trim(); }
function extract(relative, id, language) {
  const source = readFileSync(join(root, relative), 'utf8').replaceAll('\r\n', '\n');
  const marker = `<!-- go-rust-node-tenth-case: ${id} -->\n\`\`\`${language}\n`;
  if (source.split(marker).length !== 2) throw new Error(`expected exactly one ${id} marker`);
  return { source, code: `${source.split(marker)[1].split('\n```')[0]}\n` };
}
const runtimes = { go: version([go, 'version']), rust: version(['docker', 'run', '--rm', '--pull=never', 'rust:1-slim-bookworm', 'rustc', '--version']), node: version(['docker', 'run', '--rm', '--pull=never', 'node:24-bookworm-slim', 'node', '--version']) };
const work = mkdtempSync(join(tmpdir(), 'go-rust-node-tenth-'));
const results = [];
try {
  for (const [id, source, language, expected_stdout] of cases) {
    const extracted = extract(source, id, language);
    const extension = language === 'go' ? 'go' : language === 'rust' ? 'rs' : 'ts';
    const file = join(work, `${id}.${extension}`); writeFileSync(file, extracted.code, 'utf8');
    const command = language === 'go' ? [go, 'run', file] : language === 'rust'
      ? ['docker', 'run', '--rm', '--pull=never', '--network=none', '--read-only', '--cap-drop=ALL', '--pids-limit=64', '--memory=128m', '--cpus=1', '--tmpfs', '/work:rw,exec,nosuid,size=16m', '--mount', `type=bind,source=${work},target=/input,readonly`, '--workdir=/work', 'rust:1-slim-bookworm', 'sh', '-c', `rustc --edition=2024 /input/${id}.rs -o /work/program && /work/program`]
      : ['docker', 'run', '--rm', '--pull=never', '--network=none', '--read-only', '--cap-drop=ALL', '--pids-limit=64', '--memory=128m', '--cpus=1', '--tmpfs', '/tmp:rw,nosuid,size=16m', '--mount', `type=bind,source=${work},target=/input,readonly`, '--workdir=/tmp', 'node:24-bookworm-slim', 'node', '--experimental-strip-types', `/input/${id}.ts`];
    const outcome = run(command);
    results.push({ id, source, language, source_sha256: sha(extracted.source), extracted_code_sha256: sha(extracted.code), command, expected_stdout, ...outcome, status: outcome.exit_code === 0 && outcome.stdout === expected_stdout && !outcome.stderr ? 'PASS' : 'FAIL' });
  }
} finally { rmSync(work, { recursive: true, force: true }); }
const passed = results.filter((item) => item.status === 'PASS').length;
const scope = 'Three named, complete fenced programs extracted unchanged from currently not_verified P1 Go, Rust, and Node.js pages. Go runs with the repository toolchain; Rust and Node run in existing local Docker images with network disabled, read-only roots, dropped capabilities, bounded CPU/memory/processes, and a read-only input mount. This does not verify other snippets, prose, network, filesystem, platform, framework, or production-security behavior.';
const report = { schema_version: 1, generated_at: new Date().toISOString(), scope, runtimes, passed, total: results.length, results };
writeFileSync(join(reports, 'go-rust-node-tenth-runtime.json'), `${JSON.stringify(report, null, 2)}\n`);
const rows = ['# Go、Rust、Node.js P1 正文限定运行验证', '', `结果：**${passed}/${results.length} passed**。`, '', '## 范围', '', scope, '', '## 结果', '', '| ID | 页面 | 运行时 | 退出码 | 状态 |', '| --- | --- | --- | ---: | --- |', ...results.map((item) => `| \`${item.id}\` | \`${item.source}\` | \`${runtimes[item.language === 'ts' ? 'node' : item.language]}\` | ${item.exit_code} | ${item.status} |`), '', 'JSON 报告保留完整命令、源码与提取程序的 SHA-256、期望/实际 stdout、stderr 及工具链版本。`PASS` 只表示该表列出的正文完整程序通过。', ''];
writeFileSync(join(reports, 'go-rust-node-tenth-runtime.md'), rows.join('\n'));
console.log(JSON.stringify({ status: passed === results.length ? 'PASS' : 'FAIL', passed, total: results.length, runtimes }));
process.exitCode = passed === results.length ? 0 : 1;
