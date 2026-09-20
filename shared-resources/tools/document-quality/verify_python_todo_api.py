"""Run the complete in-memory FastAPI TODO project embedded in its tutorial.

The verifier writes the four named source blocks to a temporary directory and
runs the page's pytest suite in a pinned Python container.  It deliberately
does not start uvicorn or claim database, multi-worker, Redis, or deployment
coverage.
"""
import hashlib
import json
import re
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DOCUMENT = ROOT / "10-python-discovery/projects/01-todo-api.md"
REPORT = Path(__file__).resolve().parent / "reports/python-todo-api-validation.json"
IMAGES = ("python:3.12-alpine", "python:3.14-alpine")
BLOCKS = {
    "schemas.py": "## 3. 数据模型：schemas.py",
    "store.py": "## 4. 存储层：store.py",
    "main.py": "## 5. 路由层：main.py",
    "tests/test_api.py": "## 6. 测试：tests/test_api.py",
}


def code_after_heading(text, heading):
    start = text.index(heading)
    match = re.search(r"```python\n(.*?)\n```", text[start:], re.DOTALL)
    if not match:
        raise RuntimeError(f"Python fence not found after {heading!r}")
    return match.group(1) + "\n"


def main():
    text = DOCUMENT.read_text(encoding="utf-8")
    source = {name: code_after_heading(text, heading) for name, heading in BLOCKS.items()}
    with tempfile.TemporaryDirectory(prefix="dev-quest-python-todo-") as temporary:
        project = Path(temporary)
        for name, code in source.items():
            target = project / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(code, encoding="utf-8")
        results = []
        for image in IMAGES:
            command = [
                "docker", "run", "--rm", "--network", "bridge",
                "-v", f"{project.resolve()}:/work:ro", "-w", "/work",
                image, "sh", "-lc",
                "pip install --no-cache-dir fastapi==0.141.1 pydantic==2.13.5 pytest==9.1.1 httpx==0.28.1 && python -m pytest -q",
            ]
            result = subprocess.run(command, text=True, capture_output=True, check=False)
            results.append({"image": image, "command": command, "stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode})
    passed = all(row["returncode"] == 0 and re.search(r"12 passed", row["stdout"]) for row in results)
    report = {
        "status": "PASS" if passed else "FAIL",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "The four complete FastAPI in-memory TODO source blocks and their 12 pytest cases on Python 3.12 and 3.14; excludes uvicorn interaction, databases, multi-worker storage, Redis, authentication, and deployment.",
        "document": "10-python-discovery/projects/01-todo-api.md",
        "document_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "files": {name: hashlib.sha256(code.encode()).hexdigest() for name, code in source.items()},
        "results": results,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "report": str(REPORT), "images": [row["image"] for row in results]}, ensure_ascii=False))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
