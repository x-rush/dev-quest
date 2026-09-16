#!/usr/bin/env python3
"""基线版本漂移检查：解析各模块 README「技术基线」区块，批量比对 registry 最新版

解析策略：
  1. 提取每个模块 README 中「技术基线」区块的表格行：名称 + 版本 token + 行内来源 URL
  2. 包身份解析优先用行内 URL（pkg.go.dev → go proxy、github releases → GitHub API、
     npmjs → npm view、pypi → PyPI JSON API、crates.io → crates API、go.dev/dl → 官方 JSON）
  3. 无 URL 行按名称回退表（FALLBACK）解析
  4. 版本比较：latest 与 pinned 前缀比对 → OK / DRIFT_MAJOR / DRIFT_MINOR / UNKNOWN / NOTE

用法：python3 baseline_check.py [--json OUT]   # 报告打印 stdout 并写 /tmp
"""
import argparse
import json
import os
import re
import subprocess
import urllib.request
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

SEMVER = re.compile(r"v?(\d+)(?:\.(\d+|x))?(?:\.(\d+))?")
URL_PATTERNS = [
    (re.compile(r"pkg\.go\.dev/([\w./~\-]+)"), "gomod"),
    (re.compile(r"github\.com/([\w.\-]+)/([\w.\-]+)"), "github"),
    (re.compile(r"npmjs\.com/package/(@?[\w./\-]+)"), "npm"),
    (re.compile(r"pypi\.org/project/([\w.\-]+)"), "pypi"),
    (re.compile(r"crates\.io/crates/([\w.\-]+)"), "crates"),
    (re.compile(r"go\.dev/(dl|blog)"), "golang"),
]
FALLBACK = {
    "next.js": ("npm", "next"), "react": ("npm", "react"), "typescript": ("npm", "typescript"),
    "tanstack query": ("npm", "@tanstack/react-query"), "tanstack router": ("npm", "@tanstack/react-router"),
    "tanstack table": ("npm", "@tanstack/react-table"), "tanstack start": ("npm", "@tanstack/react-start"),
    "vite": ("npm", "vite"), "tailwind css": ("npm", "tailwindcss"), "turborepo": ("npm", "turbo"),
    "react native": ("npm", "react-native"), "expo": ("npm", "expo"), "zustand": ("npm", "zustand"),
    "express": ("npm", "express"), "nestjs": ("npm", "@nestjs/core"), "fastify": ("npm", "fastify"),
    "go": ("golang", None), "kotlin": ("github", "JetBrains/kotlin"),
    "spring boot": ("github", "spring-projects/spring-boot"),
    "spring framework": ("github", "spring-projects/spring-framework"),
    "spring security": ("github", "spring-projects/spring-security"),
    "hibernate / jpa": ("github", "hibernate/hibernate-orm"),
    "jackson": ("github", "FasterXML/jackson-core"),
    "junit / testcontainers": ("github", "junit-team/junit5"),
    "maven / gradle": ("github", "apache/maven"),
    "graalvm": ("github", "oracle/graal"),
    "java": ("github", "openjdk/jdk"), "php": ("github", "php/php-src"),
    "laravel": ("github", "laravel/laravel"), "composer": ("github", "composer/composer"),
    "phpunit": ("github", "sebastianbergmann/phpunit"), "pest": ("github", "pestphp/pest"),
    "swift": ("github", "swiftlang/swift"), "python": ("github", "python/cpython"),
    "django": ("github", "django/django"), "fastapi": ("github", "fastapi/fastapi"),
    "pytest": ("pypi", "pytest"), "gradle": ("github", "gradle/gradle"),
    "expo sdk": ("npm", "expo"), "expo router": ("npm", "expo-router"),
    "reanimated": ("npm", "react-native-reanimated"),
    "jetpack compose bom": ("googlemaven", "androidx/compose/compose-bom"),
    "material 3": ("googlemaven", "androidx/compose/material3/material3"),
    "material3": ("googlemaven", "androidx/compose/material3/material3"),
    "agp": ("googlemaven", "com/android/tools/build/gradle"),
    # KSP 版本号为 <kotlin>-<ksp> 拼接格式，通用比较器无法解析，人工核实
    "ksp": ("human", None),
    # 版本号无独立语义或依赖厂商发布策略：固定人工核实
    "graalvm": ("human", None),
    "java": ("human", None),
    # 平台闭源工具链：无通用 registry，固定人工核实
    "xcode": ("human", None), "ios sdk": ("human", None),
    "android studio": ("human", None), "targetsdk": ("human", None),
    "hermes": ("human", None),
}
UA = {"User-Agent": "dev-quest-baseline-check/1.0"}


