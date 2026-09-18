#!/usr/bin/env python3
"""Execute a reviewed allowlist of self-contained Go documentation examples."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[3]
PREFIX = '01-go-backend/reference/'
PROGRAMS = {
    'language-concepts/04-go-data-types.md': (True, ['[7 2] [9 2] [7 2]']),
    'library-guides/04-encoding-json.md': (False, ['bob 20', 'json.Number']),
    'library-guides/05-context.md': (False, ['context deadline exceeded', '两个子 ctx 都已取消']),
    'library-guides/06-sync.md': (False, ['100\n3']),
    'library-guides/07-database-sql.md': (False, ['a@b.c\ntrue']),
    'library-guides/08-time.md': (False, ['2026-09-14T08:05:03Z', 'tick 完成 3', '超时']),
    'library-guides/09-errors.md': (False, ['load user 42: record not found', 'email']),
    'library-guides/10-io-bufio.md': (False, ['true 102400', 'copiedbuffered']),
    'library-guides/11-os.md': (False, ['hello os true', 'true true']),
    'library-guides/13-slices-maps.md': (False, ['[a b c]', '[a b]']),
    'library-guides/14-strconv.md': (False, ['id=9001,ok=true']),
    'library-guides/15-log-slog.md': (False, ['"service":"api"', '"http":{"ms":950}']),
    'library-guides/16-flag.md': (False, ['9000 true 3 a,b']),
}

def blocks(path):
    return re.findall(r'```go\s*\n(.*?)\n```', (ROOT / (PREFIX + path)).read_text(encoding='utf8'), re.S)

def execute(command, cwd):
    p = subprocess.run(command, cwd=cwd, capture_output=True, text=True, encoding='utf8', timeout=120)
    if p.returncode:
        raise RuntimeError(f'{command}\n{p.stdout}\n{p.stderr}')
    return (p.stdout + p.stderr).replace('\r\n', '\n')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--go', required=True, type=Path)
    parser.add_argument('--report', required=True, type=Path)
    parser.add_argument('--skip', action='append', default=[], help='Explicitly skip a path blocked by host execution policy')
    args = parser.parse_args()
    go = str(args.go.resolve())
    results = []
    with tempfile.TemporaryDirectory(prefix='dev-quest-go-') as folder:
        root = Path(folder)
        for index, (path, (added_only, expected)) in enumerate(PROGRAMS.items()):
            if path in args.skip:
                results.append({'path': PREFIX + path, 'status': 'blocked', 'reason': 'Skipped after Windows Application Control rejection; no bypass attempted'})
                continue
            source = (ROOT / (PREFIX + path)).read_text(encoding='utf8')
            if added_only:
                source = source.split('<!-- full-library-explanation -->', 1)[1]
            code = next(b for b in re.findall(r'```go\s*\n(.*?)\n```', source, re.S) if b.startswith('package main'))
            cwd = root / str(index)
            cwd.mkdir()
            (cwd / 'main.go').write_text(code, encoding='utf8')
            command = [go, 'run', 'main.go']
            if path.endswith('16-flag.md'):
                command += ['-port=9000', '-verbose', '-tags', 'a, b']
            try:
                output = execute(command, cwd)
            except RuntimeError as error:
                if 'Application Control policy has blocked' not in str(error):
                    raise
                results.append({'path': PREFIX + path, 'status': 'blocked', 'reason': 'Windows Application Control blocked execution; no bypass attempted'})
                print('BLOCKED', path, flush=True)
                continue
            for fragment in expected:
                assert fragment in output, (path, fragment, output)
            results.append({'path': PREFIX + path, 'status': 'passed', 'kind': 'selected complete program', 'code_sha256': hashlib.sha256(code.encode()).hexdigest()})
            print('PASS', path, flush=True)
        path = 'library-guides/12-testing.md'
        code = next(b for b in blocks(path) if 'package mathx' in b)
        cwd = root / 'testing'
        cwd.mkdir()
        (cwd / 'go.mod').write_text('module example/mathx\n\ngo 1.27\n', encoding='utf8')
        (cwd / 'mathx_test.go').write_text(code, encoding='utf8')
        try:
            execute([go, 'test', '-v', './...'], cwd)
            results.append({'path': PREFIX + path, 'status': 'passed', 'kind': 'table tests and fuzz seeds; no duration fuzz campaign'})
        except RuntimeError as error:
            if 'Application Control policy has blocked' not in str(error):
                raise
            results.append({'path': PREFIX + path, 'status': 'blocked', 'reason': 'Windows Application Control blocked test executable'})
        path = 'library-guides/03-net-http.md'
        code = next(b for b in blocks(path) if b.startswith('package main'))
        cwd = root / 'http'
        cwd.mkdir()
        (cwd / 'go.mod').write_text('module example/http\n\ngo 1.27\n', encoding='utf8')
        (cwd / 'main.go').write_text(code, encoding='utf8')
        (cwd / 'main_test.go').write_text('''package main
import ("testing"; "net/http/httptest"; "encoding/json")
func TestRoutes(t *testing.T) {
 for _, tc := range []struct{ method, path string; status int }{
  {"GET", "/users/42", 200}, {"HEAD", "/users/42", 200},
  {"POST", "/users/42", 405}, {"GET", "/missing", 404},
 } {
  r := httptest.NewRequest(tc.method, tc.path, nil)
  w := httptest.NewRecorder()
  newMux().ServeHTTP(w, r)
  if w.Code != tc.status { t.Fatalf("%s %s: got %d want %d", tc.method, tc.path, w.Code, tc.status) }
  if tc.method == "GET" && tc.status == 200 {
   var u User
   if err := json.Unmarshal(w.Body.Bytes(), &u); err != nil { t.Fatal(err) }
   if u.Name != "用户42" { t.Fatalf("unexpected user: %#v", u) }
  }
 }
}
''', encoding='utf8')
        if path in args.skip:
            results.append({'path': PREFIX + path, 'status': 'blocked', 'reason': 'Skipped after host policy rejection'})
        else:
            try:
                execute([go, 'test', '-v', './...'], cwd)
                results.append({'path': PREFIX + path, 'status': 'passed', 'kind': 'server routing and decoded response; client fragment not run'})
            except RuntimeError as error:
                if 'Application Control policy has blocked' not in str(error):
                    raise
                results.append({'path': PREFIX + path, 'status': 'blocked', 'reason': 'Windows Application Control blocked test executable'})
        version = execute([go, 'version'], root).strip()
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps({'runtime': version, 'scope': 'Allowlisted complete examples only; no external databases, race run, deployment or whole-document compilation', 'results': results}, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
    print(f'{sum(r["status"] == "passed" for r in results)} passed; {sum(r["status"] == "blocked" for r in results)} blocked')

if __name__ == '__main__':
    main()
