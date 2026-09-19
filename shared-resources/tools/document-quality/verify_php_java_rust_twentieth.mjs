#!/usr/bin/env node
/** Extract three named Markdown programs unchanged and run them in resource-bounded Docker containers. */
import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, "..", "..", "..");
const reportDir = join(here, "reports");
const cases = [
  { id: "php-magic-isset-get", language: "php", document: "07-php-mastery/reference/language-concepts/17-magic-methods.md", image: "php:8.5-cli-alpine", expected: "present\nempty\npresent\nempty\n", command: ["php", "/tmp/main.php"] },
  { id: "java-annotation-inherited-runtime", language: "java", document: "08-java-revisited/reference/language-concepts/09-annotations.md", image: "eclipse-temurin:21-jdk-noble", expected: "base\ntrue\n", command: ["sh", "-c", "javac --release 21 -encoding UTF-8 -d /tmp /tmp/Main.java && java -cp /tmp Main"] },
  { id: "rust-unsafe-split-at-mut", language: "rust", document: "11-rust-cross-platform/reference/language-concepts/06-unsafe.md", image: "rust:1-slim-bookworm", expected: "[10, 2, 3, 40]\n", command: ["sh", "-c", "rustc --edition 2024 /tmp/main.rs -o /tmp/main && /tmp/main"] },
];

function sourceFor(item) {
  const raw = readFileSync(join(root, item.document));
  const text = raw.toString("utf8").replace(/\r\n/g, "\n");
  const marker = `<!-- terra-twentieth-case: ${item.id} -->`;
  const start = text.indexOf(marker);
  if (start < 0) throw new Error(`${item.document}: missing ${marker}`);
  if (text.indexOf(marker, start + marker.length) >= 0) throw new Error(`${item.document}: marker is not unique`);
  const fenceStart = text.indexOf(`\`\`\`${item.language}\n`, start);
  const fenceEnd = text.indexOf("\n```", fenceStart + item.language.length + 5);
  if (fenceStart < 0 || fenceEnd < 0) throw new Error(`${item.document}: named complete ${item.language} fence missing`);
  return { raw, code: `${text.slice(fenceStart + item.language.length + 4, fenceEnd)}\n` };
}

function run(item, code) {
  const filename = item.language === "java" ? "Main.java" : item.language === "rust" ? "main.rs" : "main.php";
  const prelude = `cat > /tmp/${filename} && exec \"$@\"`;
  const args = ["run", "--rm", "-i", "--pull=never", "--network=none", "--read-only", "--cap-drop=ALL", "--security-opt=no-new-privileges", "--pids-limit=64", "--memory=512m", "--cpus=1", "--tmpfs", "/tmp:rw,exec,nosuid,nodev,size=64m", item.image, "sh", "-c", prelude, "document-program", ...item.command];
  const child = spawnSync("docker", args, { cwd: root, input: code, encoding: "utf8", timeout: 90000 });
  if (child.error) throw child.error;
  return { command: ["docker", ...args], exit_code: child.status, stdout: child.stdout, stderr: child.stderr };
}

const docker = spawnSync("docker", ["--version"], { cwd: root, encoding: "utf8", timeout: 10000 });
if (docker.error || docker.status !== 0) throw docker.error ?? new Error(docker.stderr || "Docker unavailable");
const results = cases.map((item) => {
  const { raw, code } = sourceFor(item);
  const execution = run(item, code);
  return { ...item, document_sha256: createHash("sha256").update(raw).digest("hex"), code_sha256: createHash("sha256").update(code).digest("hex"), extraction: "unique named Markdown fence extracted without code edits after CRLF-to-LF normalization", execution, status: execution.exit_code === 0 && execution.stdout === item.expected && execution.stderr === "" ? "PASS" : "FAIL" };
});
const report = { schema_version: 1, generated_at: new Date().toISOString(), purpose: "Twentieth-round runtime evidence for three named P1 PHP, Java, and Rust core or standard-library body programs.", isolation: "No network, read-only container root, dropped capabilities, no-new-privileges, bounded CPU/memory/PIDs, and tmpfs-only writable workspace. Images must already be present because --pull=never is used.", scope: "Only the three unique named complete fences are executed. Other prose/fences, framework integration, browser or Web-SAPI behavior, performance, Miri/sanitizers, and full projects remain outside this evidence.", docker: { exit_code: docker.status, stdout: docker.stdout, stderr: docker.stderr }, results, summary: { passed: results.filter((r) => r.status === "PASS").length, total: results.length } };
mkdirSync(reportDir, { recursive: true });
writeFileSync(join(reportDir, "php-java-rust-twentieth-runtime.json"), `${JSON.stringify(report, null, 2)}\n`);
const rows = results.map((r) => `| \`${r.id}\` | \`${r.document}\` | \`${r.image}\` | ${r.status} |`);
writeFileSync(join(reportDir, "php-java-rust-twentieth-runtime.md"), ["# PHP / Java / Rust 第二十轮正文提取运行验证", "", report.purpose, "", "| 具名程序 | 来源 | 隔离工具链 | 结果 |", "| --- | --- | --- | --- |", ...rows, "", "验证器只原样提取表中唯一具名完整围栏，并断言精确 stdout、空 stderr 和零退出码。JSON 记录文档与提取程序 SHA-256、完整 Docker 命令、退出码及输出。隔离限制和未覆盖范围见 JSON 的 `isolation` 与 `scope`。", ""].join("\n"));
console.log(`${report.summary.passed === report.summary.total ? "PASS" : "FAIL"}: ${report.summary.passed}/${report.summary.total} named body programs`);
process.exitCode = report.summary.passed === report.summary.total ? 0 : 1;