def http_json(url, timeout=25):
    headers = dict(UA)
    tok = os.environ.get("GITHUB_TOKEN")
    if tok and "api.github.com" in url:
        headers["Authorization"] = f"Bearer {tok}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def sh(cmd, timeout=40):
    """cmd 为参数列表（不经 shell），ident 来源于仓库内 README 表格行"""
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.stdout.strip() if p.returncode == 0 else None
    except Exception:
        return None


def strip_v(tag):
    # 兼容 swift-6.4.0-RELEASE / php-8.5.10 / jdk-25 等带前缀 tag：任意位置提取版本
    m = re.search(r"(\d+(?:\.\d+)+)", tag)
    return m.group(1) if m else tag.lstrip("vV")


def norm(v):
    m = SEMVER.match(v.strip().lstrip("vV"))
    if not m:
        return None
    maj = int(m.group(1))
    mid = m.group(2)
    return (maj,) if mid in (None, "x") else (maj, int(mid))


def latest_for(kind, ident):
    if kind == "gomod":
        out = sh(["go", "list", "-m", "-versions", ident])
        if out:
            return strip_v(out.split()[-1])
    elif kind == "github":
        out = sh(["gh", "api", f"repos/{ident}/releases/latest", "--jq", ".tag_name"])
        if out:
            return strip_v(out)
        try:
            return strip_v(http_json(f"https://api.github.com/repos/{ident}/releases/latest")["tag_name"])
        except Exception:
            pass
        # releases/latest 404（如 openjdk/jdk 只打 tag）→ 退 tags 首页取首个版本 tag
        try:
            tags = http_json(f"https://api.github.com/repos/{ident}/tags?per_page=15")
            for t in tags:
                if re.search(r"\d", t["name"]):
                    return strip_v(t["name"])
        except Exception:
            pass
        return None
    elif kind == "googlemaven":
        # Google Maven metadata XML；部分组件 <release>/<latest> 含 alpha，从版本列表取最新稳定版
        try:
            req = urllib.request.Request(f"https://maven.google.com/{ident}/maven-metadata.xml", headers=UA)
            xml = urllib.request.urlopen(req, timeout=25).read().decode()
            vers = re.findall(r"<version>([^<]+)</version>", xml)
            stable = [v for v in vers if not re.search(r"-(alpha|beta|rc|dev)", v)]
            if stable:
                return stable[-1]
            m = re.search(r"<release>([^<]+)</release>", xml)
            return m.group(1) if m else None
        except Exception:
            return None
    elif kind == "npm":
        out = sh(["npm", "view", ident, "version"], timeout=30)
        return out.splitlines()[-1] if out else None
    elif kind == "pypi":
        try:
            return http_json(f"https://pypi.org/pypi/{ident}/json")["info"]["version"]
        except Exception:
            return None
    elif kind == "crates":
        try:
            c = http_json(f"https://crates.io/api/v1/crates/{ident}")["crate"]
            return c.get("max_stable_version") or c.get("newest_version")
        except Exception:
            return None
    elif kind == "golang":
        try:
            return http_json("https://go.dev/dl/?mode=json")[0]["version"].lstrip("go")
        except Exception:
            return None
    return None


