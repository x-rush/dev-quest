#!/usr/bin/env node
/** Extract and run only the three named sixteenth-round Markdown body programs unchanged. */
import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, "..", "..", "..");
const reports = join(here, "reports");
const marker = "sixteenth-body-runtime-case";
const cases = [
  ["php", "07-php-mastery/reference/language-concepts/03-types-oop-modern.md", "php-readonly-slot-and-object-state", "php:8.5-cli-alpine"],
  ["java", "08-java-revisited/reference/language-concepts/04-concurrency-api.md", "java-concurrent-map-per-key-initialization", "eclipse-temurin:21-jdk-noble"],
  ["rust", "11-rust-cross-platform/reference/language-concepts/03-const-generics.md", "rust-const-generic-frame-and-slice", "rust:1-slim-bookworm"],
];
const fence = new RegExp(`<!-- ${marker}: (\\{[^\\n]+\\}) -->\\n\\x60\\x60\\x60(php|java|rust)\\n(.*?)\\n\\x60\\x60\\x60`, "gs");

function dockerArgs(language, image) {
  if (language === "php") return ["run", "--rm", "-i", image, "php"];
  if (language === "java") return ["run", "--rm", "-i", image, "sh", "-c", "cat > /tmp/Main.java && javac --release 21 -encoding UTF-8 /tmp/Main.java && java -cp /tmp Main"];
  return ["run", "--rm", "-i", image, "sh", "-c", "cat > /tmp/main.rs && rustc --edition 2024 /tmp/main.rs -o /tmp/main && /tmp/main"];
}

const results = [];
for (const [language, document, id, image] of cases) {
  const raw = readFileSync(join(root, document));
  const normalized = raw.toString("utf8").replace(/\r\n/g, "\n");
  const matches = [...normalized.matchAll(fence)].filter((item) => item[2] === language && JSON.parse(item[1]).id === id);
  if (matches.length !== 1) throw new Error(`${document}: expected exactly one ${id} fence, found ${matches.length}`);
  const metadata = JSON.parse(matches[0][1]);
  const source = `${matches[0][3]}\n`;
  const args = dockerArgs(language, image);
  const run = spawnSync("docker", args, { input: source, encoding: "utf8", timeout: 90000 });
  if (run.error) throw run.error;
  const status = run.status === 0 && run.stdout === metadata.stdout && run.stderr === "" ? "passed" : "failed";
  results.push({
    id, document, document_sha256: createHash("sha256").update(raw).digest("hex"),
    extraction: "complete named Markdown fence passed unchanged to stdin", toolchain: { language, container_image: image },
    command: ["docker", ...args], exit_code: run.status, stdout: run.stdout, stderr: run.stderr,
    expected_stdout: metadata.stdout, status,
  });
  console.log(`${status === "passed" ? "PASS" : "FAIL"} ${id}`);
}

const report = {
  schema_version: 1,
  purpose: "Runtime evidence for the three named sixteenth-round P1 PHP/Java/Rust core or standard-library Markdown body programs.",
  scope: "Only the three complete fences named by sixteenth-body-runtime-case are extracted and executed. Partial snippets, all other document content, framework integration, stress testing, performance, and whole-document claims are outside this report.",
  results,
  summary: { passed: results.filter((item) => item.status === "passed").length, failed: results.filter((item) => item.status === "failed").length },
};
mkdirSync(reports, { recursive: true });
writeFileSync(join(reports, "php-java-rust-sixteenth-body-validation.json"), `${JSON.stringify(report, null, 2)}\n`, "utf8");
const rows = results.map((item) => `| \`${item.document}\` | \`${item.id}\` | \`${item.toolchain.container_image}\` | \`${item.status}\` |`);
writeFileSync(join(reports, "php-java-rust-sixteenth-body-validation.md"), [
  "# PHP / Java / Rust 第十六轮正文提取验证", "", report.scope, "",
  "| 文档 | 具名正文程序 | 容器工具链 | 状态 |", "|---|---|---|---|", ...rows, "",
  `结果：${report.summary.passed}/${results.length} 通过。JSON 保留文档哈希、原样提取方式、完整命令、退出码和 stdout/stderr。`, "",
].join("\n"), "utf8");
process.exitCode = report.summary.failed === 0 ? 0 : 1;
