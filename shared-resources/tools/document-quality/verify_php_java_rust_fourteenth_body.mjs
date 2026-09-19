#!/usr/bin/env node
/** Extract and run three named PHP/Java/Rust Markdown body programs unchanged. */
import { createHash } from "node:crypto";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, "..", "..", "..");
const reports = join(here, "reports");
const cases = [
  ["php", "07-php-mastery/reference/library-guides/05-file-stream-io.md", "php-file-stream-full-write-and-locked-update", "php:8.5-cli-alpine"],
  ["java", "08-java-revisited/reference/library-guides/07-java-text-and-time-format.md", "java-time-strict-locale-decimal", "eclipse-temurin:21-jdk-noble"],
  ["rust", "11-rust-cross-platform/basics/04-traits-generics.md", "rust-trait-generic-dyn-dispatch", "rust:1-slim-bookworm"],
];
const fence = /<!-- body-runtime-case: (\{[^\n]+\}) -->\n```(php|java|rust)\n(.*?)\n```/gs;

function dockerCommand(language, image) {
  if (language === "php") return ["run", "--rm", "-i", image, "php"];
  if (language === "java") return ["run", "--rm", "-i", image, "sh", "-c", "cat > /tmp/Main.java && javac --release 21 -encoding UTF-8 /tmp/Main.java && java -cp /tmp Main"];
  return ["run", "--rm", "-i", image, "sh", "-c", "cat > /tmp/main.rs && rustc --edition 2024 /tmp/main.rs -o /tmp/main && /tmp/main"];
}

const results = [];
for (const [language, relative, id, image] of cases) {
  const raw = readFileSync(join(root, relative));
  const text = raw.toString("utf8").replace(/\r\n/g, "\n");
  const found = [...text.matchAll(fence)].filter((match) => match[2] === language && JSON.parse(match[1]).id === id);
  if (found.length !== 1) throw new Error(`${relative}: expected one named complete body case ${id}, found ${found.length}`);
  const metadata = JSON.parse(found[0][1]);
  const source = found[0][3] + "\n";
  const args = dockerCommand(language, image);
  const run = spawnSync("docker", args, { input: source, encoding: "utf8", timeout: 90000 });
  if (run.error) throw run.error;
  const status = run.status === 0 && run.stdout === metadata.stdout && run.stderr === "" ? "passed" : "failed";
  results.push({ id, document: relative, document_sha256: createHash("sha256").update(raw).digest("hex"), extraction: "complete named body fence, passed unchanged to stdin", toolchain: { container_image: image, language }, command: ["docker", ...args], exit_code: run.status, stdout: run.stdout, stderr: run.stderr, expected_stdout: metadata.stdout, status });
  console.log(`${status === "passed" ? "PASS" : "FAIL"} ${id}`);
}

const report = { schema_version: 1, purpose: "Runtime evidence for three named complete P1 PHP/Java/Rust Markdown body programs.", scope: "Each result is one complete fenced program extracted by its unique body-runtime-case id. Partial fences, prose, external services, cross-process contention, performance, and whole-document claims are outside this evidence.", results, summary: { passed: results.filter((item) => item.status === "passed").length, failed: results.filter((item) => item.status === "failed").length } };
mkdirSync(reports, { recursive: true });
writeFileSync(join(reports, "php-java-rust-fourteenth-body-validation.json"), JSON.stringify(report, null, 2) + "\n", "utf8");
const table = results.map((item) => `| \`${item.document}\` | \`${item.id}\` | \`${item.toolchain.container_image}\` | \`${item.status}\` |`);
writeFileSync(join(reports, "php-java-rust-fourteenth-body-validation.md"), ["# PHP / Java / Rust 第十四轮正文提取验证", "", report.scope, "", "| 文档 | 具名正文程序 | 容器工具链 | 状态 |", "|---|---|---|---|", ...table, "", `结果：${report.summary.passed}/${results.length} 通过。JSON 报告保留文档哈希、完整命令、退出码与 stdout/stderr。`, ""].join("\n"), "utf8");
process.exitCode = report.summary.failed === 0 ? 0 : 1;
