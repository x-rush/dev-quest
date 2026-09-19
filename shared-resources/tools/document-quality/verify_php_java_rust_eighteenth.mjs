#!/usr/bin/env node
/** Extract three named complete Markdown programs unchanged and run them in isolated Docker containers. */
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, "..", "..", "..");
const reports = join(here, "reports");
const cases = [
  ["php-session-write-close", "PHP", "07-php-mastery/reference/library-guides/06-http-session-cookie.md", "php", "main.php", "php:8.5-cli-alpine", ["sh", "-c", "cat > /tmp/main.php && php /tmp/main.php"], "closed\nstored\n"],
  ["java-jpms-module-map", "Java", "08-java-revisited/reference/library-guides/09-jdk-package-map.md", "java", "Main.java", "eclipse-temurin:21-jdk-noble", ["sh", "-c", "cat > /tmp/Main.java && javac --release 21 -encoding UTF-8 -d /tmp /tmp/Main.java && java -cp /tmp Main"], "java.lang.String=java.base\njava.util.logging.Logger=java.logging\njava.sql.Connection=java.sql\njavax.annotation.processing.Processor=java.compiler\n"],
  ["rust-arc-weak-lifecycle", "Rust", "11-rust-cross-platform/reference/language-concepts/07-smart-pointers.md", "rust", "main.rs", "rust:1-slim-bookworm", ["sh", "-c", "cat > /tmp/main.rs && rustc --edition 2024 /tmp/main.rs -o /tmp/main && /tmp/main"], "strong=2\nvalue=shared\ngone=true\n"],
];

function invoke(command, input) {
  const run = spawnSync(command[0], command.slice(1), { cwd: root, input, encoding: "utf8", timeout: 90000 });
  if (run.error) throw run.error;
  return { command, exit_code: run.status, stdout: run.stdout, stderr: run.stderr };
}
function extract(document, id, language) {
  const source = readFileSync(join(root, document), "utf8").replace(/\r\n/g, "\n");
  const re = new RegExp(`<!--\\s*terra-eighteenth-case:\\s*${id}\\s*-->\\s*\\x60\\x60\\x60${language}\\s*\\n(.*?)\\n\\x60\\x60\\x60`, "gs");
  const found = [...source.matchAll(re)];
  if (found.length !== 1) throw new Error(`${document}: expected exactly one named ${id} fence; got ${found.length}`);
  return `${found[0][1]}\n`;
}
function main() {
  if (!existsSync(process.env.ComSpec ?? "cmd.exe")) { /* Docker lookup below yields the useful platform error. */ }
  const report = { schema_version: 1, generated_at: new Date().toISOString(),
    scope: "Three named, complete PHP/Java/Rust P1 core or standard-library Markdown programs are extracted unchanged and run with exact stdout assertions.",
    method: "Each program is extracted unchanged from its unique named fence and passed on stdin to an already-present Docker image, where it is written only to isolated tmpfs. Containers have no network, read-only roots, no Linux capabilities, and bounded CPU, memory, process, and tmpfs resources.",
    not_verified: ["other prose or fences in the three documents", "HTTP browser and Web-SAPI behavior", "named-module requires configuration", "thread scheduling, performance, and platform-specific behavior"],
    docker: invoke(["docker", "--version"]), cases: [] };
  for (const [id, language, document, fence, filename, image, command, expected] of cases) {
    const code = extract(document, id, fence);
    const run = invoke(["docker", "run", "--rm", "-i", "--pull=never", "--network=none", "--read-only", "--cap-drop=ALL", "--pids-limit=64", "--memory=512m", "--cpus=1", "--tmpfs", "/tmp:rw,exec,nosuid,size=64m", image, ...command], code);
    const status = run.exit_code === 0 && run.stdout === expected && run.stderr === "" ? "PASS" : "FAIL";
    report.cases.push({ id, language, source: document, filename, image, document_sha256: createHash("sha256").update(readFileSync(join(root, document))).digest("hex"), code_sha256: createHash("sha256").update(code).digest("hex"), expected_stdout: expected, execution: run, status });
  }
  report.passed = report.cases.filter((item) => item.status === "PASS").length; report.total = report.cases.length;
  mkdirSync(reports, { recursive: true });
  writeFileSync(join(reports, "php-java-rust-eighteenth-runtime.json"), `${JSON.stringify(report, null, 2)}\n`);
  const rows = report.cases.map((item) => `| \`${item.id}\` | \`${item.source}\` | \`${item.image}\` | ${item.status} |`);
  writeFileSync(join(reports, "php-java-rust-eighteenth-runtime.md"), ["# PHP / Java / Rust 第十八轮正文提取运行验证", "", report.scope, "", "| Case | Source | Runtime | Result |", "| --- | --- | --- | --- |", ...rows, "", "## 边界", "", "只验证表中唯一具名围栏的原样提取、隔离执行和精确输出。PHP 覆盖隔离文件会话的写入和关闭，不覆盖 HTTP 或浏览器；Java 覆盖类到 JPMS 模块的反查，不覆盖命名模块构建；Rust 覆盖 Arc/Weak 生命周期，不覆盖线程调度或性能。JSON 报告保留来源和程序 SHA-256、完整容器命令、退出码及 stdout/stderr。", ""].join("\n"));
  console.log(`${report.passed === report.total ? "PASS" : "FAIL"}: ${report.passed}/${report.total} named body programs`);
  return report.passed === report.total ? 0 : 1;
}
process.exitCode = main();
