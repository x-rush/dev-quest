#!/usr/bin/env python3
"""Run only explicitly selected complete examples added in the full-library pass."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
P = '10-python-discovery/reference/'
CASES = [
    ('language-concepts/03-data-structures.md', "['read', 'test']\n['read', 'test', 'review']\ncontains an unhashable list\n", []),
    ('language-concepts/07-generators-iterators.md', 'created\nstarted\n10\n[20]\n[]\n', []),
    ('language-concepts/08-context-managers.md', 'open\nresource\nclose\nhandled\n', []),
    ('language-concepts/10-exceptions-system.md', 'ConfigError\nValueError\n', []),
    ('language-concepts/12-string-formatting.md', "0.33\nTrue\n{name} = 'Ada'\n", []),
    ('language-concepts/04-oop-protocols.md', "2 True\n['intro', 'outro']\n['intro']\n", []),
    ('language-concepts/05-typing-annotations.md', '6\n33\nrejected\n', []),
    ('language-concepts/09-asyncio-concurrency.md', "group failed\n['written']\n", []),
    ('language-concepts/13-dataclasses.md', "['python']\n[]\nnot hashable\n", []),
    ('language-concepts/14-comprehensions.md', "{'py': 2, 'go': 2, 'rust': 4}\n{2: 'go', 4: 'rust'}\n{2: ['py', 'go'], 4: ['rust']}\n", []),
    ('language-concepts/17-functions-parameters.md', "['a']\n['b']\nTrue\n", []),
    ('library-guides/04-os-sys.md', "os-sys-environment: argv=['hello']; cwd=True; executable=True\n", ['hello']),
    ('library-guides/05-enum-module.md', 'True\nTrue\ninvalid state\n', []),
    ('library-guides/06-functools-subprocess.md', 'a b; c\n0\n', []),
]

def blocks(text):
    return re.findall(r'```python\s*\n(.*?)\n```', text, re.S)

def added(path):
    return (ROOT / (P + path)).read_text(encoding='utf8').split('<!-- full-library-explanation -->', 1)[1]

def run(command, work):
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    result = subprocess.run(command, cwd=work, capture_output=True, text=True,
                            encoding='utf8', env=env, timeout=30)
    if result.returncode:
        raise RuntimeError({'command': command, 'stderr': result.stderr, 'stdout': result.stdout})
    return result.stdout.replace('\r\n', '\n')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--python', default=sys.executable)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    if Path(args.python).is_file():
        args.python = str(Path(args.python).resolve())
    results = []
    with tempfile.TemporaryDirectory(prefix='dev-quest-reference-') as temporary:
        work = Path(temporary)
        for index, (path, expected, arguments) in enumerate(CASES):
            script = work / f'example_{index}.py'
            script.write_text(blocks(added(path))[0], encoding='utf8')
            output = run([args.python, str(script), *arguments], work)
            if output != expected:
                raise AssertionError({'source': path, 'actual': output, 'expected': expected})
            results.append({'source': P + path, 'status': 'PASS', 'output': output})

        path = 'language-concepts/11-modules-imports.md'
        helper, main_script = blocks(added(path))[:2]
        (work / 'helper.py').write_text(helper, encoding='utf8')
        (work / 'main.py').write_text(main_script, encoding='utf8')
        output = run([args.python, 'main.py'], work)
        assert output == 'helper loaded\n7\n', output
        results.append({'source': P + path, 'status': 'PASS', 'output': output})

        path = 'language-concepts/15-closures-and-scope.md'
        text = (ROOT / (P + path)).read_text(encoding='utf8')
        definition = [b for b in blocks(text.split('<!-- full-library-explanation -->')[0]) if 'def make_counter(start:' in b][-1]
        (work / 'counter.py').write_text(definition + '\n' + blocks(added(path))[0], encoding='utf8')
        output = run([args.python, 'counter.py'], work)
        assert output == '1 2 11 3\n', output
        results.append({'source': P + path, 'status': 'PASS', 'output': output})

        for path, count in [('library-guides/03-pytest-testing.md', 6), ('framework-essentials/01-fastapi-essentials.md', 2)]:
            (work / 'test_example.py').write_text(blocks(added(path))[0], encoding='utf8')
            output = run([args.python, '-m', 'pytest', 'test_example.py', '-q', '-p', 'no:cacheprovider'], work)
            assert f'{count} passed' in output, output
            results.append({'source': P + path, 'status': 'PASS', 'tests': count, 'output': output})
        versions = run([args.python, '-c', 'import sys,json,importlib.metadata as m;print(json.dumps({"python":sys.version.split()[0],**{p:m.version(p) for p in ["pytest","fastapi","httpx","pydantic"]}}))'], work)
    report = {'environment': json.loads(versions), 'results': results,
              'scope': 'Only the listed complete added examples. Historical snippets, Python 3.14-only syntax, databases, Docker and CI are not executed by this tool.'}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps({'examples': len(results), 'pytest_cases': 8, 'status': 'PASS'}, ensure_ascii=False))

if __name__ == '__main__':
    main()
