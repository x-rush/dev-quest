/**
 * Extract three named teaching examples from Markdown and verify their limited contracts.
 * A passing run covers only these code blocks, never their complete documents or modules.
 */
import crypto from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const toolDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(toolDir, '../../../..');
const curriculumRoot = path.join(repoRoot, 'dev-quest');
const reportDir = path.join(toolDir, 'reports');
const tick = String.fromCharCode(96);
const cases = [
  ['next-typescript-boundary', '02-nextjs-frontend/basics/03-typescript-integration.md', 'ts', 'node'],
  ['node-esm-binding', '09-nodejs-backend/basics/03-modules-esm.md', 'js', 'node'],
  ['python-bindings-formatting', '10-python-discovery/basics/03-variables-types.md', 'python', 'python'],
];

const sha256 = (value) => crypto.createHash('sha256').update(value).digest('hex');
const normalizedText = (source) => fs.readFileSync(source, 'utf8').replaceAll('\r\n', '\n');

function extract(source, id, language) {
  const text = normalizedText(source);
  const start = `${tick}${tick}${tick}${language} verify:${id}\n`;
  const codeStart = text.indexOf(start);
  if (codeStart < 0) throw new Error(`Missing named Markdown block: ${source} ${id}`);
  if (text.indexOf(start, codeStart + start.length) >= 0) throw new Error(`Named Markdown block is not unique: ${source} ${id}`);
  const end = text.indexOf(`\n${tick}${tick}${tick}`, codeStart + start.length);
  if (end < 0) throw new Error(`Unclosed named Markdown block: ${source} ${id}`);
  return { text, code: `${text.slice(codeStart + start.length, end)}\n`, line: text.slice(0, codeStart + start.length).split('\n').length };
}

function invoke(command, args) {
  try {
    const stdout = execFileSync(command, args, { cwd: repoRoot, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] });
    return { command: [command, ...args], exit_code: 0, stdout, stderr: '', status: 'PASS' };
  } catch (error) {
    return {
      command: [command, ...args],
      exit_code: error.status ?? 1,
      stdout: error.stdout?.toString() ?? '',
      stderr: error.stderr?.toString() ?? error.message,
      status: 'FAIL',
    };
  }
}

const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'dq-next-node-python-'));
let results;
try {
  results = cases.map(([id, relative, language, runtime]) => {
    const source = path.join(curriculumRoot, relative);
    const extracted = extract(source, id, language);
    const extension = { ts: '.ts', js: '.mjs', python: '.py' }[language];
    const fileName = `${id}${extension}`;
    fs.writeFileSync(path.join(temp, fileName), extracted.code, 'utf8');
    const image = runtime === 'python' ? 'python:3.14-alpine' : 'node:24-bookworm-slim';
    const command = runtime === 'python'
      ? ['run', '--rm', '--network', 'none', '--read-only', '-v', `${temp}:/input:ro`, image, 'python', '-I', `/input/${fileName}`]
      : ['run', '--rm', '--network', 'none', '--read-only', '-v', `${temp}:/input:ro`, image, 'node', '--experimental-strip-types', `/input/${fileName}`];
    return {
      id,
      source: `dev-quest/${relative}`,
      source_sha256: sha256(extracted.text),
      line: extracted.line,
      code_sha256: sha256(extracted.code),
      extracted_directly_from_markdown: true,
      environment: image,
      ...invoke('docker', command),
      scope: 'Only this named, complete code block; no whole-document, framework, network, or application coverage.',
    };
  });
} finally {
  fs.rmSync(temp, { recursive: true, force: true });
}

const report = {
  generated_at: new Date().toISOString(),
  purpose: 'Limited direct-body extraction verification for three P1 basics documents.',
  passed: results.filter((result) => result.status === 'PASS').length,
  total: results.length,
  results,
};
fs.mkdirSync(reportDir, { recursive: true });
fs.writeFileSync(path.join(reportDir, 'next-node-python-basics-results.json'), `${JSON.stringify(report, null, 2)}\n`, 'utf8');
const rows = results.map((result) => `| \`${result.source}\` | \`${result.id}\` | ${result.line} | ${result.status} |`);
const markdown = [
  '# Next、Node 与 Python P1 基础页限定验证',
  '',
  '该报告只覆盖以下从 Markdown 正文直接提取的具名程序，不代表整篇页面、Next.js 应用、网络或第三方依赖已经验证。',
  '',
  '| 页面 | 程序 | 行 | 结果 |',
  '| --- | --- | ---: | --- |',
  ...rows,
  '',
  '执行方式：代码在禁网、只读文件系统的 Docker 容器中执行。Next/TypeScript 示例使用 Node 24 的 TypeScript 类型擦除执行；它验证该示例可执行，不替代完整 `tsc` 项目检查。完整命令、哈希和标准输出见同目录 JSON 报告。',
  '',
].join('\n');
fs.writeFileSync(path.join(reportDir, 'next-node-python-basics-report.md'), markdown, 'utf8');
console.log(`${report.passed}/${report.total} passed; wrote reports/next-node-python-basics-{results.json,report.md}`);
process.exitCode = report.passed === report.total ? 0 : 1;