def parse_module(readme):
    lines = open(readme, encoding="utf-8").read().splitlines()
    rows, in_sec = [], False
    for ln in lines:
        if re.match(r"^##\s+.*技术基线", ln):
            in_sec = True
            continue
        if in_sec and ln.startswith("## "):
            break
        if in_sec and ln.startswith("|") and not re.match(r"^\|[\s:\-|]+\|$", ln):
            cells = [c.strip() for c in ln.strip("|").split("|")]
            if len(cells) >= 2 and cells[0] not in ("技术", "Technology"):
                rows.append(cells)
    return rows


def classify(pinned, latest):
    if latest is None:
        return "UNKNOWN"
    p, l = norm(pinned), norm(latest)
    if p is None or l is None:
        return "UNKNOWN"
    if l[: len(p)] == p:
        return "OK"
    if l[0] > p[0]:
        return "DRIFT_MAJOR"
    return "DRIFT_MINOR"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", help="同时写 JSON 到该路径")
    args = ap.parse_args()
    modules = sorted(d for d in os.listdir(REPO)
                     if re.match(r"^\d{2}-", d) and os.path.isdir(os.path.join(REPO, d)))
    results = []
    for d in modules:
        readme = os.path.join(REPO, d, "README.md")
        for cells in parse_module(readme):
            name = cells[0]
            vm = SEMVER.search(cells[1])
            if not vm:
                results.append(dict(module=d, name=name, pinned=cells[1], latest="", status="NOTE"))
                continue
            pinned = vm.group(0)
            kind = ident = None
            row = "|".join(cells)
            for pat, k in URL_PATTERNS:
                m = pat.search(row)
                if m:
                    kind = k
                    if k == "gomod":
                        ident = m.group(1).rstrip("/")
                    elif k == "github":
                        ident = f"{m.group(1)}/{m.group(2)}"
                    elif k == "npm":
                        ident = m.group(1).rstrip("/")
                        if not ident.startswith("@"):
                            ident = ident.split("/")[0]
                    else:
                        ident = None
                    break
            if kind is None:
                fb = FALLBACK.get(name.lower().strip("*_ "))
                if fb:
                    kind, ident = fb
            if kind == "human":
                results.append(dict(module=d, name=name, pinned=pinned, latest="",
                                    status="NOTE"))
                continue
            latest = latest_for(kind, ident) if kind else None
            results.append(dict(module=d, name=name, pinned=pinned, latest=latest or "",
                                status=classify(pinned, latest) if latest else "UNKNOWN"))
    order = {"DRIFT_MAJOR": 0, "DRIFT_MINOR": 1, "UNKNOWN": 2, "OK": 3, "NOTE": 4}
    results.sort(key=lambda r: (order[r["status"]], r["module"]))
    icons = {"DRIFT_MAJOR": "✗", "DRIFT_MINOR": "⚠", "UNKNOWN": "?", "OK": "✓", "NOTE": "-"}
    print(f"\n基线漂移检查 {date.today()}（{len(modules)} 模块）\n")
    for r in results:
        print(f"{icons[r['status']]} [{r['status']:<11}] {r['module']:<22} {r['name']:<28} pinned={r['pinned']:<12} latest={r['latest']}")
    stat = {}
    for r in results:
        stat[r["status"]] = stat.get(r["status"], 0) + 1
    print("\n统计:", json.dumps(stat, ensure_ascii=False))
    out = f"/tmp/baseline-check-{date.today()}.md"
    with open(out, "w", encoding="utf-8") as f:
        f.write(f"# 基线漂移检查 {date.today()}\n\n| 状态 | 模块 | 技术 | 基线 | registry 最新 |\n|---|---|---|---|---|\n")
        for r in results:
            f.write(f"| {r['status']} | {r['module']} | {r['name']} | {r['pinned']} | {r['latest']} |\n")
    print("报告:", out)
    if args.json:
        json.dump(results, open(args.json, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
