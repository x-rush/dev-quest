#!/usr/bin/env node
/*
 * Extract four complete fenced programs from their teaching pages unchanged and
 * run them in the repository's already-present language images.  This is a
 * deliberately narrow evidence producer: it never claims coverage for other
 * fences, framework behaviour, I/O, network, or a project's own toolchain.
 */
import { execFileSync } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = fileURLToPath(new URL('.', import.meta.url));
const root = resolve(here, '../../..');
const reports = join(here, 'reports');
const cases = [
  {
    id: 'go-map-semantics', file: '01-go-backend/reference/language-concepts/11-map-semantics.md', lang: 'go',
    needle: 'package main\n\nimport (\n\t"fmt"', out: 'main.go', image: 'golang:1.27',
    env: ['GOCACHE=/output/go-build'],
    command: ['sh', '-c', 'go build -o /output/main /work/main.go && /output/main'], expect: ['no rust', 'alice 25', 'bob 28', 'carol 30', '1'],
  },
  {
    id: 'php-datetime-immutable', file: '07-php-mastery/reference/language-concepts/10-datetime.md', lang: 'php',
    needle: "$start = new DateTime('2026-09-11 09:00:00');", out: 'main.php', image: 'php:8.5-cli',
    command: ['php', '/work/main.php'], expect: ['09:00 ~ 10:00'],
  },
  {
    id: 'java-regex', file: '08-java-revisited/reference/library-guides/08-java-util-regex.md', lang: 'java',
    needle: 'public class RegexDemo', out: 'RegexDemo.java', image: 'eclipse-temurin:21-jdk',
    command: ['sh', '-c', 'javac -d /tmp/classes /work/RegexDemo.java && java -cp /tmp/classes RegexDemo'], expect: ['0', '2', '2', '$$b'],
  },
  {
    id: 'python-asyncio', file: '10-python-discovery/basics/07-advanced-features.md', lang: 'python',
    needle: 'import asyncio\n\nasync def fetch', out: 'main.py', image: 'python:3.14-alpine',
    command: ['python', '/work/main.py'], expect: ["['A 完成', 'B 完成', 'C 完成']"],
  },
];

function fencedBody(markdown, lang, needle) {
  const normalized = markdown.replaceAll('\r\n', '\n');
  const blocks = [...normalized.matchAll(new RegExp('```' + lang + '\\n([\\s\\S]*?)```', 'g'))].map((m) => m[1]);
  const body = blocks.find((block) => block.includes(needle));
  if (!body) throw new Error(`complete ${lang} fence containing ${needle} was not found`);
  return body;
}
function runCase(item) {
  const source = fencedBody(readFileSync(join(root, item.file), 'utf8'), item.lang, item.needle);
  const dir = mkdtempSync(join(tmpdir(), 'dev-quest-eleventh-'));
  const outputDir = mkdtempSync(join(tmpdir(), 'dev-quest-eleventh-output-'));
  try {
    writeFileSync(join(dir, item.out), source, 'utf8');
    const envArgs = (item.env ?? []).flatMap((entry) => ['-e', entry]);
    const args = ['run', '--rm', '--network', 'none', '--read-only', '--cap-drop', 'ALL', '--pids-limit', '64', '--memory', '256m', '--cpus', '1', '--tmpfs', '/tmp:rw,nosuid,size=256m', ...envArgs, '-v', `${dir.replaceAll('\\', '/') }:/work:ro`, '-v', `${outputDir.replaceAll('\\', '/')}:/output`, item.image, ...item.command];
    const output = execFileSync('docker', args, { encoding: 'utf8', timeout: 30000, stdio: ['ignore', 'pipe', 'pipe'] });
    const missing = item.expect.filter((text) => !output.includes(text));
    return { id: item.id, file: item.file, language: item.lang, status: missing.length ? 'FAIL' : 'PASS', command: `docker ${args.join(' ')}`, expected_output_fragments: item.expect, output, missing_output_fragments: missing };
  } catch (error) {
    return { id: item.id, file: item.file, language: item.lang, status: 'FAIL', command: item.command.join(' '), expected_output_fragments: item.expect, output: `${error.stdout ?? ''}${error.stderr ?? ''}`, error: error.message };
  } finally { rmSync(dir, { recursive: true, force: true }); rmSync(outputDir, { recursive: true, force: true }); }
}
const results = cases.map(runCase);
const report = {
  scope: 'Four named complete fenced programs extracted unchanged from current P1 core/standard-library pages: Go map semantics, PHP DateTimeImmutable, Java java.util.regex, and Python asyncio.',
  execution: 'Existing local Docker images; network disabled, read-only root filesystem, capabilities dropped, bounded CPU/memory/processes, a read-only extracted source mount, and disposable writable output/tmp mounts only for compiler/runtime artifacts.',
  not_verified: ['Other fences or prose in these pages', 'Go map concurrent-access/race behaviour', 'PHP timezone/database/framework integration', 'Java regex performance or project-specific JDK behaviour', 'Python external I/O, type checking, or framework integration'],
  passed: results.filter((result) => result.status === 'PASS').length, total: results.length, results,
};
writeFileSync(join(reports, 'go-php-java-python-eleventh-runtime.json'), JSON.stringify(report, null, 2) + '\n');
const lines = ['# Go、PHP、Java、Python P1 限定运行验证（第十一轮）', '', `范围：${report.scope}`, '', `执行约束：${report.execution}`, '', `结果：${report.passed}/${report.total} 通过。`, '', '| 案例 | 原文位置 | 结果 | 可观察输出 |', '|---|---|---|---|', ...results.map((r) => `| ${r.id} | \`${r.file}\` | ${r.status} | ${r.expected_output_fragments.map((x) => `\`${x}\``).join('、')} |`), '', '## 未覆盖边界', '', ...report.not_verified.map((item) => `- ${item}`), ''];
writeFileSync(join(reports, 'go-php-java-python-eleventh-runtime.md'), lines.join('\n'));
if (report.passed !== report.total) process.exitCode = 1;
