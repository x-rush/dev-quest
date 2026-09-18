"""Exercise the built parser; rejects a runner that accepts all input or emits nothing."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile


def main():
    binary = str(Path(sys.argv[1]).resolve())
    cases = [
        ("package main\nfunc main() {}\n", True, 0),
        ("type User struct { Name string }\n", True, 1),
        ("answer := 42\n_ = answer\n", True, 2),
        ("package main\nfunc main( {\n", False, 0),
    ]
    with tempfile.TemporaryDirectory(prefix="parsego-test-") as folder:
        root = Path(folder)
        paths = []
        for index, (source, _, _) in enumerate(cases):
            path = root / f"case-{index}.go"
            path.write_text(source, encoding="utf-8")
            paths.append(str(path))
        paths.append(str(root / "missing.go"))
        filelist = root / "files.txt"
        filelist.write_text("\n".join(paths) + "\n", encoding="utf-8")
        run = subprocess.run(
            [binary, str(filelist)], capture_output=True, text=True,
            encoding="utf-8", check=True, timeout=30,
        )
        results = [json.loads(line) for line in run.stdout.splitlines()]
        assert len(results) == len(paths), results
        for result, path, (_, ok, level) in zip(results, paths, cases):
            assert result["file"] == path, result
            assert result["ok"] is ok and result["level"] == level, result
            if not ok:
                assert result.get("err"), result
        assert results[-1]["file"] == paths[-1], results[-1]
        assert results[-1]["ok"] is False and results[-1]["level"] == -1, results[-1]
        assert results[-1]["err"].startswith("read: "), results[-1]
    print("parsego: 5 regression cases passed")


if __name__ == "__main__":
    main()
